from datetime import date
from datetime import datetime
from typing import List
from typing import Optional
from uuid import UUID

from fastapi import Query
from sqlmodel import SQLModel

from app.models import DealStage


class PipelineUpdateStage(SQLModel):
    deal_stage: DealStage


class PipelineGetQuery(SQLModel):
    page: int = Query(1, ge=1)
    limit: int = Query(10, ge=1, le=100)
    deal_stage: Optional[DealStage] = Query(None)
    date_from: Optional[date] = Query(None)
    date_to: Optional[date] = Query(None)
    search: Optional[str] = Query(None)


class PipelineRequest(SQLModel):
    deal_name: str
    client_account: str
    deal_stage: DealStage
    expected_close_date: datetime
    amount: float
    probability_of_close: int
    notes: Optional[str] = None


class PipelineResponse(SQLModel):
    id: UUID
    deal_name: str
    client_account: str
    deal_stage: DealStage
    expected_close_date: datetime
    amount: float
    probability_of_close: int
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime


class PipelineListResponse(SQLModel):
    total: int
    page: int
    total_pages: int
    pipelines: List[PipelineResponse]
