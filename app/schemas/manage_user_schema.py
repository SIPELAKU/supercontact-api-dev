from datetime import datetime
from enum import StrEnum
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserStatus(StrEnum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    PENDING = "Pending"


class UserLevel(StrEnum):
    STAFF = "Staff"
    MANAGER = "Manager"


class UserCreateRequest(BaseModel):
    fullname: str
    email: EmailStr

    role: str
    department: Optional[str] = None
    branch: Optional[str] = None

    user_level: UserLevel = UserLevel.STAFF
    employee_id: Optional[str] = None
    status: UserStatus = UserStatus.PENDING

    password: str = Field(..., min_length=6)


class UserUpdateRequest(BaseModel):
    fullname: Optional[str] = None
    email: Optional[EmailStr] = None

    role: Optional[str] = None
    department: Optional[str] = None
    branch: Optional[str] = None

    user_level: Optional[UserLevel] = None
    employee_id: Optional[str] = None
    status: Optional[UserStatus] = None

    password: Optional[str] = Field(default=None, min_length=6)


class UserResponse(BaseModel):
    id: UUID
    fullname: str
    email: EmailStr

    role_id: UUID
    department_id: Optional[UUID]
    branch_id: Optional[UUID]

    user_level: UserLevel
    employee_id: Optional[str]
    status: UserStatus

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserListResponse(BaseModel):
    total: int
    items: List[UserResponse]
