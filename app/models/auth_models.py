"""
Authentication Models for Legal Dashboard
========================================
Pydantic models for user authentication and authorization.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr


class UserBase(BaseModel):
    """Base user model"""
    username: str = Field(..., min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    is_active: bool = True
    is_admin: bool = False


class UserCreate(UserBase):
    """User creation model"""
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    """User login model"""
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)


class User(UserBase):
    """User model"""
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


class Token(BaseModel):
    """Token model"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    refresh_token: Optional[str] = None


class TokenData(BaseModel):
    """Token data model"""
    username: Optional[str] = None
    user_id: Optional[int] = None
    is_admin: bool = False


class PasswordChange(BaseModel):
    """Password change model"""
    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=6)


class PasswordReset(BaseModel):
    """Password reset model"""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation model"""
    token: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=6)


class UserUpdate(BaseModel):
    """User update model"""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    """User response model"""
    id: int
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    is_active: bool
    is_admin: bool
    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    """Login response model"""
    user: UserResponse
    token: Token


class AuthStatus(BaseModel):
    """Authentication status model"""
    is_authenticated: bool
    user: Optional[UserResponse] = None
    token_expires_in: Optional[int] = None
