from pydantic import EmailStr
from typing import Optional, List, Generic, TypeVar
from datetime import date
from uuid import UUID
from sqlmodel import SQLModel


T = TypeVar("T")

class ContactBase(SQLModel):
    name: str
    email: EmailStr
    phone: str
    company: str
    job_title: str
    address: str

class ContactRes(ContactBase):
    id: UUID

    class Config:
        from_attributes = True

class PaginatedContacts(SQLModel):
    status: str
    message: str
    total: int
    page: int
    limit: int
    data: List[ContactRes]

    class Config:
        from_attributes = True

class ContactCreate(ContactBase):
    pass

class ResponseModel(SQLModel, Generic[T]):
    status: str
    message: str
    data: Optional[T] = None

class ContactResponse(ResponseModel[ContactRes]):
    pass

class ContactUpdate(SQLModel):
    name: Optional[str]
    email: Optional[EmailStr]
    phone: Optional[str]
    company: Optional[str]
    job_title: Optional[str]
    address: Optional[str]

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