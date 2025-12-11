from datetime import datetime, timezone
from uuid import UUID, uuid4

from pydantic import ConfigDict
from sqlalchemy import Column, DateTime, String, Integer, Index
from sqlmodel import SQLModel, Field


class Quotation(SQLModel, table=True):
    __tablename__ = "products"
    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    lead_id: UUID = Field(foreign_key="leads.id", nullable=False)
    
    quotation_title: str = Field(sa_column=Column(String(255), nullable=False))
    expire_date: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False))
    grand_total: int = Field(sa_column=Column(Integer, nullable=False))

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
