from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.prediction import Prediction, PredictionSource


async def get_llm_stats(db: AsyncSession) -> dict:
    stmt = select(Prediction).where(
        Prediction.source == PredictionSource.LLM,
        Prediction.is_scored == True,
    )
    result = await db.execute(stmt)
    predictions = result.scalars().all()

    if not predictions:
        return {
            "total_predictions": 0,
            "correct_results": 0,
            "correct_goal_diff": 0,
            "exact_scores": 0,
            "avg_points": 0.0,
            "wins": 0,
            "draws": 0,
            "losses": 0,
        }

    total = len(predictions)
    correct_results = sum(1 for p in predictions if p.points_awarded and p.points_awarded >= 3)
    correct_goal_diff = sum(1 for p in predictions if p.points_awarded and p.points_awarded >= 1)
    exact_scores = sum(1 for p in predictions if p.points_awarded and p.points_awarded >= 5)
    total_points = sum(p.points_awarded or 0 for p in predictions)

    # LLM wins = user predictions where user_vs_llm_result == "user_loss"
    # LLM draws = user predictions where user_vs_llm_result == "draw"
    # LLM losses = user predictions where user_vs_llm_result == "user_win"
    user_stmt = select(Prediction).where(
        Prediction.source == PredictionSource.USER,
        Prediction.is_scored == True,
        Prediction.user_vs_llm_result.isnot(None),
    )
    user_result = await db.execute(user_stmt)
    user_predictions = user_result.scalars().all()

    llm_wins = sum(1 for p in user_predictions if p.user_vs_llm_result == "user_loss")
    llm_draws = sum(1 for p in user_predictions if p.user_vs_llm_result == "draw")
    llm_losses = sum(1 for p in user_predictions if p.user_vs_llm_result == "user_win")

    return {
        "total_predictions": total,
        "correct_results": correct_results,
        "correct_goal_diff": correct_goal_diff,
        "exact_scores": exact_scores,
        "avg_points": round(total_points / total, 2) if total > 0 else 0.0,
        "wins": llm_wins,
        "draws": llm_draws,
        "losses": llm_losses,
    }


async def get_llm_vs_user_stats(db: AsyncSession) -> dict:
    stmt = select(
        Prediction.user_vs_llm_result,
        func.count(Prediction.id),
    ).where(
        Prediction.source == PredictionSource.USER,
        Prediction.is_scored == True,
        Prediction.user_vs_llm_result.isnot(None),
    ).group_by(Prediction.user_vs_llm_result)

    result = await db.execute(stmt)
    rows = result.all()
    stats = {row[0]: row[1] for row in rows}

    return {
        "wins": stats.get("user_win", 0),
        "draws": stats.get("draw", 0),
        "losses": stats.get("user_loss", 0),
        "total_compared": sum(stats.values()),
    }
