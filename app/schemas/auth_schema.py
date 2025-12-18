from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import EmailStr, StringConstraints
from sqlmodel import SQLModel
from typing_extensions import Annotated

from app.models import UserPosition, UserOTPType


class User(SQLModel):
    id: UUID
    fullname: str
    email: str
    role: Optional[UUID]
    status: str
    is_verified: bool
    avatar_initial: str
    created_at: datetime
    updated_at: datetime


class UserRegisterRequest(SQLModel):
    fullname: Annotated[
        str,
        StringConstraints(
            min_length=3,
            max_length=100,
            strip_whitespace=True
        )
    ]
    email: EmailStr
    phone: str
    company: str
    position: UserPosition
    password: str
    confirm_password: str


class UserRegisterResponse(SQLModel):
    message: str

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
