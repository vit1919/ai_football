
from re import match

from fastapi import APIRouter, Depends, HTTPException, Query
from app.api.dependencies import get_current_user, get_current_user_optional, get_db
from services import get_matches_today, save_matches, get_matches, get_match_by_id, get_all_matches, get_user_prediction_for_match, get_match_detail
from services.comparison_service import get_match_comparison
from schemas import MatchSchemaIndexPage, MatchSchema, MatchDetailResponse
from schemas.prediction_schema import PredictionRead
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils import get_today_range_utc, get_now_utc
from datetime import datetime
from pydantic import AwareDatetime, BaseModel
from app.core.constants import TOP5_LEAGUES, MAIN_LEAGUES
from models import User

router = APIRouter(tags=["matches"])


class MatchComparisonResponse(BaseModel):
    match: MatchSchema
    user_prediction: PredictionRead | None = None
    llm_prediction: PredictionRead | None = None
    result: str | None = None
    actual_score: dict | None = None

@router.post("/sync_matches", dependencies=[Depends(get_current_user)])
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


@router.get("/matches/{event_id}/compare", response_model=MatchComparisonResponse)
async def compare_predictions(
    event_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    data = await get_match_comparison(db, event_id, current_user)
    return MatchComparisonResponse(
        match=data["match"],
        user_prediction=data["user_prediction"],
        llm_prediction=data["llm_prediction"],
        result=data["result"],
        actual_score=data["actual_score"],
    )


@router.get("/matches/{event_id}", response_model=MatchDetailResponse)
async def get_detailed_match(
    event_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    match, user_prediction = await get_match_detail(db, event_id, current_user)
    return MatchDetailResponse(match=match, user_prediction=user_prediction)

