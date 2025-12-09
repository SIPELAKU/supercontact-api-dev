from datetime import date
from datetime import datetime
from enum import StrEnum
from typing import List, Optional
from uuid import UUID

from fastapi import Query
from pydantic import EmailStr
from sqlmodel import SQLModel

from app.models import LeadSource, LeadStatus, LeadIndustry, LeadCompanySize, LeadOfficeLocation, LeadTag


class Contact(SQLModel):
    id: UUID
    name: str
    email: EmailStr
    company: str
    phone: Optional[str]


class User(SQLModel):
    id: UUID
    fullname: str
    email: str


class SortOrder(StrEnum):
    ASC = "asc"
    DESC = "desc"


class LeadUpdateStatus(SQLModel):
    lead_status: LeadStatus


class LeadGetQuery(SQLModel):
    page: int = Query(1, ge=1)
    limit: int = Query(10, ge=1, le=100)
    lead_status: Optional[LeadStatus] = Query(None)
    lead_source: Optional[LeadSource] = Query(None)
    assigned_to: Optional[UUID] = Query(None)
    date_from: Optional[date] = Query(None)
    date_to: Optional[date] = Query(None)
    search: Optional[str] = Query(None)
    sort_order: SortOrder = Query(SortOrder.DESC)


class LeadRequest(SQLModel):
    lead_name: UUID
    industry: LeadIndustry
    company_size: LeadCompanySize
    office_location: LeadOfficeLocation
    lead_status: LeadStatus
    lead_source: LeadSource
    assigned_to: UUID
    tag: LeadTag
    notes: str


class LeadResponse(SQLModel):
    id: UUID
    lead_name: UUID
    industry: LeadIndustry
    company_size: LeadCompanySize
    office_location: LeadOfficeLocation
    lead_status: LeadStatus
    lead_source: LeadSource
    assigned_to: UUID
    tag: LeadTag
    notes: str
    created_at: datetime
    updated_at: datetime
    contact: Optional[Contact]
    user: Optional[User]


class LeadListResponse(SQLModel):
    total: int
    page: int
    total_pages: int
    leads: List[LeadResponse]
