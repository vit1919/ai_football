from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, get_db
from app.core.limiter import limiter
from models import User
from schemas import PredictionCreateUser, PredictionRead, PredictionUpdate
from schemas.prediction_schema import PredictionWithMatchRead
from services import (
    create_prediction,
    delete_user_prediction,
    get_all_predictions,
    get_user_predictions,
    update_user_prediction,
)

router = APIRouter(tags=["predictions"])


@router.get("/predictions/all", response_model=list[PredictionRead])
async def list_all_predictions(db: AsyncSession = Depends(get_db)):
    return await get_all_predictions(db)


@router.post("/predictions", response_model=PredictionRead)
@limiter.limit("20/minute")
async def prediction_from_user(
    request: Request,
    data: PredictionCreateUser,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user_prediction = await create_prediction(db, current_user, data)
    return user_prediction


@router.get("/predictions/me", response_model=list[PredictionWithMatchRead])
async def get_user_prediction(
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
):
    return await get_user_predictions(db, current_user)


@router.patch("/predictions/{prediction_id}", response_model=PredictionRead)
@limiter.limit("20/minute")
async def update_prediction(
    request: Request,
    prediction_id: int,
    data: PredictionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await update_user_prediction(db, current_user, prediction_id, data)


@router.delete("/predictions/{prediction_id}", status_code=204)
async def delete_prediction(
    request: Request,
    prediction_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await delete_user_prediction(db, current_user, prediction_id)
