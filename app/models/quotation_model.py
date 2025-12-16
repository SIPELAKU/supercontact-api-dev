from datetime import datetime, timezone
from enum import StrEnum
from typing import List, Optional
from uuid import UUID, uuid4

from pydantic import ConfigDict
from sqlalchemy import Column, DateTime, String, Integer, Numeric, Text, Enum
from sqlalchemy.orm import relationship
from sqlmodel import SQLModel, Field, Relationship


class QuotationStatus(StrEnum):
    PENDING = "Pending"
    ACCEPTED = "Accepted"


class Quotation(SQLModel, table=True):
    __tablename__ = "quotations"
    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    lead_id: UUID = Field(foreign_key="leads.id", nullable=False)
    quotation_number: str = Field(sa_column=Column(String(10), nullable=False))
    quotation_title: str = Field(sa_column=Column(String(255), nullable=False))
    expire_date: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False))
    grand_total: float = Field(le=1, sa_column=Column(Numeric(18, 2), nullable=False))
    quotation_status: QuotationStatus = Field(
        sa_column=Column(
            Enum(
                QuotationStatus,
                name="quotation_status_enum",
                native_enum=False,
                values_callable=lambda enum_cls: [enum.value for enum in enum_cls]
            ),
            nullable=False,
            server_default=QuotationStatus.PENDING,
        )
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

    lead: "Lead" = Relationship(back_populates="quotations")
    items: List["QuotationItem"] = Relationship(
        back_populates="quotation",
        sa_relationship=relationship(
            "QuotationItem",
            back_populates="quotation",
            cascade="all, delete-orphan",
            passive_deletes=True
        )
    )


class QuotationItem(SQLModel, table=True):
    __tablename__ = "quotation_items"

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    quotation_id: UUID = Field(foreign_key="quotations.id", nullable=False)
    product_id: UUID = Field(foreign_key="products.id", nullable=False)

    quantity: int = Field(sa_column=Column(Integer, nullable=False))
    unit_price: float = Field(le=1, sa_column=Column(Numeric(18, 2), nullable=False))
    notes: Optional[str] = Field(sa_column=Column(Text, nullable=True))
    discount: int = Field(ge=0, le=100, default=0)

    quotation: "Quotation" = Relationship(back_populates="items")
    product: "Product" = Relationship(back_populates="quotation_items")
