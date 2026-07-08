from sqlalchemy import select, func
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

    return {
        "total_predictions": total,
        "correct_results": correct_results,
        "correct_goal_diff": correct_goal_diff,
        "exact_scores": exact_scores,
        "avg_points": round(total_points / total, 2) if total > 0 else 0.0,
        "wins": 0,
        "draws": 0,
        "losses": 0,
    }


async def get_llm_vs_user_stats(db: AsyncSession) -> dict:
    from models.match import Match

    stmt = select(Match).where(
        Match.predictions_scored == True,
        Match.llm_vs_user_result.isnot(None),
    )
    result = await db.execute(stmt)
    matches = result.scalars().all()

    wins = sum(1 for m in matches if m.llm_vs_user_result == "win")
    draws = sum(1 for m in matches if m.llm_vs_user_result == "draw")
    losses = sum(1 for m in matches if m.llm_vs_user_result == "loss")

    return {
        "wins": wins,
        "draws": draws,
        "losses": losses,
        "total_compared": len(matches),
    }
