from app.core.database import AsyncSessionLocal
from sqlalchemy.ext.asyncio import AsyncSession


async def get_db() -> AsyncSession: # type: ignore 
    async with AsyncSessionLocal() as session:
        yield session 