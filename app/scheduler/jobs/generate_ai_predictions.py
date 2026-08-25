import logging

from app.core.database import AsyncSessionLocal
from services.ai_prediction_service import generate_for_upcoming_matches

logger = logging.getLogger(__name__)


async def generate_ai_predictions_job():
    try:
        async with AsyncSessionLocal() as db:
            predictions = await generate_for_upcoming_matches(db)
            if predictions:
                logger.info("Generated %d AI predictions", len(predictions))
    except Exception as e:
        logger.error("Error generating AI predictions: %s", e, exc_info=True)
