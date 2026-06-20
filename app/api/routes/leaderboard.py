from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dependencies import get_db
from schemas.user_schema import LeaderboardEntry
from services.leaderboard_service import get_leaderboard

router = APIRouter(tags=["leaderboard"])


@router.get("/leaderboard", response_model=list[LeaderboardEntry])
async def leaderboard(limit: int = Query(default=20, ge=1, le=100), db: AsyncSession = Depends(get_db)):
    return await get_leaderboard(db, limit)
