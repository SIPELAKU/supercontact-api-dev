from datetime import datetime, date, time, timezone
from typing import Optional, List
from uuid import UUID, uuid4

from sqlalchemy import Column, String, Date, DateTime, Time
from sqlmodel import Relationship, SQLModel, Field


class Note(SQLModel, table=True):
    __tablename__ = "notes"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id")

    title: str = Field(sa_column=Column(String(255), nullable=False))
    content: str = Field(sa_column=Column(String(255), nullable=False))
    reminder_date: date = Field(sa_column=Column(Date(), nullable=False))
    reminder_time: time = Field(sa_column=Column(Time(), nullable=False))

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False
        ),
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            onupdate=lambda: datetime.now(timezone.utc),
        ),
    )

    user: "User" = Relationship(back_populates="notes")