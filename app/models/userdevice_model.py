from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field, Relationship, DateTime, Column, String


class UserDevice(SQLModel, table=True):
    __tablename__ = "user_devices"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)

    browser: str = Field(sa_column=Column(String(255), nullable=False))
    device: str = Field(sa_column=Column(String(255), nullable=False))
    location: Optional[str] = Field(sa_column=Column(String(255), nullable=True))

    last_activity: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False))

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

    user: "User" = Relationship(back_populates="device")
