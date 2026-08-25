import asyncio
import logging
from datetime import timedelta

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.utils import calc_result, get_now_utc
from models.match import Match
from models.prediction import Prediction, PredictionSource
from services.llm_client import call_llm
from services.prompt_builder import build_prediction_prompt

logger = logging.getLogger(__name__)


async def generate_ai_prediction(db: AsyncSession, match: Match, model_name: str | None = None) -> Prediction:
    used_model = model_name or settings.llm_default_model
    match_id = match.id

    exists_stmt = select(Prediction.id).where(
        Prediction.match_id == match_id,
        Prediction.source == PredictionSource.LLM,
        Prediction.model_name == used_model,
    )
    if (await db.execute(exists_stmt)).scalar_one_or_none():
        raise ValueError(f"LLM prediction for model '{used_model}' already exists for match {match_id}")

    prompt = build_prediction_prompt(match)
    response = await call_llm(prompt, model_name)

    prediction = Prediction(
        match_id=match_id,
        source=PredictionSource.LLM,
        model_name=used_model,
        score_home=response["score_home"],
        score_away=response["score_away"],
        predicted_result=calc_result(response["score_home"], response["score_away"]),
        confidence=response.get("confidence"),
    )
    db.add(prediction)
    return prediction


async def generate_for_upcoming_matches(db: AsyncSession, model_name: str | None = None) -> list[Prediction]:
    now = get_now_utc()
    cutoff = now + timedelta(minutes=15)
    used_model = model_name or settings.llm_default_model

    prediction_exists_subq = (
        select(1)
        .where(
            Prediction.match_id == Match.id,
            Prediction.source == PredictionSource.LLM,
            Prediction.model_name == used_model,
        )
        .exists()
    )

    stmt = select(Match.id).where(
        Match.date >= now,
        Match.date <= cutoff,
        Match.completed == False,
        ~prediction_exists_subq,
    )
    result = await db.execute(stmt)
    match_ids = result.scalars().all()

    predictions = []
    for match_id in match_ids:
        res_match = await db.execute(select(Match).where(Match.id == match_id))
        match = res_match.scalar_one_or_none()
        if not match:
            continue

        match_event_id = match.event_id

        try:
            pred = await generate_ai_prediction(db, match, model_name)
            await db.commit()
            await db.refresh(pred)
            predictions.append(pred)

            await asyncio.sleep(5)

        except IntegrityError:
            await db.rollback()
            logger.info("Prediction for match %s by %s already inserted concurrently.", match_event_id, used_model)
        except Exception as e:
            await db.rollback()
            logger.warning("Failed to generate AI prediction for match %s: %s", match_event_id, e)

    return predictions
