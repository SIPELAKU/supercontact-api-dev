from datetime import datetime, timezone
from enum import StrEnum
from typing import Optional
from uuid import UUID, uuid4

from pydantic import ConfigDict
from sqlalchemy import Column, DateTime, Enum, String, Index
from sqlmodel import Relationship, SQLModel, Field


# ENUM
class LeadSource(StrEnum):
    WEB_FORM = "Web Form"
    WHATSAPP = "Whatsapp"
    MANUAL = "Manual"


class LeadStatus(StrEnum):
    NEW = "New"
    CONTACTED = "Contacted"
    QUALIFIED = "Qualified"
    PROPOSAL = "Proposal"
    CLOSED_WON = "Closed Won"
    CLOSED_LOST = "Closed Lost"


class Lead(SQLModel, table=True):
    __tablename__ = "leads"
    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    lead_name: str = Field(sa_column=Column(String(255), nullable=False))
    source: LeadSource = Field(
        sa_column=Column(
            Enum(
                LeadSource,
                name="lead_source_enum",
                native_enum=False,
                values_callable=lambda enum_cls: [enum.value for enum in enum_cls],
            ),
            nullable=False
        )
    )
    contact: str = Field(sa_column=Column(String(30), nullable=False))
    status: LeadStatus = Field(
        sa_column=Column(
            Enum(
                LeadStatus,
                name="lead_status_enum",
                native_enum=False,
                values_callable=lambda enum_cls: [enum.value for enum in enum_cls],
            ),
            nullable=False
        ),
        default=LeadStatus.NEW,
    )
    assigned_to: UUID = Field(foreign_key="users.id")
    last_contacted: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
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
    user: Optional["User"] = Relationship(back_populates="leads")

    __table_args__ = (
        Index("idx_lead_status", "status"),
        Index("idx_lead_source", "source"),
        Index("idx_lead_assigned_to", "assigned_to"),
        Index("idx_lead_created_at", "created_at"),
    )
