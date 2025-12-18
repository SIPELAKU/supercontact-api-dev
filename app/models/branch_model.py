from typing import List, TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import Column, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.department_model import Department
    from app.models.manage_user_model import ManageUser


class Branch(SQLModel, table=True):
    __tablename__ = "branches"

    __table_args__ = (
        UniqueConstraint("department_id", "name", name="uq_department_branch"),
    )

    id: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(PG_UUID(as_uuid=True), primary_key=True),
    )

    name: str = Field(sa_column=Column(String(100), nullable=False))

    department_id: UUID = Field(
        sa_column=Column(
            PG_UUID(as_uuid=True),
            ForeignKey("departments.id", ondelete="CASCADE"),
            nullable=False,
        )
    )

    department: "Department" = Relationship(back_populates="branches")
    manage_users: List["ManageUser"] = Relationship(back_populates="branch")
