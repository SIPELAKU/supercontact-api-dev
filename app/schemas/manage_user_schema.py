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
    SUPERVISOR = "Supervisor"
    MANAGER = "Manager"


class Position(StrEnum):
    SUPPORT_AGENT = "Support Agent"
    FRONTEND_ENGINEER = "Frontend Engineer"
    HR_GENERALIST = "HR Generalist"
    CONTENT_SPECIALIST = "Content Specialist"
    SALES_DEVELOPMENT = "Sales Development"


# CREATE
class ManageUserCreateRequest(BaseModel):

    email: EmailStr

    department: Optional[str] = None
    branch: Optional[str] = None
    role: Optional[str] = None

    user_level: Optional[UserLevel] = None
    position: Optional[Position] = None
    status: Optional[UserStatus] = None


# UPDATE
class ManageUserUpdateRequest(BaseModel):

    department: str
    branch: str
    role: Optional[str]

    user_level: UserLevel
    position: Optional[Position]
    status: UserStatus


class ManageUserResponse(BaseModel):
    id: UUID
    user_id: UUID

    fullname: str
    email: EmailStr

    role: Optional[str]
    department: Optional[str]
    branch: Optional[str]

    user_level: UserLevel
    position: Optional[Position]

    employee_id: Optional[str]
    status: UserStatus

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ManageUserListResponse(BaseModel):
    total: int
    items: List[ManageUserResponse]
