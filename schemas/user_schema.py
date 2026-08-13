from datetime import datetime
from pydantic import BaseModel, EmailStr, AwareDatetime, Field, field_validator
import re

class UserBase(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr = Field(max_length=255)

    @field_validator("email")
    @classmethod
    def norm_email(cls, v: str) -> str:
        return v.strip().lower()
    
    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        v = v.strip()
        if not re.fullmatch(r"[a-zA-Z0-9_]{3,30}", v):
            raise ValueError("Username must be 3-30 chars, latin letters/numbers/_")
        return v

    
class UserLogin(BaseModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=6, max_length=72)

class UserCreate(UserBase):
    password: str = Field(min_length=6, max_length=72)

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not re.search(r"[A-Za-z]", v) or not re.search(r"\d", v):
            raise ValueError("Password must contain at least one letter and one digit")
        return v

class UserUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=3, max_length=50)
    email: EmailStr | None = Field(default=None, max_length=255)
    password: str | None = Field(default=None, min_length=6, max_length=72)

class UserRead(UserBase):
    id: int
    is_active: bool
    total_points: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class LeaderboardEntry(BaseModel):
    rank: int
    username: str
    total_points: int

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    refresh_token: str  
    token_type: str = "bearer"

class RefreshTokenRequest(BaseModel): 
    refresh_token: str


class TokenData(BaseModel):
    user_id: int | None = None

