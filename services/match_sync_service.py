from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from models import Match
from schemas import MatchSchema

_INTERNAL_FIELDS: set[str] = {"predictions_scored", "lineups_fetched"}

async def upsert_matches(db: AsyncSession, matches: list[MatchSchema]) -> dict:
    if not matches:
        return {"matches_received": 0, "added": 0, "updated": 0}

    event_ids = [m.event_id for m in matches]
    result = await db.execute(select(Match).where(Match.event_id.in_(event_ids)))
    existing = {m.event_id: m for m in result.scalars().all()}

    added = 0
    updated = 0

    for match in matches:
        data = match.model_dump(exclude={"id"})
        current = existing.get(match.event_id)
        if current:
            for key, value in data.items():
                if key not in _INTERNAL_FIELDS:
                    setattr(current, key, value)
            updated += 1
        else:
            db.add(Match(**data))
            added += 1

    try:
        await db.commit()
    except SQLAlchemyError:
        await db.rollback()
        raise

    return {"matches_received": len(matches), "added": added, "updated": updated}

