
from services import get_matches_today, upsert_matches
from app.core.database import AsyncSessionLocal
from app.core.constants import TOP5_LEAGUES, MAIN_LEAGUES, FOR_TESTING


async def sync_matches_job():
    try: 
        matches = await get_matches_today(FOR_TESTING)

        async with AsyncSessionLocal() as db:
            result = await upsert_matches(db, matches)

        print(result)

    except Exception as e:
        print(f"Error syncing matches: {e}")