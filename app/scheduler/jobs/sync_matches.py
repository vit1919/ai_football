import logging
from services import get_matches_today, upsert_matches
from app.core.database import AsyncSessionLocal
from app.core.constants import TOP5_LEAGUES, MAIN_LEAGUES, FOR_TESTING

logger = logging.getLogger(__name__)


async def sync_matches_job():
    try:
        matches = await get_matches_today(FOR_TESTING)

        async with AsyncSessionLocal() as db:
            result = await upsert_matches(db, matches)

        logger.info("Sync matches result: %s", result)

    except Exception as e:
        logger.error("Error syncing matches: %s", e, exc_info=True)