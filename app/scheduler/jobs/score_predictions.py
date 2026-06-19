from app.core.database import AsyncSessionLocal
from services import score_predictions

async def score_predictions_job():
    try: 
        async with AsyncSessionLocal() as db:
            result = await score_predictions(db)

        print(result)

    except Exception as e:
        print(f"Error scoring predictions: {e}")