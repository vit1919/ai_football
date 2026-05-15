from fastapi import APIRouter, Depends, HTTPException, Query
from app.api.dependencies import get_current_user, get_db
from schemas import MatchSchemaIndexPage, MatchSchema
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils import get_today_range_utc, get_now_utc
from datetime import datetime
from schemas import PredictionCreateUser, PredictionRead
from models import User
from services import create_prediction

router = APIRouter(tags=["predictions"])

@router.post("/prediction", response_model=PredictionRead)
async def prediction_from_user(
    data: PredictionCreateUser,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user), 
):
    user_prediction = await create_prediction(db, current_user, data)
    return user_prediction
    