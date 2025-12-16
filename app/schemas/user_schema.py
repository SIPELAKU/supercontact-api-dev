from typing import Optional, List
from pydantic import BaseModel, EmailStr
from uuid import UUID
from app.models.user_model import UserStatus


class UserBase(BaseModel):
    fullname: Optional[str] = None
    email: Optional[EmailStr] = None
    status: Optional[UserStatus] = None
    employee_id: Optional[str] = None
    department_id: Optional[UUID] = None
    role_id: Optional[UUID] = None


class UserCreate(BaseModel):
    fullname: str
    email: EmailStr
    password: str
    role_id: UUID
    status: Optional[UserStatus] = UserStatus.PENDING
    employee_id: Optional[str] = None
    department_id: Optional[UUID] = None


class UserUpdate(BaseModel):
    fullname: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    status: Optional[UserStatus] = None
    role_id: Optional[UUID] = None
    employee_id: Optional[str] = None
    department_id: Optional[UUID] = None


class UserResponse(UserBase):
    id: UUID
    avatar_initial: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    model_config = {"from_attributes": True}


class PaginatedUserResponse(BaseModel):
    data: List[UserResponse]
    total: int
    page: int
    page_size: int
