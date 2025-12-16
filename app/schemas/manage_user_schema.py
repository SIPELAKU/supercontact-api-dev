from datetime import datetime
from enum import StrEnum
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, EmailStr, ConfigDict


class UserStatus(StrEnum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    PENDING = "Pending"


class UserLevel(StrEnum):
    STAFF = "Staff"
    MANAGER = "Manager"


# REQUEST SCHEMAS


class UserCreateRequest(BaseModel):
    email: EmailStr

    role_id: UUID
    department_id: Optional[UUID] = None
    branch_id: Optional[UUID] = None

    user_level: UserLevel = UserLevel.STAFF
    employee_id: Optional[str] = None
    status: UserStatus = UserStatus.PENDING


# Update Manage User


class UserUpdateRequest(BaseModel):
    role_id: Optional[UUID] = None
    department_id: Optional[UUID] = None
    branch_id: Optional[UUID] = None

    user_level: Optional[UserLevel] = None
    employee_id: Optional[str] = None
    status: Optional[UserStatus] = None


# RESPONSE SCHEMAS


class UserResponse(BaseModel):
    id: UUID
    user_id: str

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


# DROPDOWN / HELPER SCHEMAS


class ManagerDropdown(BaseModel):
    id: UUID
    fullname: str

    model_config = ConfigDict(from_attributes=True)
