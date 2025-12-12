from datetime import datetime
from enum import StrEnum
from typing import List
from uuid import UUID

from sqlmodel import SQLModel


class Product(SQLModel):
    product_name: str
    sku: str
    price: float


class Contact(SQLModel):
    id: int
    name: str
    email: str
    phone: str
    company: str


class LeadOfficeLocation(StrEnum):
    JAKARTA = "DKI Jakarta"
    BANDUNG = "Bandung"
    YOGYAKARTA = "Yogyakarta"
    MALANG = "Malang"


class Lead(SQLModel):
    id: UUID
    office_location: LeadOfficeLocation
    contact: Contact


class QuotationItemRequest(SQLModel):
    quotation_id: UUID
    product_id: UUID
    quantity: int
    unit_price: float
    subtotal: float
    notes: str


class QuotationRequest(SQLModel):
    lead_id: UUID
    quotation_title: str
    expire_date: datetime
    grand_total: float
    items: List[QuotationItemRequest]


class QuotationItemResponse(SQLModel):
    id: UUID
    quotation_id: UUID
    product_id: UUID
    quantity: int
    unit_price: float
    subtotal: float
    notes: str
    product: Product


class QuotationResponse(SQLModel):
    id: UUID
    lead_id: UUID
    quotation_title: str
    expire_date: datetime
    grand_total: float
    lead: Lead
    items: List[QuotationItemResponse]
    created_at: datetime
    updated_at: datetime
