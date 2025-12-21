from datetime import datetime
from enum import StrEnum
from typing import Optional, TYPE_CHECKING
from uuid import UUID, uuid4

from pydantic import ConfigDict
from sqlalchemy import (
    Column,
    DateTime,
    Enum as SAEnum,
    Index,
    String,
    func,
    text,
)
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.user_model import User
    from app.models.role_model import Role
    from app.models.branch_model import Branch
    from app.models.department_enum import DepartmentEnum


# ENUMS
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


class ManageUser(SQLModel, table=True):

    __tablename__ = "manage_users"
    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    user_id: UUID = Field(
        foreign_key="users.id",
        nullable=False,
    )

    branch_id: Optional[UUID] = Field(
        default=None,
        foreign_key="branches.id",
        nullable=True,
    )

    role_id: Optional[UUID] = Field(
        default=None,
        foreign_key="roles.id",
        nullable=True,
    )

    user_level: UserLevel = Field(
        sa_column=Column(
            SAEnum(
                UserLevel,
                values_callable=lambda e: [i.value for i in e],
                name="user_level_enum",
                native_enum=False,
            ),
            nullable=False,
            server_default=text("'Staff'"),
        )
    )

    position: Optional[Position] = Field(
        default=None,
        sa_column=Column(
            SAEnum(
                Position,
                values_callable=lambda e: [i.value for i in e],
                name="user_position_enum",
                native_enum=False,
            ),
            nullable=True,
        ),
    )

    status: UserStatus = Field(
        sa_column=Column(
            SAEnum(
                UserStatus,
                values_callable=lambda e: [i.value for i in e],
                name="user_status_enum",
                native_enum=False,
            ),
            nullable=False,
            server_default=text("'Pending'"),
        )
    )

    employee_id: Optional[str] = Field(
        default=None,
        sa_column=Column(String(20), unique=True),
    )

    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
        )
    )

    updated_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),
        )
    )

    user: "User" = Relationship(back_populates="manage_user")
    branch: Optional["Branch"] = Relationship(back_populates="manage_users")
    role: Optional["Role"] = Relationship(back_populates="manage_users")

    @property
    def department(self) -> Optional["DepartmentEnum"]:

        return self.branch.department if self.branch else None

    __table_args__ = (
        Index("idx_manage_user_user_id", "user_id"),
        Index("idx_manage_user_branch_id", "branch_id"),
    )
