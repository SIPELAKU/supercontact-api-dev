from datetime import datetime, timezone
from enum import StrEnum
from typing import List
from uuid import UUID, uuid4

from pydantic import ConfigDict
from sqlalchemy import Column, DateTime, Text, String, Enum, Index, func
from sqlmodel import SQLModel, Field, Relationship

from app.models import UserTaskLink


class UserPosition(StrEnum):
    BUSINESS_OWNER = "Business Owner"
    C_LEVEL = "C-Level"
    SENIOR_MANAGER = "Senior Manager"
    STAFF = "Staff"
    OTHER = "Lainnya"


def utc_now():
    return datetime.now(timezone.utc)


class User(SQLModel, table=True):
    __tablename__ = "users"
    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    fullname: str = Field(sa_column=Column(String(255), nullable=False))
    email: str = Field(sa_column=Column(String(255), unique=True, nullable=False))
    phone: str = Field(sa_column=Column(String(255), nullable=False))
    company: str = Field(sa_column=Column(String(255), nullable=False))
    position: UserPosition = Field(
        sa_column=Column(
            Enum(
                UserPosition,
                name="user_position_enum",
                values_callable=lambda enum_cls: [enum.value for enum in enum_cls],
                native_enum=False
            ),
            nullable=False,
        ),
    )
    password: str = Field(sa_column=Column(Text, nullable=False))

    avatar_initial: str = Field(sa_column=Column(String(2), nullable=False))

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
    pipelines: List["Pipeline"] = Relationship(back_populates="user")
    contacts: List["Contact"] = Relationship(back_populates="user")
    contact_tasks: List["ContactTask"] = Relationship(
        back_populates="users", link_model=UserTaskLink
    )
    detail: List["UserDetail"] = Relationship(back_populates="user")
    manage_user: "ManageUser" = Relationship(back_populates="user")

    __table_args__ = (
        Index("idx_user_fullname", "fullname"),
        Index("idx_user_email", "email"),
    )
