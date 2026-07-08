from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload
from models import Match
from models.prediction import Prediction, PredictionSource
from app.utils import calculate_prediction_points
from app.utils import get_now_utc

async def score_predictions(db: AsyncSession) -> dict:
    stmt = (
        select(Match)
        .options(
            selectinload(Match.predictions).selectinload(Prediction.user)
        )
        .where(
            Match.completed == True,
            Match.predictions_scored == False
        )
    )
    result = await db.execute(stmt)
    matches_to_score = result.scalars().unique().all()

    if not matches_to_score:
        return {
            "matches_scored": 0,
            "predictions_scored": 0
        }

    predictions_scored = 0
    for match in matches_to_score:
        llm_points = 0
        user_points = 0
        has_user_prediction = False

        for prediction in match.predictions:
            points = calculate_prediction_points(prediction, match)

            prediction.points_awarded = points
            prediction.is_scored = True
            prediction.scored_at = get_now_utc()

            if prediction.source == PredictionSource.LLM:
                llm_points = points
            elif prediction.source == PredictionSource.USER and prediction.user:
                prediction.user.total_points += points
                user_points = points
                has_user_prediction = True

            predictions_scored += 1

        match.llm_points_awarded = llm_points
        if llm_points > 0 and has_user_prediction:
            if llm_points > user_points:
                match.llm_vs_user_result = "win"
            elif llm_points < user_points:
                match.llm_vs_user_result = "loss"
            else:
                match.llm_vs_user_result = "draw"

        match.predictions_scored = True

    try:
        await db.commit()
    except SQLAlchemyError:
        await db.rollback()
        raise

    return {
        "matches_scored": len(matches_to_score),
        "predictions_scored": predictions_scored,
    }