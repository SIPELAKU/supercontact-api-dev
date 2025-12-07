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


class UserLoginRequest(SQLModel):
    email: EmailStr
    password: str


class UserLoginResponse(SQLModel):
    user: User
    access_token: str

    model_config = {"from_attributes": True}
