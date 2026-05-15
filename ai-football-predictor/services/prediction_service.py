
from app.utils import get_now_utc
from fastapi import HTTPException
from models import Prediction, User, Match
from models.prediction import Result, PredictionSource
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from schemas import PredictionCreateUser, PredictionRead
from sqlalchemy.exc import IntegrityError


async def create_prediction(db: AsyncSession, current_user: User, data: PredictionCreateUser) -> Prediction:

    if data.score_home > data.score_away:
        predicted_result = Result.HOME_WIN
    elif data.score_home < data.score_away:
        predicted_result = Result.AWAY_WIN
    else:
        predicted_result = Result.DRAW

    match = await db.execute(select(Match).where(Match.id == data.match_id))
    match = match.scalar_one_or_none()

    if match is None:
        raise HTTPException(status_code=404, detail="Match not found")
    
    if match.date <= get_now_utc():
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
        locked_at=match.date,
    )

    db.add(prediction)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Prediction already exists for this match")

    await db.refresh(prediction)

    return prediction