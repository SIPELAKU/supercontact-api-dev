from typing import Optional, List
from uuid import UUID

from fastapi import Query
from pydantic import EmailStr
from sqlmodel import SQLModel

from app.models.user_model import UserPosition


class UserGetQuery(SQLModel):
    page: int = Query(1, ge=1)
    limit: int = Query(10, ge=1, le=100)
    search: Optional[str] = Query(None)
    position: Optional[UserPosition] = Query(None)


class UserBase(SQLModel):
    fullname: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    position: Optional[UserPosition] = None


# CREATE
class UserCreateRequest(SQLModel):
    fullname: str
    email: EmailStr
    phone: str
    company: str
    position: UserPosition
    password: str


# UPDATE
class UserUpdateRequest(SQLModel):
    fullname: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    position: Optional[UserPosition] = None
    password: Optional[str] = None


class UserResponse(UserBase):
    id: UUID
    avatar_initial: str

    model_config = {"from_attributes": True}


# PAGINATION
class PaginatedUserResponse(SQLModel):
    total: int
    page: int
    limit: int
    total_pages: int
    users: List[UserResponse]
