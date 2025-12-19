from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4, UUID

from sqlmodel import SQLModel, Field, Relationship, Column, DateTime, Text, String


class UserDetail(SQLModel, table=True):
    __tablename__ = "user_details"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id")

    fullname: str = Field(sa_column=Column(String(255), nullable=False))
    email: str = Field(sa_column=Column(String(255), unique=True, nullable=False))
    company: str = Field(sa_column=Column(String(255), nullable=False))
    country: Optional[str] = Field(sa_column=Column(String(255), nullable=False))
    language: Optional[str] = Field(sa_column=Column(String(255), nullable=False))
    phone: Optional[str] = Field(sa_column=Column(String(255), nullable=False))
    skype: Optional[str] = Field(sa_column=Column(String(255), nullable=False))
    bio: Optional[str] = Field(sa_column=Column(Text, nullable=False))

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
    user: "User" = Relationship(back_populates="detail")
