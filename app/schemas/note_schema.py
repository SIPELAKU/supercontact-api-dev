from datetime import date, time
from typing import Optional, List
from uuid import UUID

from sqlmodel import SQLModel


class NoteGetQuery(SQLModel):
    page: int = 1
    limit: int = 10
    search: Optional[str] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    sort_by: str = "created_at"
    sort_order: str = "desc"


class NoteBase(SQLModel):
    title: str
    content: str
    reminder_date: date
    reminder_time: time


class NoteResponse(NoteBase):
    id: UUID

    class Config:
        from_attributes = True


class PaginatedNote(SQLModel):
    total: int
    page: int
    limit: int
    notes: List[NoteResponse]

    class Config:
        from_attributes = True


class NoteCreate(NoteBase):
    pass


class NoteUpdate(SQLModel):
    title: Optional[str]
    content: Optional[str]
    reminder_date: Optional[date]
    reminder_time: Optional[time]

