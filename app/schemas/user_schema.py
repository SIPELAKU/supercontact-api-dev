from typing import Optional, List
from pydantic import BaseModel, EmailStr
from uuid import UUID
from app.models.user_model import RoleEnum, StatusEnum


class UserBase(BaseModel):
    fullname: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[RoleEnum] = None
    status: Optional[StatusEnum] = None


class UserCreate(BaseModel):
    fullname: str
    email: EmailStr
    password: str
    role: RoleEnum
    status: StatusEnum


class UserUpdate(BaseModel):
    fullname: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    role: Optional[RoleEnum] = None
    status: Optional[StatusEnum] = None


class UserResponse(UserBase):
    id: UUID
    avatar_initial: Optional[str] = None

    model_config = {"from_attributes": True}


class PaginatedUserResponse(BaseModel):
    data: List[UserResponse]
    total: int
    page: int
    page_size: int
