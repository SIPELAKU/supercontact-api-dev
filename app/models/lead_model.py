from datetime import datetime, timezone
from enum import StrEnum
from typing import Optional
from uuid import UUID, uuid4

from pydantic import ConfigDict
from sqlalchemy import Column, DateTime, Enum, Index, Text
from sqlmodel import Relationship, SQLModel, Field


# ENUM
class LeadIndustry(StrEnum):
    MANUFAKTUR = "Manufaktur"
    TEKNOLOGI = "Teknologi"
    RITEL = "Ritel"
    FINANCE = "Finance"


class LeadCompanySize(StrEnum):
    SMALL = "1 - 50 Karyawan"
    MEDIUM = "51 - 200 Karyawan"
    LARGE = "201+ Karyawan"


class LeadOfficeLocation(StrEnum):
    JAKARTA = "DKI Jakarta"
    BANDUNG = "Bandung"
    YOGYAKARTA = "Yogyakarta"
    MALANG = "Malang"


class LeadTag(StrEnum):
    RENEWAL = "Renewal"
    URGENT = "Urgent"
    HIGH_VALUE = "High Value"
    TRIAL_USER = "Trial User"


class LeadSource(StrEnum):
    WEB_FORM = "Web Form"
    WHATSAPP = "WhatsApp"
    MANUAL = "Manual Entry"


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
    lead_name: UUID = Field(foreign_key="contacts.id", nullable=False)

    industry: LeadIndustry = Field(
        sa_column=Column(
            Enum(
                LeadIndustry,
                name="lead_industry_enum",
                native_enum=False,
                values_callable=lambda enum_cls: [enum.value for enum in enum_cls],
            ),
            nullable=False
        )
    )
    company_size: LeadCompanySize = Field(
        sa_column=Column(
            Enum(
                LeadCompanySize,
                name="lead_company_size_enum",
                native_enum=False,
                values_callable=lambda enum_cls: [enum.value for enum in enum_cls],
            ),
            nullable=False
        )
    )
    office_location: LeadOfficeLocation = Field(
        sa_column=Column(
            Enum(
                LeadOfficeLocation,
                name="lead_office_location_enum",
                native_enum=False,
                values_callable=lambda enum_cls: [enum.value for enum in enum_cls],
            ),
            nullable=False
        )
    )
    lead_status: LeadStatus = Field(
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
    lead_source: LeadSource = Field(
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
    assigned_to: UUID = Field(foreign_key="users.id")
    tag: LeadTag = Field(
        sa_column=Column(
            Enum(
                LeadTag,
                name="lead_tag_enum",
                native_enum=False,
                values_callable=lambda enum_cls: [enum.value for enum in enum_cls],
            ),
            nullable=False
        )
    )
    notes: str = Field(sa_column=Column(Text, nullable=True))

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
    contact: Optional["Contact"] = Relationship(back_populates="lead")

    __table_args__ = (
        Index("idx_lead_status", "lead_status"),
        Index("idx_lead_source", "lead_source"),
        Index("idx_lead_assigned_to", "assigned_to"),
        Index("idx_lead_created_at", "created_at"),
    )
