from app.core.database import AsyncSessionLocal
from services.ai_prediction_service import generate_for_upcoming_matches


async def generate_ai_predictions_job():
    try:
        async with AsyncSessionLocal() as db:
            predictions = await generate_for_upcoming_matches(db)
            if predictions:
                print(f"Generated {len(predictions)} AI predictions")
    except Exception as e:
        print(f"Error generating AI predictions: {e}")
