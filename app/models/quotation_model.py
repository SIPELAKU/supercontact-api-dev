from datetime import datetime, timezone
from typing import List
from uuid import UUID, uuid4

from pydantic import ConfigDict
from sqlalchemy import Column, DateTime, String, Integer, Numeric, Text
from sqlmodel import SQLModel, Field, Relationship


class Quotation(SQLModel, table=True):
    __tablename__ = "quotations"
    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    lead_id: UUID = Field(foreign_key="leads.id", nullable=False)
    quotation_title: str = Field(sa_column=Column(String(255), nullable=False))
    expire_date: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False))
    grand_total: float = Field(le=1, sa_column=Column(Numeric(18, 2), nullable=False))

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
    items: List["QuotationItem"] = Relationship(back_populates="quotation")


class QuotationItem(SQLModel, table=True):
    __tablename__ = "quotation_items"

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    quotation_id: UUID = Field(foreign_key="quotations.id", nullable=False)
    product_id: UUID = Field(foreign_key="products.id", nullable=False)

    quantity: int = Field(sa_column=Column(Integer, nullable=False))
    unit_price: float = Field(le=1, sa_column=Column(Numeric(18, 2), nullable=False))
    subtotal: float = Field(le=1, sa_column=Column(Numeric(18, 2), nullable=False))
    notes: str = Field(sa_column=Column(Text, nullable=False))

    quotation: "Quotation" = Relationship(back_populates="items")
    product: "Product" = Relationship()
