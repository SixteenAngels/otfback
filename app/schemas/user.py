from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from enum import Enum


class UserRole(str, Enum):
    ADMIN = "admin"
    SCANNER = "scanner"
    VIEWER = "viewer"


class UserBase(BaseModel):
    username: str
    email: str
    role: UserRole = UserRole.VIEWER


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None
