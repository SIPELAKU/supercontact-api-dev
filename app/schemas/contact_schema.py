from datetime import date
from typing import List, Optional
from uuid import UUID

from pydantic import EmailStr
from sqlmodel import SQLModel


class ContactRequest(SQLModel):
    name: str
    email: EmailStr
    company: str
    phone: Optional[str] = None
    job_title: Optional[str] = None
    address: Optional[str] = None


class ContactResponse(SQLModel):
    id: UUID
    name: str
    email: EmailStr
    company: str
    phone: Optional[str] = None
    job_title: Optional[str] = None
    address: Optional[str] = None


class ContactListResponse(SQLModel):
    total: int
    page: int
    limit: int
    data: List[ContactResponse]

    class Config:
        from_attributes = True


class NoteCreate(SQLModel):
    note: str


class NoteResponse(SQLModel):
    id: UUID
    contact_id: UUID
    note: str

    class Config:
        from_attributes = True


class TaskCreate(SQLModel):
    task_name: str
    date: date
    priority: str
    assign_to_contact: UUID


class TaskResponse(SQLModel):
    id: UUID
    contact_id: int
    task_name: str
    date: date
    priority: str
    assign_to_contact: UUID

    class Config:
        from_attributes = True
