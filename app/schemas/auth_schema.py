from datetime import datetime
from uuid import UUID

from pydantic import EmailStr
from sqlmodel import SQLModel

from app.models import UserRole, UserStatus


class User(SQLModel):
    id: UUID
    fullname: str
    email: str
    role: UserRole
    status: UserStatus
    avatar_initial: str
    created_at: datetime
    updated_at: datetime


class UserRegisterRequest(SQLModel):
    fullname: str
    email: EmailStr
    password: str
    company_name: str


class UserRegisterResponse(SQLModel):
    user: User

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


class ForgotPasswordRequest(SQLModel):
    email: EmailStr


class ResetPasswordRequest(SQLModel):
    email: EmailStr
    new_password: str
    token: str
