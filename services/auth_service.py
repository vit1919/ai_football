import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from models import User
from pydantic import EmailStr
from app.core.security import hash_password
from schemas.user_schema import UserCreate

logger = logging.getLogger(__name__)

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

async def user_email_exists(db: AsyncSession, email: EmailStr) -> bool:
    stmt = select(User).where(User.email == email)
    result = await db.execute(stmt)

    if result.scalar_one_or_none() is not None:
        return True
    return False

async def username_exists(db: AsyncSession, username: str) -> bool:
    stmt = select(User).where(User.username == username)
    result = await db.execute(stmt)

    if result.scalar_one_or_none() is not None:
        return True
    return False

async def create_user(db: AsyncSession, user_data: UserCreate) -> User:
    user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hash_password(user_data.password)
    )
    db.add(user)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise ValueError("User with this email or username already exists")
    except SQLAlchemyError:
        await db.rollback()
        raise
    await db.refresh(user)

    return user


