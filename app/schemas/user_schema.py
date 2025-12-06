from datetime import datetime
from typing import List
from uuid import UUID

from sqlmodel import SQLModel

# from app.models import UserRole


class Lead(SQLModel):
    id: UUID
    lead_name: str


class UserResponse(SQLModel):
    id: UUID
    fullname: str
    email: str
    # role: UserRole
    created_at: datetime
    updated_at: datetime
    leads: List[Lead]


class UserListResponse(SQLModel):
    total: int
    users: List[UserResponse]
