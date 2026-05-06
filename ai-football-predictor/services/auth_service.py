from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models import User


async def get_user_by_id(db: AsyncSession, id: int) -> User | None:
    stmt = select(User).where(User.id == id)
    result = await db.execute(stmt)

    return result.scalar_one_or_none()

async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    stmt = select(User).where(User.email == email)
    result = await db.execute(stmt)

    return result.scalar_one_or_none()

async def get_user_by_username(db: AsyncSession, username: str) -> User | None:
    stmt = select(User).where(User.username == username)
    result = await db.execute(stmt)

    return result.scalar_one_or_none()