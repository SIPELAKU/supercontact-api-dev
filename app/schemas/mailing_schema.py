from sqlmodel import SQLModel
from datetime import date
from typing import Optional, List
from uuid import UUID
from datetime import date


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
    status: str
    message: str
    total: int
    page: int
    limit: int
    data: List[MailingResponse]

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
