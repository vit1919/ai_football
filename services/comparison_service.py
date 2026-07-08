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
    llm_prediction = None

    for pred in match.predictions:
        if pred.source == PredictionSource.USER and user and pred.user_id == user.id:
            user_prediction = pred
        elif pred.source == PredictionSource.LLM and llm_prediction is None:
            llm_prediction = pred

    result_label = None
    if match.llm_vs_user_result == "win":
        result_label = "llm_won"
    elif match.llm_vs_user_result == "loss":
        result_label = "user_won"
    elif match.llm_vs_user_result == "draw":
        result_label = "draw"

    return {
        "match": match,
        "user_prediction": user_prediction,
        "llm_prediction": llm_prediction,
        "result": result_label,
        "actual_score": {
            "home": match.home_score,
            "away": match.away_score,
        } if match.home_score is not None else None,
    }
