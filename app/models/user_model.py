from datetime import datetime, timezone
from enum import StrEnum
from typing import List
from typing import Optional
from uuid import UUID, uuid4

from pydantic import ConfigDict
from sqlalchemy import Column, DateTime, Text, String, Enum, Index, func
from sqlmodel import SQLModel, Field, Relationship


class UserRole(StrEnum):
    SALES = "Sales"
    SUPER_ADMIN = "Super Admin"
    ADMIN = "Admin"
    TENANT_ADMIN = "Tenant Admin"


class UserStatus(StrEnum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"


def utc_now():
    return datetime.now(timezone.utc)


class User(SQLModel, table=True):
    __tablename__ = "users"
    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    fullname: str = Field(sa_column=Column(String(255), nullable=False))
    email: str = Field(sa_column=Column(String(255), unique=True, nullable=False))
    password: str = Field(sa_column=Column(Text, nullable=False))

    role: UserRole = Field(
        sa_column=Column(
            Enum(
                UserRole,
                name="user_role_enum",
                values_callable=lambda enum_cls: [enum.value for enum in enum_cls],
                native_enum=False
            ),
            nullable=False,
        )
    )

    status: UserStatus = Field(
        default=UserStatus.ACTIVE,
        sa_column=Column(
            Enum(
                UserStatus,
                name="status_enum",
                values_callable=lambda enum_cls: [enum.value for enum in enum_cls],
                native_enum=False
            ),
            nullable=False,
        ),
    )

    avatar_initial: Optional[str] = Field(
        default=None,
        sa_column=Column(String(255), nullable=True),
    )

    created_at: datetime = Field(
        default_factory=utc_now,
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
        ),
    )

    updated_at: datetime = Field(
        default_factory=utc_now,
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
            onupdate=func.now(),
        ),
    )
    leads: List["Lead"] = Relationship(back_populates="user")

    __table_args__ = (
        Index("idx_user_fullname", "fullname"),
        Index("idx_user_email", "email"),
    )
