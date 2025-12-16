from datetime import datetime, timezone
from enum import StrEnum
from typing import List
from uuid import UUID, uuid4

from pydantic import ConfigDict
from sqlalchemy import Column, DateTime, func, Enum as SAEnum, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlmodel import SQLModel, Field, Relationship


def utc_now():
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
        )
    )
    branch: str = Field(sa_column=Column(String(50), nullable=False, unique=True))

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

    # RELATIONSHIP
    user_departments: List["ManageUser"] = Relationship(back_populates="department")
