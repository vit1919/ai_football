import logging
import asyncio
from datetime import timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from models.match import Match
from models.prediction import Prediction, PredictionSource
from app.utils import calc_result, get_now_utc
from app.core.config import settings
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
    exists_result = await db.execute(exists_stmt)
    if exists_result.scalar_one_or_none():
        raise ValueError(f"LLM prediction for model '{used_model}' already exists for this match")

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
    match.ai_predictions_generated = True
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise ValueError(f"LLM prediction for model '{used_model}' already exists for this match")
    except SQLAlchemyError:
        await db.rollback()
        raise
    await db.refresh(prediction)
    return prediction


async def generate_for_upcoming_matches(db: AsyncSession, model_name: str | None = None) -> list[Prediction]:
    now = get_now_utc()
    cutoff = now + timedelta(minutes=15)

    stmt = select(Match).where(
        Match.date >= now,
        Match.date <= cutoff,
        Match.completed == False,
        Match.ai_predictions_generated == False,
    )
    result = await db.execute(stmt)
    matches = result.scalars().all()

    predictions = []
    for match in matches:
        match_event_id = match.event_id

        try:
            pred = await generate_ai_prediction(db, match, model_name)
            predictions.append(pred)

            await asyncio.sleep(5)

        except Exception:
            await db.rollback()
            logger.warning("Failed to generate AI prediction for match %s", match_event_id, exc_info=True)

    return predictions