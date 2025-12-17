from datetime import date
from typing import Optional, List
from uuid import UUID, uuid4

from sqlalchemy import Column, String, Date, Text
from sqlmodel import Relationship, SQLModel, Field


class Contact(SQLModel, table=True):
    __tablename__ = "contacts"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    # user_id: UUID = Field(foreign_key="users.id")

    name: str = Field(sa_column=Column(String(255), nullable=False))
    email: str = Field(sa_column=Column(String(255), nullable=False, unique=True))
    company: str = Field(sa_column=Column(String(255), nullable=False))
    phone: Optional[str] = Field(sa_column=Column(String(30), nullable=True))
    job_title: Optional[str] = Field(sa_column=Column(String(30), nullable=True))
    address: Optional[str] = Field(sa_column=Column(Text(), nullable=True))

    # user: Optional["User"] = Relationship(back_populates="contacts")
    lead: Optional["Lead"] = Relationship(back_populates="contact")
    pipeline: Optional["Pipeline"] = Relationship(back_populates="contact")

    tasks: List["ContactTask"] = Relationship(
        back_populates="contact",
        sa_relationship_kwargs={"foreign_keys": "[ContactTask.contact_id]", "cascade": "all, delete-orphan"}
    )

    notes: List["ContactNote"] = Relationship(
        back_populates="contact",
        sa_relationship_kwargs={"foreign_keys": "[ContactNote.contact_id]", "cascade": "all, delete-orphan"}
    )


class UserTaskLink(SQLModel, table=True):
    __tablename__ = "user_tasks"

    user_id: UUID = Field(foreign_key="users.id", primary_key=True)
    task_id: UUID = Field(foreign_key="contact_tasks.id", primary_key=True)


class ContactTask(SQLModel, table=True):
    __tablename__ = "contact_tasks"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    contact_id: UUID = Field(foreign_key="contacts.id")
    task_name: str = Field(sa_column=Column(String(255), nullable=False))
    task_date: date = Field(sa_column=Column(Date, nullable=False))
    priority: str = Field(sa_column=Column(String(255), nullable=False))
    assign_to: UUID = Field(foreign_key="users.id")

    # Relationships
    contact: Optional["Contact"] = Relationship(
        back_populates="tasks",
        sa_relationship_kwargs={"foreign_keys": "[ContactTask.contact_id]"}
    )

    users: List["User"] = Relationship(
        back_populates="contact_tasks",
        link_model=UserTaskLink
    )


class ContactNote(SQLModel, table=True):
    __tablename__ = "contact_notes"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    contact_id: UUID = Field(foreign_key="contacts.id")
    note: str = Field(sa_column=Column(Text, nullable=False))

    contact: Optional["Contact"] = Relationship(
        back_populates="notes",
        sa_relationship_kwargs={"foreign_keys": "[ContactNote.contact_id]"}
    )
