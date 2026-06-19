from fastapi import APIRouter, Depends, HTTPException, Query
from app.api.dependencies import get_current_user, get_db
from schemas import PredictionUpdate, PredictionRead
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from schemas import PredictionCreateUser, PredictionRead
from models import User
from services import create_prediction, get_user_predictions, update_user_prediction, delete_user_prediction, get_user_prediction_for_match

router = APIRouter(tags=["predictions"])


@router.post("/predictions", response_model=PredictionRead)
async def prediction_from_user(
    data: PredictionCreateUser,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user), 
):
    user_prediction = await create_prediction(db, current_user, data)
    return user_prediction


@router.get("/predictions/me", response_model=list[PredictionRead])
async def get_user_prediction(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await get_user_predictions(db, current_user)


@router.patch("/predictions/{prediction_id}", response_model=PredictionRead)
async def update_prediction(
    prediction_id: int,
    data: PredictionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await update_user_prediction(db, current_user, prediction_id, data)

@router.delete("/predictions/{prediction_id}", status_code=204)
async def delete_prediction(
    prediction_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await delete_user_prediction(db, current_user, prediction_id)