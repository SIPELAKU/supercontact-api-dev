from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import EmailStr
from sqlmodel import SQLModel


class User(SQLModel):
    id: UUID
    fullname: str
    email: str
    role: Optional[UUID]
    status: str
    avatar_initial: str
    created_at: datetime
    updated_at: datetime


class UserRegisterRequest(SQLModel):
    fullname: str
    email: EmailStr
    password: str
    company_name: str
    avatar_initial: str  #
    role: str  #
    status: str  #


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
