from typing import Optional, List
from uuid import uuid4, UUID
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field, Relationship, Column, DateTime
from sqlalchemy import func


class UserDetail(SQLModel, table=True):
    __tablename__ = "user_details"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id")

    country: Optional[str] = Field(default=None)
    language: Optional[str] = Field(default=None)
    phone: Optional[str] = Field(default=None)
    skype: Optional[str] = Field(default=None)
    bio: Optional[str] = Field(default=None)

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