from datetime import timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.match import Match
from models.prediction import Prediction, PredictionSource
from app.utils import calc_result, get_now_utc
from services.llm_client import call_llm
from services.prompt_builder import build_prediction_prompt


async def generate_ai_prediction(db: AsyncSession, match: Match, model_name: str | None = None) -> Prediction:
    prompt = build_prediction_prompt(match)
    response = await call_llm(prompt, model_name)

    used_model = model_name or "gemini-2.0-flash"

    prediction = Prediction(
        match_id=match.id,
        source=PredictionSource.LLM,
        model_name=used_model,
        score_home=response["score_home"],
        score_away=response["score_away"],
        predicted_result=calc_result(response["score_home"], response["score_away"]),
        confidence=response.get("confidence"),
    )

    db.add(prediction)
    match.ai_predictions_generated = True
    await db.commit()
    await db.refresh(prediction)
    return prediction


async def generate_for_upcoming_matches(db: AsyncSession, model_name: str | None = None) -> list[Prediction]:
    now = get_now_utc()
    cutoff = now + timedelta(minutes=15)

    stmt = select(Match).where(
        Match.date <= cutoff,
        Match.completed == False,
        Match.ai_predictions_generated == False,
    )
    result = await db.execute(stmt)
    matches = result.scalars().all()

    predictions = []
    for match in matches:
        try:
            pred = await generate_ai_prediction(db, match, model_name)
            predictions.append(pred)
        except Exception:
            await db.rollback()

    return predictions
