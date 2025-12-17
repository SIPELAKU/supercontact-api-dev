from datetime import date
from typing import Optional, List
from uuid import UUID

from sqlmodel import SQLModel


class MailingBase(SQLModel):
    subject: str
    status: str
    send_date: date
    statistic: str


class MailingResponse(MailingBase):
    id: UUID

    class Config:
        from_attributes = True


class PaginatedMailings(SQLModel):
    total: int
    page: int
    limit: int
    total_pages: int
    mailings: List[MailingResponse]

    class Config:
        from_attributes = True


class MailingCreate(MailingBase):
    pass


class MailingUpdate(SQLModel):
    subject: Optional[str] = None
    status: Optional[str] = None
    send_date: Optional[date] = None
    statistic: Optional[str] = None


class MailingDeleteResponse(SQLModel):
    id: UUID
    deleted: bool
