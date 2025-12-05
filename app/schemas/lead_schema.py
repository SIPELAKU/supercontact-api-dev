from datetime import date
from datetime import datetime
from enum import StrEnum
from typing import List, Optional
from uuid import UUID

from sqlmodel import SQLModel

from app.models import LeadSource, LeadStatus


class User(SQLModel):
    id: UUID
    fullname: str
    email: str


class LeadSortBy(StrEnum):
    CREATED_AT = "created_at"
    LAST_CONTACTED = "last_contacted"


class SortOrder(StrEnum):
    ASC = "asc"
    DESC = "desc"


class LeadUpdateStatus(SQLModel):
    lead_status: LeadStatus


class LeadGetQuery(SQLModel):
    page: int = 1,
    limit: int = 10,
    status: Optional[List[LeadStatus]] = None,
    source: Optional[List[LeadSource]] = None,
    assigned_to: Optional[UUID] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    search: Optional[str] = None,
    sort_by: LeadSortBy = LeadSortBy.CREATED_AT,
    sort_order: SortOrder = SortOrder.DESC,


class LeadRequest(SQLModel):
    lead_name: str
    source: LeadSource
    contact: str
    status: LeadStatus
    assigned_to: UUID
    last_contacted: datetime


class LeadResponse(SQLModel):
    id: UUID
    lead_name: str
    source: LeadSource
    contact: str
    status: LeadStatus
    assigned_to: UUID
    last_contacted: datetime
    created_at: datetime
    updated_at: datetime
    user: User


class LeadListResponse(SQLModel):
    total: int
    page: int
    total_pages: int
    leads: List[LeadResponse]
