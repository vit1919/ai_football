from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from fastapi import HTTPException
from models.match import Match
from models.prediction import Prediction, PredictionSource
from models.user import User


async def get_match_comparison(db: AsyncSession, event_id: int, user: User | None) -> dict:
    stmt = (
        select(Match)
        .options(selectinload(Match.predictions))
        .where(Match.event_id == event_id)
    )
    result = await db.execute(stmt)
    match = result.scalars().one_or_none()

    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    if not match.completed:
        raise HTTPException(status_code=400, detail="Match not completed yet")

    user_prediction = None
    if user:
        user_prediction = next(
            (p for p in match.predictions if p.source == PredictionSource.USER and p.user_id == user.id),
            None
        )

    llm_prediction = None
    target_model = user_prediction.selected_model if (user_prediction and user_prediction.selected_model) else None

    if target_model:
        llm_prediction = next(
            (p for p in match.predictions if p.source == PredictionSource.LLM and p.model_name == target_model),
            None
        )
    else:
        llm_prediction = next(
            (p for p in match.predictions if p.source == PredictionSource.LLM),
            None
        )

    result_label = None
    if user_prediction and user_prediction.user_vs_llm_result:
        if user_prediction.user_vs_llm_result == "user_win":
            result_label = "user_won"
        elif user_prediction.user_vs_llm_result == "user_loss":
            result_label = "llm_won"
        elif user_prediction.user_vs_llm_result == "draw":
            result_label = "draw"

    return {
        "match": match,
        "user_prediction": user_prediction,
        "llm_prediction": llm_prediction,
        "result": result_label,
        "model_name": llm_prediction.model_name if llm_prediction else (target_model or "AI Model"),
        "actual_score": {
            "home": match.home_score,
            "away": match.away_score,
        } if match.home_score is not None else None,
    }