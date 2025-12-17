from datetime import datetime, timezone
from typing import List
from uuid import UUID, uuid4

from pydantic import ConfigDict
from sqlalchemy import Column, DateTime, String, Numeric, Text, Index
from sqlmodel import SQLModel, Field, Relationship


class Product(SQLModel, table=True):
    __tablename__ = "products"
    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    product_name: str = Field(sa_column=Column(String(255), nullable=False))
    price: float = Field(le=1, sa_column=Column(Numeric(18, 2), nullable=False))
    sku: str = Field(sa_column=Column(String(20), nullable=False))
    description: str = Field(sa_column=Column(Text, nullable=False))
    quotation_items: List["QuotationItem"] = Relationship(back_populates="product")

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

    __table_args__ = (
        Index("idx_product_product_name", "product_name"),
        Index("idx_product_sku", "sku"),
    )
