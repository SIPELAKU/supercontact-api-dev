from typing import Optional, List
from uuid import UUID

from fastapi import Query
from pydantic import EmailStr
from sqlmodel import SQLModel

from app.models import UserRole, UserStatus


class UserGetQuery(SQLModel):
    page: int = Query(1, ge=1)
    limit: int = Query(10, ge=1, le=100)
    search: Optional[str] = Query(None)
    role: Optional[UserRole] = Query(None)
    status: Optional[UserStatus] = Query(None)


class UserBase(SQLModel):
    fullname: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None
    status: Optional[UserStatus] = None


class UserCreateRequest(SQLModel):
    fullname: str
    email: EmailStr
    password: str
    role: UserRole
    status: UserStatus


class UserUpdateRequest(SQLModel):
    fullname: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    role: Optional[UserRole] = None
    status: Optional[UserStatus] = None


class UserResponse(UserBase):
    id: UUID
    avatar_initial: Optional[str] = None

    model_config = {"from_attributes": True}


class PaginatedUserResponse(SQLModel):
    total: int
    page: int
    limit: int
    total_pages: int
    users: List[UserResponse]
