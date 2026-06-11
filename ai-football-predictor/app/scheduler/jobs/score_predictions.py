from app.core.database import AsyncSessionLocal

async def score_predictions_job():
    try: 
        async with AsyncSessionLocal() as db:
            result = await score_predictions(db)

        print(result)

    except Exception as e:
        print(f"Error scoring predictions: {e}")