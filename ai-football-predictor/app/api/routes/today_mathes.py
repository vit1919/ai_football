# app/api/routes/matches.py
from fastapi import APIRouter, Depends
from app.api.dependencies import get_db
from services import get_matches_today, save_matches

router = APIRouter()

@router.post("/matchday")
async def sync_matches(db=Depends(get_db)):
    
    matches = await get_matches_today(['eng.1', 'esp.1', 'ita.1', 'ger.1', 'fra.1'])
    await save_matches(db, matches)
    return {"saved": len(matches)}