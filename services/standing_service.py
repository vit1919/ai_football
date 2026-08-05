import logging
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models import Standing
from schemas.standing_schema import StandingRead, LeagueStandingResponse
from services.espn_client_standings import get_standings

logger = logging.getLogger(__name__)


async def sync_standings_from_espn(db: AsyncSession, league_slug: str) -> dict:
    standings = await get_standings(league_slug)
    if not standings:
        logger.warning("No standings received for league %s", league_slug)
        return {"league": league_slug, "standings_received": 0, "added": 0, "updated": 0}

    season = standings[0].season
    stmt = select(Standing).where(
        Standing.league_slug == league_slug,
        Standing.season == season,
    )
    result = await db.execute(stmt)
    existing = {m.team_espn_id: m for m in result.scalars().all()}

    added = 0
    updated = 0

    for s in standings:
        data = s.model_dump()
        current = existing.get(s.team_espn_id)
        if current:
            for k, v in data.items():
                setattr(current, k, v)
            updated += 1
        else:
            db.add(Standing(**data))
            added += 1

    return {"league": league_slug, "standings_received": len(standings), "added": added, "updated": updated}


async def sync_standings_batch(db: AsyncSession, leagues: list[str]) -> list[dict]:
    try:
        results = []
        for league in leagues:
            results.append(await sync_standings_from_espn(db, league))
        await db.commit()
    except Exception:
        await db.rollback()
        raise
    return results


async def get_standings_from_db(db: AsyncSession, league_slug: str) -> LeagueStandingResponse | None:
    stmt = (
        select(Standing)
        .where(Standing.league_slug == league_slug)
        .order_by(Standing.rank)
    )
    result = await db.execute(stmt)
    standings = result.scalars().all()

    if not standings:
        return None

    first = standings[0]
    entries = [StandingRead.model_validate(s) for s in standings]

    return LeagueStandingResponse(
        league_slug=first.league_slug,
        group_name=first.group_name,
        season=first.season,
        entries=entries,
    )


async def get_or_sync_standings(db: AsyncSession, league_slug: str) -> LeagueStandingResponse:
    cached = await get_standings_from_db(db, league_slug)
    if cached:
        return cached

    await sync_standings_from_espn(db, league_slug)
    await db.commit()
    result = await get_standings_from_db(db, league_slug)
    if not result:
        raise HTTPException(status_code=404, detail=f"Standings not found for league: {league_slug}")
    return result
