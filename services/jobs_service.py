from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.utils import calculate_prediction_points, get_now_utc
from models import Match
from models.prediction import Prediction, PredictionSource


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
        return {"matches_scored": 0, "predictions_scored": 0}

    predictions_scored = 0
    for match in matches_to_score:
        llm_predictions = []

        for prediction in match.predictions:
            points = calculate_prediction_points(prediction, match)
            prediction.points_awarded = points
            prediction.is_scored = True
            prediction.scored_at = get_now_utc()

            if prediction.source == PredictionSource.USER and prediction.user:
                prediction.user.total_points += points
            elif prediction.source == PredictionSource.LLM:
                llm_predictions.append(prediction)

            predictions_scored += 1

        for prediction in match.predictions:
            if prediction.source != PredictionSource.USER:
                continue
            if not prediction.selected_model:
                continue

            llm_prediction = None
            for llm_pred in llm_predictions:
                if llm_pred.model_name == prediction.selected_model:
                    llm_prediction = llm_pred
                    break

            if llm_prediction is None:
                continue

            llm_pts = llm_prediction.points_awarded or 0
            user_pts = prediction.points_awarded or 0
            prediction.llm_compared_points = llm_pts

            if llm_pts > user_pts:
                prediction.user_vs_llm_result = "user_loss"
            elif llm_pts < user_pts:
                prediction.user_vs_llm_result = "user_win"
            else:
                prediction.user_vs_llm_result = "draw"

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