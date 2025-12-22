from uuid import UUID, uuid4
from typing import List, TYPE_CHECKING

from sqlalchemy import Column, String, UniqueConstraint, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlmodel import SQLModel, Field, Relationship

from app.models.department_enum import DepartmentEnum

if TYPE_CHECKING:
    from app.models.manage_user_model import ManageUser


class Branch(SQLModel, table=True):
    __tablename__ = "branches"

    __table_args__ = (
        UniqueConstraint(
            "department",
            "name",
            name="uq_department_branch",
        ),
    )

    id: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(
            PG_UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
        ),
    )

    name: str = Field(
        sa_column=Column(
            String(100),
            nullable=False,
        ),
    )

    department: DepartmentEnum = Field(
        sa_column=Column(
            SAEnum(
                DepartmentEnum,
                name="department_enum",
                native_enum=False,
                values_callable=lambda e: [i.value for i in e],
            ),
            nullable=False,
        ),
    )

    manage_users: List["ManageUser"] = Relationship(back_populates="branch")
