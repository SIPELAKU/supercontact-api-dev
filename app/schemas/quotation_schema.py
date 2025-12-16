from datetime import datetime, date
from typing import List, Optional
from uuid import UUID

from fastapi import Query
from pydantic import EmailStr
from sqlmodel import SQLModel, Field

from app.models import QuotationStatus


class Product(SQLModel):
    product_name: str
    sku: str
    price: float


class User(SQLModel):
    id: UUID
    fullname: str
    email: EmailStr


class Contact(SQLModel):
    id: UUID
    name: str
    email: EmailStr
    phone: str
    company: str


class Lead(SQLModel):
    id: UUID
    office_location: str
    contact: Contact
    user: User


class QuotationGetQuery(SQLModel):
    page: int = Query(1, ge=1)
    limit: int = Query(10, ge=0, le=100)
    date_from: Optional[date] = Query(None)
    date_to: Optional[date] = Query(None)
    search: Optional[str] = Query(None)


class QuotationItemRequest(SQLModel):
    product_id: UUID
    quantity: int = Field(gt=0)
    notes: Optional[str]
    discount: int = Field(ge=0, le=100)


class QuotationRequest(SQLModel):
    lead_id: UUID
    quotation_title: str
    expire_date: datetime
    items: List[QuotationItemRequest]


class QuotationItemResponse(SQLModel):
    id: UUID
    quotation_id: UUID
    product_id: UUID
    quantity: int
    unit_price: int
    notes: Optional[str]
    discount: int
    product: Product


class QuotationResponse(SQLModel):
    id: UUID
    lead_id: UUID
    quotation_number: str
    quotation_title: str
    expire_date: datetime
    grand_total: int
    quotation_status: QuotationStatus
    lead: Lead
    items: List[QuotationItemResponse]
    created_at: datetime
    updated_at: datetime


class QuotationListResponse(SQLModel):
    total: int
    page: int
    total_pages: int
    quotations: List[QuotationResponse]


class QuotationDeleteResponse(SQLModel):
    id: UUID
    deleted: bool
