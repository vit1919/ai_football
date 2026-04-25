
from fastapi import APIRouter, Depends
from app.api.dependencies import get_db
from services import get_matches_today, save_matches, get_matches, get_match_by_id
from schemas import MatchSchemaIndexPage, MatchSchema
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter()

@router.post("/sync_matches")
async def sync_matches(db: AsyncSession = Depends(get_db)):
    matches = await get_matches_today(['eng.1', 'esp.1', 'ita.1', 'ger.1', 'fra.1'])
    await save_matches(db, matches)
    return {"saved": len(matches)}


@router.get("/matches", response_model=list[MatchSchemaIndexPage])
async def list_matches(db: AsyncSession = Depends(get_db)):
    matches = await get_matches(db, ['eng.1', 'esp.1', 'ita.1', 'ger.1', 'fra.1'])
    return matches

@router.get("/matches/{event_id}", response_model=MatchSchema)
async def get_detailed_match(event_id : int, db: AsyncSession = Depends(get_db)):
    match = await get_match_by_id(db, event_id)
    return match