from datetime import datetime
from uuid import UUID

from sqlmodel import SQLModel

from app.models import UserRole


class User(SQLModel):
    id: UUID
    fullname: str
    email: str
    role: UserRole
    created_at: datetime
    updated_at: datetime


class UserLoginRequest(SQLModel):
    email: str
    password: str


class UserLoginResponse(SQLModel):
    user: User
    access_token: str

    class Config:
        from_attributes = True
