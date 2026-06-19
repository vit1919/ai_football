from app.utils import get_now_utc, ensure_utc
from fastapi import HTTPException
from models import Prediction, User, Match
from models.prediction import PredictionSource
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from schemas import PredictionCreateUser, PredictionRead, PredictionUpdate
from sqlalchemy.exc import IntegrityError
from app.utils import calc_result


async def create_prediction(db: AsyncSession, current_user: User, data: PredictionCreateUser) -> Prediction:
    predicted_result = calc_result(data.score_home, data.score_away)

    match = await db.execute(select(Match).where(Match.id == data.match_id))
    match = match.scalar_one_or_none()

    if match is None:
        raise HTTPException(status_code=404, detail="Match not found")
    
    match_date = ensure_utc(match.date)
    if match_date <= get_now_utc():
        raise HTTPException(status_code=400, detail="Match already started")
    
    exists_stmt = select(Prediction.id).where(
        Prediction.user_id == current_user.id,
        Prediction.match_id == data.match_id
    )
    exists_result = await db.execute(exists_stmt)
    if exists_result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Prediction already exists for this match")

    prediction = Prediction(
        match_id=data.match_id,
        predicted_result=predicted_result,
        source=PredictionSource.USER,
        user_id=current_user.id,
        score_home=data.score_home,
        score_away=data.score_away,
        predicted_mvp=data.predicted_mvp,
        locked_at=match_date,
    )

    db.add(prediction)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Prediction already exists for this match")

    await db.refresh(prediction)

    return prediction


async def get_user_predictions(db: AsyncSession, current_user: User) -> list[Prediction]:
    stmt = (select(Prediction).where(Prediction.user_id == current_user.id).order_by(Prediction.created_at.desc()))
    result = await db.execute(stmt)
    
    return result.scalars().all()

async def update_user_prediction(db: AsyncSession, current_user: User, prediction_id: int, data: PredictionUpdate) -> Prediction:
    stmt = select(Prediction).where(Prediction.id == prediction_id, Prediction.user_id == current_user.id)
    result = await db.execute(stmt)
    prediction = result.scalar_one_or_none()

    if prediction is None:
        raise HTTPException(status_code=404, detail="Prediction not found")
    
    locked_at = prediction.locked_at
    if locked_at is not None and ensure_utc(locked_at) <= get_now_utc():
        raise HTTPException(status_code=403, detail="Prediction is locked and cannot be updated")

    if data.score_home is not None:
        prediction.score_home = data.score_home
    if data.score_away is not None:
        prediction.score_away = data.score_away
    if data.predicted_mvp is not None:
        prediction.predicted_mvp = data.predicted_mvp

    prediction.predicted_result = calc_result(prediction.score_home, prediction.score_away)

    try:
        await db.commit()
    except Exception:
        await db.rollback()
        raise
    await db.refresh(prediction)

    return prediction

async def delete_user_prediction(db: AsyncSession, current_user: User, prediction_id: int) -> None:
    stmt = select(Prediction).where(Prediction.id == prediction_id, Prediction.user_id == current_user.id)
    result = await db.execute(stmt)
    prediction = result.scalar_one_or_none()

    if prediction is None:
        raise HTTPException(status_code=404, detail="Prediction not found")
    
    locked_at = prediction.locked_at
    if locked_at is not None and ensure_utc(locked_at) <= get_now_utc():
        raise HTTPException(status_code=403, detail="Prediction is locked and cannot be deleted")

    await db.delete(prediction)
    try:
        await db.commit()
    except Exception:
        await db.rollback()
        raise

async def get_user_prediction_for_match(db: AsyncSession, current_user: User, match_id: int) -> Prediction | None:
    stmt = select(Prediction).where(Prediction.match_id == match_id, Prediction.user_id == current_user.id)
    result = await db.execute(stmt)
    prediction = result.scalar_one_or_none()

    return prediction