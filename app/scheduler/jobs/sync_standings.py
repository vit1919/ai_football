import logging
from services import sync_standings_batch
from app.core.database import AsyncSessionLocal
from app.core.constants import FOR_TESTING

logger = logging.getLogger(__name__)


async def sync_standings_job():
    try:
        async with AsyncSessionLocal() as db:
            results = await sync_standings_batch(db, FOR_TESTING)
            for result in results:
                logger.info("Sync standings: %s", result)

    except Exception as e:
        logger.error("Error syncing standings: %s", e, exc_info=True)
