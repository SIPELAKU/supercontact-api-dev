from datetime import datetime
from enum import StrEnum
from typing import List, Optional
from uuid import UUID

from fastapi import Query
from sqlmodel import SQLModel


class SortOrder(StrEnum):
    ASC = "asc"
    DESC = "desc"


class ProductGetQuery(SQLModel):
    page: int = Query(1, ge=1)
    limit: int = Query(10, ge=0, le=100)
    search: Optional[str] = Query(None)


class ProductRequest(SQLModel):
    product_name: str
    price: float
    sku: str
    description: Optional[str]


class ProductResponse(SQLModel):
    id: UUID
    product_name: str
    price: float
    sku: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime


class ProductListResponse(SQLModel):
    total: int
    page: int
    total_pages: int
    products: List[ProductResponse]


class ProductDeleteResponse(SQLModel):
    id: UUID
    deleted: bool
