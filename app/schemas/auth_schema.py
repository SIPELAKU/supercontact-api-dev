from datetime import datetime
from uuid import UUID
from sqlmodel import SQLModel

from app.models.user_model import RoleEnum


class User(SQLModel):
    id: UUID
    fullname: str
    email: str
    role: RoleEnum
    created_at: datetime
    updated_at: datetime


class UserLoginRequest(SQLModel):
    email: str
    password: str


class UserLoginResponse(SQLModel):
    access_token: str
    token_type: str = "bearer"

    model_config = {"from_attributes": True}
