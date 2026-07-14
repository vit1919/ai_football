import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from app.api.dependencies import get_current_user, get_db
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from schemas import TeamSchema, FavouriteTeamRead
from models import User, Team
from services import get_team_by_id, get_team_info, save_team_to_db, add_favourite_team, delete_favourite_team, get_user_favourite_teams

logger = logging.getLogger(__name__)
router = APIRouter(tags=["teams"])

@router.get("/teams/{league_slug}/{team_id}", response_model=TeamSchema)
async def get_team(league_slug: str, team_id: int, db: AsyncSession = Depends(get_db)):
    team = await get_team_by_id(db, team_id)
    if team is None:
        new_team = await get_team_info(league_slug, team_id)
        if new_team is None:
            raise HTTPException(status_code=404, detail="Team not found")

        logger.debug("Team %d fetched from ESPN", team_id)
        return await save_team_to_db(db, new_team)

    logger.debug("Team %d loaded from DB", team_id)
    return team


@router.post("/teams/{team_id}/favourite", response_model=FavouriteTeamRead)
async def favourite_team(team_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    team = await get_team_by_id(db, team_id)
    if team is None:
        raise HTTPException(status_code=404, detail="Team not found")
    
    return await add_favourite_team(db, current_user, team)


@router.delete("/teams/{team_id}/favourite", status_code=204)
async def unfavourite_team(team_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    team = await get_team_by_id(db, team_id)
    if team is None:
        raise HTTPException(status_code=404, detail="Team not found")
    
    await delete_favourite_team(db, current_user, team)
    
@router.get("/favourite-teams/me", response_model=list[FavouriteTeamRead])
async def get_favourite_teams(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await get_user_favourite_teams(db, current_user)