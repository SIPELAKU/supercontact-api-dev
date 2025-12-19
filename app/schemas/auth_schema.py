from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import EmailStr
from sqlmodel import SQLModel, Field

from app.models import UserPosition, UserOTPType


class User(SQLModel):
    id: UUID
    fullname: str
    email: EmailStr
    avatar_initial: str
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserRegisterRequest(SQLModel):
    fullname: str = Field(min_length=3, max_length=100)
    email: EmailStr
    phone: str
    company: str
    position: UserPosition
    password: str = Field(min_length=3, max_length=64)
    confirm_password: str = Field(min_length=3, max_length=64)


class UserRegisterResponse(SQLModel):
    message: str

    class Config:
        from_attributes = True

    class Config:
        from_attributes = True


class UserLoginRequest(SQLModel):
    email: EmailStr
    password: str


class UserLoginResponse(SQLModel):
    user: User
    access_token: str

    class Config:
        from_attributes = True


class ResetPasswordRequest(SQLModel):
    password: str
    confirm_password: str


class ResetPasswordResponse(SQLModel):
    message: str


class ResendOtpRequest(SQLModel):
    email: EmailStr
    otp_type: UserOTPType


class ResendOtpResponse(SQLModel):
    email: EmailStr
    otp_type: UserOTPType
    valid: bool


class VerifyOtpRequest(SQLModel):
    email: EmailStr
    otp_type: UserOTPType
    code: str


class VerifyOtpResponse(SQLModel):
    email: EmailStr
    otp_type: UserOTPType
    access_token: Optional[str]
    reset_token: Optional[str]
