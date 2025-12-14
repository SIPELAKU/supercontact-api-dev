from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from uuid import UUID, uuid4
from enum import StrEnum

from pydantic import ConfigDict
from sqlalchemy import Column, DateTime, ForeignKey, func, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.user_model import User
    from app.models.branch_model import Branch


def utc_now():
    from datetime import datetime, timezone

    return datetime.now(timezone.utc)


class DepartmentName(StrEnum):
    MARKETING = "Marketing"
    SALES = "Sales"
    ENGINEERING = "Engineering"
    HUMAN_RESOURCES = "Human Resources"
    CUSTOMER_SUPPORT = "Customer Support"


class Department(SQLModel, table=True):
    __tablename__ = "departments"
    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(PG_UUID(as_uuid=True), primary_key=True, index=True),
    )

    name: DepartmentName = Field(
        sa_column=Column(
            SAEnum(
                DepartmentName,
                values_callable=lambda e: [item.value for item in e],
                name="department_name_enum",
                native_enum=False,
            ),
            nullable=False,
            unique=True,
        )
    )

    manager_id: Optional[UUID] = Field(
        default=None,
        sa_column=Column(
            PG_UUID(as_uuid=True),
            ForeignKey("manage_users.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )

    manager: Mapped[Optional["User"]] = Relationship(
        back_populates="managed_department",
        sa_relationship_kwargs={"foreign_keys": "[Department.manager_id]"},
    )

    users: Mapped[List["User"]] = Relationship(
        back_populates="department",
        sa_relationship_kwargs={"foreign_keys": "[User.department_id]"},
    )

    branches: Mapped[List["Branch"]] = Relationship(
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
