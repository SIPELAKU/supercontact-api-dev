from datetime import datetime
from typing import List
from typing import Optional
from uuid import UUID

from fastapi import Query
from pydantic import EmailStr
from sqlmodel import SQLModel, Field

from app.models import DealStage


class PipelineUpdateStage(SQLModel):
    deal_stage: DealStage


class Metric(SQLModel):
    value: int
    percent: int
    trend: str


class PipelineStats(SQLModel):
    total_pipeline: Metric
    avg_pipeline: Metric
    winrate_pipeline: Metric


class User(SQLModel):
    id: UUID
    fullname: str
    email: EmailStr


class Contact(SQLModel):
    id: UUID
    name: str
    company: str


class PipelineGetQuery(SQLModel):
    deal_stage: Optional[DealStage] = Query(None)
    date_from: Optional[datetime] = Query(None)
    date_to: Optional[datetime] = Query(None)
    search: Optional[str] = Query(None)


class PipelineRequest(SQLModel):
    deal_name: str
    client_account: UUID
    deal_stage: DealStage
    expected_close_date: datetime
    amount: float = Field(ge=1)
    probability_of_close: int = Field(ge=1, le=100)
    notes: Optional[str] = None


class PipelineResponse(SQLModel):
    id: UUID
    deal_name: str
    client_account: UUID
    deal_stage: DealStage
    expected_close_date: datetime
    amount: float
    probability_of_close: int
    notes: Optional[str]
    assigned_to: UUID
    is_deleted: bool
    created_at: datetime
    updated_at: datetime
    user: User
    contact: Contact


class PipelineListResponse(SQLModel):
    total: int
    stats: PipelineStats
    pipelines: List[PipelineResponse]


class PipelineActiveUser(SQLModel):
    id: UUID
    fullname: str
    active_pipeline_count: int


class PipelineAssignedUsers(SQLModel):
    total: int
    users: List[PipelineActiveUser]
