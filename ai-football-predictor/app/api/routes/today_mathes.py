# app/api/routes/matches.py
from fastapi import APIRouter, Depends
from app.api.dependencies import get_db
from services.espn_client import get_matches_today_top5
from services.match_service import save_matches

router = APIRouter()

@router.post("/matchday")
async def sync_matches(db=Depends(get_db)):
    
    matches = await get_matches_today_top5()
    await save_matches(db, matches)
    return {"saved": len(matches)}