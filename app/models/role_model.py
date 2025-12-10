from datetime import datetime, timezone
from typing import List
from uuid import UUID, uuid4
from pydantic import ConfigDict
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, String, DateTime, func, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID


def utc_now():
    return datetime.now(timezone.utc)


class RolePermission(SQLModel, table=True):
    __tablename__ = "role_permission"
    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(
        default_factory=uuid4, sa_column=Column(PG_UUID(as_uuid=True), primary_key=True)
    )
    role_id: UUID = Field(
        sa_column=Column(
            PG_UUID(as_uuid=True),
            ForeignKey("roles.id", ondelete="CASCADE"),
            nullable=False,
        )
    )
    permission_id: UUID = Field(
        sa_column=Column(
            PG_UUID(as_uuid=True),
            ForeignKey("permissions.id", ondelete="CASCADE"),
            nullable=False,
        )
    )
    created_at: datetime = Field(
        default_factory=utc_now,
        sa_column=Column(DateTime(timezone=True), server_default=func.now()),
    )


class Role(SQLModel, table=True):
    __tablename__ = "roles"
    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(
        default_factory=uuid4, sa_column=Column(PG_UUID(as_uuid=True), primary_key=True)
    )
    role_name: str = Field(sa_column=Column(String(255), unique=True, nullable=False))
    is_system_role: bool = Field(default=False)

    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    updated_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
        )
    )

    users: List["User"] = Relationship(back_populates="role")
    permissions: List["Permission"] = Relationship(
        back_populates="roles", link_model=RolePermission
    )


class Permission(SQLModel, table=True):
    __tablename__ = "permissions"
    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(
        default_factory=uuid4, sa_column=Column(PG_UUID(as_uuid=True), primary_key=True)
    )
    permission_name: str = Field(sa_column=Column(String(255), nullable=False))
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    updated_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
        )
    )

    roles: List["Role"] = Relationship(
        back_populates="permissions", link_model=RolePermission
    )
