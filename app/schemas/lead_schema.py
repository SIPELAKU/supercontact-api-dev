from datetime import date
from datetime import datetime
from enum import StrEnum
from typing import List, Optional
from uuid import UUID

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
    page: int = 1,
    limit: int = 10,
    status: Optional[List[LeadStatus]] = None,
    source: Optional[List[LeadSource]] = None,
    assigned_to: Optional[UUID] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    search: Optional[str] = None,
    sort_order: SortOrder = SortOrder.DESC,


class LeadRequest(SQLModel):
    lead_name: str
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
    lead_name: str
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
    contact: Contact
    user: User


class LeadListResponse(SQLModel):
    total: int
    page: int
    total_pages: int
    leads: List[LeadResponse]
