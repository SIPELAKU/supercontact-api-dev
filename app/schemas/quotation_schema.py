from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import EmailStr
from sqlmodel import Field, SQLModel

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
    page: int = 1
    limit: int = 10
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    search: Optional[str] = None
    quotation_status: Optional[List[QuotationStatus]] = None


class QuotationItemRequest(SQLModel):
    product_id: UUID
    quantity: int = Field(gt=0)
    notes: Optional[str]
    discount: int = Field(ge=0, le=25)


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


class QuotationSendEmailResponse(SQLModel):
    to_email: EmailStr
    subject: str
    delivered: bool
