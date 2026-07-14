import logging
from app.core.database import AsyncSessionLocal
from services import score_predictions

logger = logging.getLogger(__name__)

async def score_predictions_job():
    try:
        async with AsyncSessionLocal() as db:
            result = await score_predictions(db)

        logger.info("Score predictions result: %s", result)

    except Exception as e:
        logger.error("Error scoring predictions: %s", e, exc_info=True)