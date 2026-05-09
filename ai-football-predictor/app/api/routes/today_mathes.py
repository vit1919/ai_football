
from fastapi import APIRouter, Depends, HTTPException, Query
from app.api.dependencies import get_db
from services import get_matches_today, save_matches, get_matches, get_match_by_id, get_all_matches
from schemas import MatchSchemaIndexPage, MatchSchema
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils import get_today_range_utc, get_now_utc
from datetime import datetime
from pydantic import AwareDatetime
from app.core.constants import TOP5_LEAGUES, MAIN_LEAGUES 

router = APIRouter(tags=["matches"])

@router.post("/sync_matches")
async def sync_matches(db: AsyncSession = Depends(get_db)) -> dict:
    matches = await get_matches_today(MAIN_LEAGUES)
    stats = await save_matches(db, matches)

    return {
        "api_received": stats["matches_received"],
        "added_to_db": stats["added"],
        "already_in_db": stats["matches_received"] - stats["added"]
    }

@router.get("/matches", response_model=list[MatchSchemaIndexPage])
async def list_matches(
    db: AsyncSession = Depends(get_db),
    leagues: list[str] | None = Query(default=None),
    start_at: datetime | None = Query(default=None),
    end_at: datetime | None = Query(default=None),
):
    return await get_matches(db, leagues, start_at, end_at)


@router.get("/matches/all", response_model=list[MatchSchemaIndexPage])
async def list_all_matches(db: AsyncSession = Depends(get_db)):
    return await get_all_matches(db)



#index
@router.get("/matches/today", response_model=list[MatchSchemaIndexPage])
async def list_matches_today(db: AsyncSession = Depends(get_db)) -> list[MatchSchemaIndexPage]:
    start, end = get_today_range_utc()
    return await get_matches(db, start_at=start, end_at=end)


@router.get("/matches/{event_id}", response_model=MatchSchema)
async def get_detailed_match(event_id : int, db: AsyncSession = Depends(get_db)) -> MatchSchema:
    match = await get_match_by_id(db, event_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    return match