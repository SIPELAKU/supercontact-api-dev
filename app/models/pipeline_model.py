from datetime import datetime, timezone
from enum import StrEnum
from typing import Optional
from uuid import UUID, uuid4

from pydantic import ConfigDict
from sqlalchemy import Column, DateTime, Enum, String, Text, Numeric, Integer, CheckConstraint
from sqlmodel import Relationship, SQLModel, Field

# ENUM
class DealStage(StrEnum):
    PROSPECT = "Prospect"
    QUALIFIED = "Qualified"
    NEGOTIATION = "Negotiation"
    PROPOSAL = "Proposal"


class Pipeline(SQLModel, table=True):
    __tablename__ = "pipelines"
    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    deal_name:str =Field(sa_column=Column(String(255), nullable=False))
    client_account: str=Field(sa_column=Column(String(255), nullable=False))

    deal_stage: DealStage = Field(
        sa_column=Column(
            Enum(
                DealStage,
                name="pipeline_deal_stage",
                native_enum=False,
                values_callable=lambda enum_cls: [enum.value for enum in enum_cls],
            ),
            nullable=False
        )
    )
    expected_close_date: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    amount:float = Field(sa_column=Column(Numeric(18,2), nullable=False))
    probability_of_close: int = Field(sa_column=Column(Integer, nullable=False))
    notes: Optional[str] = Field(sa_column=Column(Text, nullable=True))
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
        CheckConstraint("probability_of_close >= 0 AND probability_of_close <= 100"),
    )