from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.user import User


async def get_leaderboard(db: AsyncSession, limit: int = 20) -> list[dict]:

    stmt = (select(User).where(User.is_active == True).order_by(User.total_points.desc()).limit(limit))
    result = await db.execute(stmt)
    users = result.scalars().all()

    return [
        {"rank": i + 1, "username": u.username, "total_points": u.total_points}
        for i, u in enumerate(users)
    ]
