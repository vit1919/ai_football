from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db
from app.core.constants import FOR_TESTING
from schemas.standing_schema import LeagueStandingResponse
from services import get_or_sync_standings, sync_standings_batch

router = APIRouter(tags=["standings"])

@router.post("/sync_standings")
async def sync_standings(db: AsyncSession = Depends(get_db)) -> list[dict]:
    return await sync_standings_batch(db, FOR_TESTING)


@router.get("/standings/{league_slug}", response_model=LeagueStandingResponse)
async def standings(league_slug: str, db: AsyncSession = Depends(get_db)):
    return await get_or_sync_standings(db, league_slug)
