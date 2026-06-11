from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload
from models import Match
from app.utils import calculate_prediction_points

async def score_predictions(db: AsyncSession) -> dict:
    stmt = (
        select(Match)
        .options(selectinload(Match.predictions))
        .where(
            Match.completed == True,
            Match.predictions_scored == False
        )
    )
    result = await db.execute(stmt)
    matches_to_score = result.scalars().all()

    if not matches_to_score:
        return {
            "matches_scored": 0,
            "predictions_scored": 0
        }

    predictions_scored = 0
    for match in matches_to_score:

        for prediction in match.predictions:
            points = calculate_prediction_points(prediction, match)

            prediction.points_awarded = points
            prediction.is_scored = True
            predictions_scored += 1

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