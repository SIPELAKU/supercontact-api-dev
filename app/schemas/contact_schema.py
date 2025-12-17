from datetime import datetime
from enum import StrEnum
from typing import Optional, List
from uuid import UUID

from pydantic import EmailStr
from sqlmodel import SQLModel


class User(SQLModel):
    fullname: str


class ContactSortOrder(StrEnum):
    ASC = 'asc'
    DESC = 'desc'


class ContactSortBy(StrEnum):
    NAME = 'name',
    CREATED_AT = 'created_at',


class ContactGetQuery(SQLModel):
    page: int = 1,
    limit: int = 10,
    search: Optional[str] = None,
    sort_by: Optional[ContactSortBy] = None,
    sort_order: Optional[ContactSortOrder] = None,


class ContactBase(SQLModel):
    name: str
    email: EmailStr
    company: str
    phone: Optional[str]
    job_title: Optional[str]
    address: Optional[str]
    created_at: datetime
    updated_at: datetime


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
    user_id: UUID
    note: str
    user: User
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TaskCreate(SQLModel):
    task_name: str
    task_date: datetime
    priority: str
    assign_to: UUID


class TaskResponse(SQLModel):
    id: UUID
    contact_id: UUID
    task_name: str
    task_date: datetime
    priority: str
    assign_to: UUID
    user: User
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
