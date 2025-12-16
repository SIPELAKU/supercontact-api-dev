from datetime import datetime
from enum import StrEnum
from typing import Optional
from uuid import UUID, uuid4

from pydantic import ConfigDict
from sqlalchemy import (
    Column,
    DateTime,
    Enum as SAEnum,
    Index,
    String,
    func,
)
from sqlmodel import Field, Relationship, SQLModel


# ==================================================
# ENUMS
# ==================================================
class UserStatus(StrEnum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    PENDING = "Pending"


class UserLevel(StrEnum):
    STAFF = "Staff"
    MANAGER = "Manager"


# MANAGE USER
class ManageUser(SQLModel, table=True):
    __tablename__ = "manage_users"
    model_config = ConfigDict(from_attributes=True)

    # PRIMARY KEY
    id: UUID = Field(default_factory=uuid4, primary_key=True)

    user_id: UUID = Field(foreign_key="users.id", nullable=False)
    department_id: UUID = Field(foreign_key="departments.id", nullable=False)
    role_id: UUID = Field(foreign_key="roles.id", nullable=False)
    user_level: UserLevel = Field(
        sa_column=Column(
            SAEnum(
                UserLevel,
                values_callable=lambda e: [item.value for item in e],
                name="user_level_enum",
                native_enum=False,
            ),
            nullable=False,
            server_default=UserLevel.STAFF,
        ),
    )
    status: UserStatus = Field(
        sa_column=Column(
            SAEnum(
                UserStatus,
                values_callable=lambda e: [item.value for item in e],
                name="user_status_enum",
                native_enum=False,
            ),
            nullable=False,
            server_default=UserStatus.PENDING,
        ),
    )

    employee_id: Optional[str] = Field(
        default=None,
        sa_column=Column(String(20), unique=True),
    )

    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    updated_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),
        )
    )

    # RELATIONSHIP
    role: "Role" = Relationship(back_populates="manage_users")
    department: "Department" = Relationship(back_populates="user_departments")
    user: "User" = Relationship(back_populates="manage_user")

    def is_active(self) -> bool:
        return self.status == UserStatus.ACTIVE

    def is_manager(self) -> bool:
        return self.user_level == UserLevel.MANAGER

    __table_args__ = (
        Index("idx_manage_user_user_id", "user_id"),
        Index("idx_manage_user_department", "department_id"),
    )
