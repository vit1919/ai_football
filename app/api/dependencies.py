from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException
from app.core.database import AsyncSessionLocal
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.jwt import decode_token
from models import User
from services import get_user_by_id

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def get_db() -> AsyncSession: # type: ignore 
    async with AsyncSessionLocal() as session:
        yield session 


async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> User:
    try:
        user_id = int(decode_token(token)["sub"])

    except (ValueError, KeyError):
        raise HTTPException(status_code=401, detail="Invalid token payload")
    
    user: User = await get_user_by_id(db, user_id)

    if user is None:
        raise HTTPException(status_code=401, detail="could not find user")
        
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=403, detail="Inactive user")
    return current_user

oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)

async def get_current_user_optional(token: str | None = Depends(oauth2_scheme_optional),db: AsyncSession = Depends(get_db),) -> User | None:
    if not token:
        return None
    try:
        user_id = int(decode_token(token)["sub"])
    except (ValueError, KeyError):
        raise HTTPException(status_code=401, detail="Invalid token payload")
    user = await get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="could not find user")
    return user




