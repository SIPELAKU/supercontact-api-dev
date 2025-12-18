from typing import Optional, List
from uuid import UUID

from pydantic import EmailStr
from sqlmodel import SQLModel

from app.models import UserRole, UserStatus


class UserGetQuery(SQLModel):
    page: int = 1
    limit: int = 10
    search: Optional[str] = None


class UserBase(SQLModel):
    fullname: Optional[str] = None
    email: Optional[EmailStr] = None
    # role: Optional[UserRole] = None
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
