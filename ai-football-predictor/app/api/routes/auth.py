from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dependencies import get_db, get_current_user
from app.core.security import hash_password, verify_password
from app.core.jwt import create_token
from models.user import User
from schemas.user_schema import UserCreate, UserRead, Token, UserLogin
from services import get_user_by_email, get_user_by_username, user_email_exists, username_exists, create_user


router = APIRouter(prefix="/auth", tags=["auth"])

@router.get("/me", response_model=UserRead)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/register", response_model=UserRead)
async def register(data: UserCreate, db: AsyncSession = Depends(get_db)):

    if await user_email_exists(db, data.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    if await username_exists(db, data.username):
        raise HTTPException(status_code=400, detail="Username already registered")
    
    user = await create_user(db, data)
    return user


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):

    user = await get_user_by_email(db, form_data.username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    jwt_token = create_token(user.id)
    return {"access_token": jwt_token, "token_type": "bearer"} 



