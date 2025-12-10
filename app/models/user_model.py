from datetime import datetime
from enum import StrEnum
from typing import Optional
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

from app.models.role_model import Role, utc_now


class UserStatus(StrEnum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    PENDING = "Pending"


class User(SQLModel, table=True):
    __tablename__ = "users"
    model_config = ConfigDict(from_attributes=True)

    # Primary Key
    id: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(PG_UUID(as_uuid=True), primary_key=True, index=True),
    )

    # Basic Fields
    fullname: str = Field(sa_column=Column(String(255), nullable=False))

    email: str = Field(sa_column=Column(String(255), unique=True, nullable=False))

    password: str = Field(sa_column=Column(Text, nullable=False))

    # Role Relationship
    role_id: UUID = Field(
        sa_column=Column(
            PG_UUID(as_uuid=True),
            ForeignKey("roles.id", ondelete="RESTRICT"),
            nullable=False,
        )
    )

    role: Optional["Role"] = Relationship(back_populates="users")

    # User Status
    status: UserStatus = Field(
        default=UserStatus.PENDING,
        sa_column=Column(
            SAEnum(
                UserStatus,
                values_callable=lambda enum_cls: [e.value for e in enum_cls],
                name="user_status_enum",
                native_enum=False,
            ),
            nullable=False,
        ),
    )

    # Avatar initials (optional)
    avatar_initial: Optional[str] = Field(
        default=None,
        sa_column=Column(String(10), nullable=True),
    )

    # Timestamps
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

    # Indexing for performance
    __table_args__ = (
        Index("idx_user_fullname", "fullname"),
        Index("idx_user_email", "email"),
    )
