from datetime import datetime
from enum import StrEnum
from typing import Optional, List
from uuid import UUID, uuid4

from pydantic import ConfigDict
from sqlalchemy import (
    Column,
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    Index,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlmodel import Field, Relationship, SQLModel

from app.models import UserTaskLink


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


# USER
class User(SQLModel, table=True):
    __tablename__ = "manage_users"
    model_config = ConfigDict(from_attributes=True)

    # PRIMARY KEY
    id: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(PG_UUID(as_uuid=True), primary_key=True, index=True),
    )

    # USER ID (EXTERNAL IDENTIFIER)
    user_id: str = Field(
        sa_column=Column(
            String(50),
            nullable=False,
            unique=True,
            index=True,
        )
    )

    # ROLE
    role_id: UUID = Field(
        sa_column=Column(
            PG_UUID(as_uuid=True),
            ForeignKey("roles.id", ondelete="RESTRICT"),
            nullable=False,
        )
    )
    role: "Role" = Relationship(back_populates="users")

    # DEPARTMENT
    department_id: Optional[UUID] = Field(
        default=None,
        sa_column=Column(
            PG_UUID(as_uuid=True),
            ForeignKey("departments.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )
    department: Optional["Department"] = Relationship(
        back_populates="users",
        sa_relationship_kwargs={"foreign_keys": "[User.department_id]"},
    )

    # BRANCH
    branch_id: Optional[UUID] = Field(
        default=None,
        sa_column=Column(
            PG_UUID(as_uuid=True),
            ForeignKey("branches.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )
    branch: Optional["Branch"] = Relationship(back_populates="users")

    # MANAGED DEPARTMENT
    managed_department: Optional["Department"] = Relationship(
        back_populates="manager",
        sa_relationship_kwargs={
            "foreign_keys": "[Department.manager_id]",
            "uselist": False,
        },
    )

    # USER LEVEL
    user_level: UserLevel = Field(
        default=UserLevel.STAFF,
        sa_column=Column(
            SAEnum(
                UserLevel,
                values_callable=lambda e: [item.value for item in e],
                name="user_level_enum",
                native_enum=False,
            ),
            nullable=False,
        ),
    )

    employee_id: Optional[str] = Field(
        default=None,
        sa_column=Column(String(20), unique=True),
    )

    status: UserStatus = Field(
        default=UserStatus.PENDING,
        sa_column=Column(
            SAEnum(
                UserStatus,
                values_callable=lambda e: [item.value for item in e],
                name="user_status_enum",
                native_enum=False,
            ),
            nullable=False,
        ),
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

    leads: List["Lead"] = Relationship(back_populates="user")

    pipelines: List["Pipeline"] = Relationship(back_populates="user")

    contacts: List["Contact"] = Relationship(back_populates="user")

    contact_tasks: List["ContactTask"] = Relationship(
        back_populates="users",
        link_model=UserTaskLink,
    )

    details: List["UserDetail"] = Relationship(back_populates="user")

    def is_active(self) -> bool:
        return self.status == UserStatus.ACTIVE

    def is_manager(self) -> bool:
        return self.user_level == UserLevel.MANAGER

    def has_department(self) -> bool:
        return self.department_id is not None

    __table_args__ = (
        Index("idx_user_user_id", "user_id"),
        Index("idx_user_department", "department_id"),
        Index("idx_user_branch", "branch_id"),
    )
