from datetime import datetime
from enum import StrEnum
from typing import List, Optional
from uuid import UUID

from pydantic import EmailStr
from sqlmodel import SQLModel

from app.models import LeadSource, LeadStatus, LeadIndustry, LeadCompanySize, LeadTag


class ContactNote(SQLModel):
    id: UUID
    note: str
    created_at: datetime


class Contact(SQLModel):
    id: UUID
    name: str
    email: EmailStr
    company: str
    phone: Optional[str]
    last_contacted: Optional[ContactNote]


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
    page: int = 1
    limit: int = 10
    lead_status: Optional[List[LeadStatus]] = None
    lead_source: Optional[List[LeadSource]] = None
    assigned_to: Optional[List[UUID]] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    search: Optional[str] = None
    sort_order: SortOrder = SortOrder.DESC


class LeadRequest(SQLModel):
    contact_id: UUID
    industry: LeadIndustry
    company_size: LeadCompanySize
    office_location: str
    lead_status: LeadStatus
    lead_source: LeadSource
    assigned_to: UUID
    tag: LeadTag
    notes: Optional[str]


class LeadResponse(SQLModel):
    id: UUID
    contact_id: UUID
    industry: LeadIndustry
    company_size: LeadCompanySize
    office_location: str
    lead_status: LeadStatus
    lead_source: LeadSource
    assigned_to: UUID
    tag: LeadTag
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    contact: Optional[Contact]
    user: Optional[User]


class LeadListResponse(SQLModel):
    total: int
    page: int
    total_pages: int
    leads: List[LeadResponse]


class LeadDeleteResponse(SQLModel):
    id: UUID
    deleted: bool
