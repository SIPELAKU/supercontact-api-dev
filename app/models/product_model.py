from datetime import datetime, timezone
from enum import StrEnum
from uuid import UUID, uuid4

from pydantic import ConfigDict
from sqlalchemy import Column, DateTime, Enum, String, Numeric, Text
from sqlmodel import SQLModel, Field


# ENUM
class ProductTaxRate(StrEnum):
    STANDARD = "Standard (5%)"
    MEDIUM = "Medium (10%)"
    HIGH = "High (15%)"


class Product(SQLModel, table=True):
    __tablename__ = "products"
    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    product_name: str = Field(sa_column=Column(String(255), nullable=False))
    price: float = Field(le=1, sa_column=Column(Numeric(18, 2), nullable=False))
    sku: str = Field(sa_column=Column(String(20), nullable=False))
    tax_rate: ProductTaxRate = Field(
        sa_column=Column(
            Enum(
                ProductTaxRate,
                name="product_tax_rate_enum",
                native_enum=False,
                values_callable=lambda enum_cls: [enum.value for enum in enum_cls],
            ),
            nullable=False
        )
    )
    description: str = Field(sa_column=Column(Text, nullable=False))

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
