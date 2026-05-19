from datetime import datetime
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from schemas import MatchSchema, MatchSchemaIndexPage
from services.prediction_service import get_user_prediction_for_match
from models import User, Match


async def save_matches(db: AsyncSession, matches: list[MatchSchema]) -> dict:

    if not matches:
        return {'matches_received': 0, 'added': 0}

    event_ids = [match.event_id for match in matches]

    stmt = select(Match.event_id).where(Match.event_id.in_(event_ids))
    result = await db.execute(stmt)
    ids = set(result.scalars().all())

    new_matches = [Match(**match.model_dump()) for match in matches if match.event_id not in ids]

    if new_matches:
        db.add_all(new_matches)
        await db.commit()

    return {
        'matches_received': len(matches),
        'added': len(new_matches)
    }


async def get_match_by_id(db: AsyncSession, event_id: int) -> Match | None:
    stmt = select(Match).where(Match.event_id == event_id)
    result = await db.execute(stmt)

    return result.scalars().one_or_none()
    

async def get_matches(db: AsyncSession, leagues: list[str] | None = None, start_at: datetime | None = None, end_at: datetime | None = None,) -> list[Match]:
    stmt = select(Match)
    
    if leagues:
        stmt = stmt.where(Match.league_slug.in_(leagues))
    if start_at is not None:
        stmt = stmt.where(Match.date >= start_at)
    if end_at is not None:
        stmt = stmt.where(Match.date < end_at)

    stmt = stmt.order_by(Match.date.asc())
    result = await db.execute(stmt)

    return result.scalars().all()


async def get_all_matches(db: AsyncSession) -> list[Match]:
    stmt = select(Match).order_by(Match.date.asc())
    result = await db.execute(stmt)

    return result.scalars().all()

async def get_match_detail(db: AsyncSession, event_id: int, user: User | None):
    match = await get_match_by_id(db, event_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    user_prediction = None
    if user:
        user_prediction = await get_user_prediction_for_match(db, user, match.id)

    return match, user_prediction





