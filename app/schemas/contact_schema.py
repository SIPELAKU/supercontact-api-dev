from datetime import date
from typing import Optional, List
from uuid import UUID

from pydantic import EmailStr
from sqlmodel import SQLModel


class ContactBase(SQLModel):
    name: str
    email: EmailStr
    company: str
    phone: Optional[str]
    job_title: Optional[str]
    address: Optional[str]


class ContactResponse(ContactBase):
    id: UUID

    class Config:
        from_attributes = True


class PaginatedContacts(SQLModel):
    total: int
    page: int
    limit: int
    contacts: List[ContactResponse]

    class Config:
        from_attributes = True


class ContactCreate(ContactBase):
    pass


class ContactUpdate(SQLModel):
    name: Optional[str]
    email: Optional[EmailStr]
    phone: Optional[str]
    company: Optional[str]
    job_title: Optional[str]
    address: Optional[str]


class ContactDeleteResponse(SQLModel):
    id: UUID
    deleted: bool


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
    task_date: date
    priority: str
    assign_to: UUID


class TaskResponse(SQLModel):
    id: UUID
    contact_id: UUID
    task_name: str
    task_date: date
    priority: str
    assign_to: UUID

    class Config:
        from_attributes = True
