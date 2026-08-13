from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from app.api.dependencies import get_db, get_current_user
from app.core.security import hash_password, verify_password
from app.core.jwt import create_refresh_token, create_token, create_access_token, decode_refresh_token
from models.user import User
from schemas.user_schema import RefreshTokenRequest, UserCreate, UserRead, Token, UserLogin
from services import get_user_by_email, get_user_by_username, user_email_exists, username_exists, create_user
from services.auth_service import get_user_by_id


router = APIRouter(prefix="/auth", tags=["auth"])

@router.get("/me", response_model=UserRead)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/register", response_model=UserRead, status_code=201)
async def register(data: UserCreate, db: AsyncSession = Depends(get_db)):

    if await user_email_exists(db, data.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    if await username_exists(db, data.username):
        raise HTTPException(status_code=400, detail="Username already registered")
    
    try:
        user = await create_user(db, data)
        return user
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=409,
            detail="User with this email or username already exists"
        )

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(),  db: AsyncSession = Depends(get_db)):
    user = await get_user_by_email(db, form_data.username)
    if user is None or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {
        "access_token": create_access_token(user.id),
        "refresh_token": create_refresh_token(user.id),
        "token_type": "bearer",
    }

@router.post("/refresh", response_model=Token)
async def refresh_tokens(
    payload: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
):
    token_data = decode_refresh_token(payload.refresh_token)

    try:
        user_id = int(token_data["sub"])
    except (ValueError, KeyError):
        raise HTTPException(status_code=401, detail="Invalid token payload")

    user = await get_user_by_id(db, user_id)
    if user is None or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")

    return {
        "access_token": create_access_token(user.id),
        "refresh_token": create_refresh_token(user.id),
        "token_type": "bearer",
    }



