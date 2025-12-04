from datetime import datetime, timezone
from enum import StrEnum
from typing import List
from uuid import UUID, uuid4

from pydantic import ConfigDict
from sqlalchemy import Column, DateTime, Text, String, Enum, Index
from sqlmodel import SQLModel, Field, Relationship


class UserRole(StrEnum):
    SALES = "Sales"
    ADMIN = "Admin"


class User(SQLModel, table=True):
    __tablename__ = "users"
    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    fullname: str = Field(sa_column=Column(String(255), nullable=False))
    email: str = Field(sa_column=Column(String(255), unique=True))
    password: str = Field(sa_column=Column(Text, nullable=False))
    role: UserRole = Field(
        sa_column=Column(
            Enum(
                UserRole,
                name="user_role_enum",
                values_callable=lambda enum_cls: [enum.value for enum in enum_cls],
                native_enum=False,
            ),
            nullable=False
        )
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )

    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            onupdate=lambda: datetime.now(timezone.utc),
        ),
    )
    leads: List["Lead"] = Relationship(back_populates="user")

    __table_args__ = (
        Index("idx_user_fullname", "fullname"),
        Index("idx_user_email", "email"),
    )
