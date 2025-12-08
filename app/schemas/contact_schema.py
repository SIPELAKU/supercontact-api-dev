from datetime import date
from typing import List
from uuid import UUID

from pydantic import EmailStr
from sqlmodel import SQLModel


class ContactResponse(SQLModel):
    id: UUID
    name: str
    email: EmailStr
    phone: str
    company: str
    job_title: str
    address: str


class ContactListResponse(SQLModel):
    total: int
    page: int
    limit: int
    data: List[ContactResponse]

    class Config:
        from_attributes = True


class ContactRequest(SQLModel):
    name: str
    email: EmailStr
    phone: str
    company: str
    job_title: str
    address: str


class DeleteResponse(SQLModel):
    status: str
    message: str


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
