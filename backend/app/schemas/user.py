from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from uuid import UUID

from app.models.user import AuthProvider


# Base schemas
class UserBase(BaseModel):
    email: EmailStr
    name: str = Field(..., min_length=1, max_length=100)


# Request schemas
class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    avatar_url: Optional[str] = None


# Response schemas
class UserResponse(UserBase):
    id: UUID
    avatar_url: Optional[str] = None
    auth_provider: AuthProvider
    is_active: bool
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserInDB(UserResponse):
    hashed_password: Optional[str] = None
    provider_id: Optional[str] = None
    updated_at: datetime
