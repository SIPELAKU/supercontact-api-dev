from datetime import datetime
from typing import List, TYPE_CHECKING
from uuid import UUID, uuid4

from pydantic import ConfigDict
from sqlalchemy import Column, DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.manage_user_model import ManageUser
    from app.models.branch_model import Branch


def utc_now():
    from datetime import datetime, timezone

    return datetime.now(timezone.utc)


class Department(SQLModel, table=True):
    __tablename__ = "departments"
    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(PG_UUID(as_uuid=True), primary_key=True, index=True),
    )

    name: str = Field(sa_column=Column(String(100), nullable=False))

    manage_users: List["ManageUser"] = Relationship(back_populates="department")

    branches: List["Branch"] = Relationship(
        back_populates="department",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )

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
