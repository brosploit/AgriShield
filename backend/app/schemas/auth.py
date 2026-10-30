"""AgriShield AI - Authentication & User Schemas
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from app.core.permissions import UserRole


class UserBase(BaseModel):
    email: EmailStr
    phone_number: str = Field(..., pattern=r"^\+?[0-9]{10,14}$", description="E.164 or 10-digit Indian mobile number")
    full_name: str = Field(..., min_length=2, max_length=100)
    role: UserRole


class UserRegisterRequest(UserBase):
    password: str = Field(..., min_length=8, max_length=128)

    # Optional initial profile data on registration
    village: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = "Maharashtra"
    pincode: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class UserLoginRequest(BaseModel):
    identifier: str = Field(..., description="Email address or phone number")
    password: str = Field(..., min_length=1)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in_seconds: int
    user_id: str
    role: str
    full_name: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: Optional[str] = None


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8, max_length=128)


class UserResponse(UserBase):
    id: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

