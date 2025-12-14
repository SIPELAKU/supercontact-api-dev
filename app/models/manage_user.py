from datetime import datetime
from enum import StrEnum
from typing import Optional, TYPE_CHECKING
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
from sqlalchemy.orm import Mapped
from sqlmodel import Field, Relationship, SQLModel

from app.models.role_model import Role, utc_now

if TYPE_CHECKING:
    from app.models.department_model import Department
    from app.models.branch_model import Branch


class UserStatus(StrEnum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    PENDING = "Pending"


class UserLevel(StrEnum):
    STAFF = "Staff"
    MANAGER = "Manager"


class User(SQLModel, table=True):
    __tablename__ = "manage_users"
    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(PG_UUID(as_uuid=True), primary_key=True, index=True),
    )

    fullname: str = Field(sa_column=Column(String(255), nullable=False))
    email: str = Field(sa_column=Column(String(255), unique=True, nullable=False))
    password: str = Field(sa_column=Column(Text, nullable=False))

    role_id: UUID = Field(
        sa_column=Column(
            PG_UUID(as_uuid=True),
            ForeignKey("roles.id", ondelete="RESTRICT"),
            nullable=False,
        )
    )
    role: Mapped[Optional["Role"]] = Relationship(back_populates="users")

    department_id: Optional[UUID] = Field(
        default=None,
        sa_column=Column(
            PG_UUID(as_uuid=True),
            ForeignKey("departments.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )
    department: Mapped[Optional["Department"]] = Relationship(
        back_populates="users",
        sa_relationship_kwargs={"foreign_keys": "[User.department_id]"},
    )

    branch_id: Optional[UUID] = Field(
        default=None,
        sa_column=Column(
            PG_UUID(as_uuid=True),
            ForeignKey("branches.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )
    branch: Mapped[Optional["Branch"]] = Relationship(back_populates="users")

    managed_department: Mapped[Optional["Department"]] = Relationship(
        back_populates="manager",
        sa_relationship_kwargs={
            "foreign_keys": "[Department.manager_id]",
            "uselist": False,
        },
    )

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
        default_factory=utc_now,
        sa_column=Column(DateTime(timezone=True), server_default=func.now()),
    )

    updated_at: datetime = Field(
        default_factory=utc_now,
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),
        ),
    )

    __table_args__ = (
        Index("idx_user_fullname", "fullname"),
        Index("idx_user_email", "email"),
        Index("idx_user_department", "department_id"),
        Index("idx_user_branch", "branch_id"),
    )
