from datetime import datetime, timezone
from enum import StrEnum
from typing import Optional
from uuid import UUID, uuid4

from pydantic import ConfigDict
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, DateTime, Text, String, Enum, Index, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID


class RoleEnum(StrEnum):
    SUPER_ADMIN = "Super_Admin"
    ADMIN = "Admin"
    TENANT_ADMIN = "Tenant_Admin"


class StatusEnum(StrEnum):
    active = "active"
    inactive = "inactive"


def utc_now():
    return datetime.now(timezone.utc)


class User(SQLModel, table=True):
    __tablename__ = "users"
    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(PG_UUID(as_uuid=True), primary_key=True, index=True),
    )

    fullname: str = Field(sa_column=Column(String(255), nullable=False))
    email: str = Field(sa_column=Column(String(255), unique=True, nullable=False))
    password: str = Field(sa_column=Column(Text, nullable=False))

    role: RoleEnum = Field(
        sa_column=Column(
            Enum(RoleEnum, name="user_role_enum", native_enum=False),
            nullable=False,
        )
    )

    status: StatusEnum = Field(
        default=StatusEnum.active,
        sa_column=Column(
            Enum(StatusEnum, name="status_enum", native_enum=False),
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

    __table_args__ = (
        Index("idx_user_fullname", "fullname"),
        Index("idx_user_email", "email"),
    )
