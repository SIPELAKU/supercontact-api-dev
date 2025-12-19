from sqlalchemy import Column, Date, String
from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID, uuid4
from typing import Optional
from datetime import date, datetime, timezone
from sqlalchemy import DateTime


class Mailing(SQLModel, table=True):
    __tablename__ = "mailings"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id")

    subject: str = Field(sa_column=Column(String(255), nullable=False))
    status: str = Field(sa_column=Column(String(255), nullable=False))
    send_date: date = Field(sa_column=Column(Date(), nullable=False))
    statistic: str = Field(sa_column=Column(String(255), nullable=False))
    created_by: datetime = Field(
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

    user: Optional["User"] = Relationship(back_populates="mailings")