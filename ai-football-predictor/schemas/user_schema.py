from datetime import datetime
from pydantic import BaseModel, EmailStr, AwareDatetime, Field


class UserBase(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr = Field(max_length=255)

class UserLogin(BaseModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=6, max_length=128)

class UserCreate(UserBase):
    password: str = Field(min_length=6, max_length=128)

class UserUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=3, max_length=50)
    email: EmailStr | None = Field(default=None, max_length=255)
    password: str | None = Field(default=None, min_length=6, max_length=128)

class UserRead(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    user_id: int | None = None

