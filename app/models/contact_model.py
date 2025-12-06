from sqlalchemy import Column, String, Date, Text
from sqlmodel import Relationship, SQLModel, Field
from uuid import UUID, uuid4
from typing import Optional, List
from datetime import date


class Contact(SQLModel, table=True):
    __tablename__ = "contacts"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id")

    name: str = Field(sa_column=Column(String(255), nullable=False))
    email: str = Field(sa_column=Column(String(255), nullable=False, unique=True))
    phone: str = Field(sa_column=Column(String(30), nullable=False))
    company: str = Field(sa_column=Column(String(30), nullable=False))
    job_title: str = Field(sa_column=Column(String(30), nullable=False))
    address: str = Field(sa_column=Column(Text(), nullable=False))

    user: Optional["User"] = Relationship(back_populates="contacts")

    tasks: List["ContactTask"] = Relationship(
        back_populates="contact",
        sa_relationship_kwargs={"foreign_keys": "[ContactTask.contact_id]"}
    )

    assigned_tasks: List["ContactTask"] = Relationship(
        back_populates="assign_to",
        sa_relationship_kwargs={"foreign_keys": "[ContactTask.assign_to_contact]"}
    )

    notes: List["ContactNote"] = Relationship(
        back_populates="contact",
        sa_relationship_kwargs={"foreign_keys": "[ContactNote.contact_id]"}
    )


class ContactTask(SQLModel, table=True):
    __tablename__ = "contact_tasks"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    contact_id: UUID = Field(foreign_key="contacts.id")
    task_name: str = Field(sa_column=Column(String(255), nullable=False))
    task_date: date = Field(sa_column=Column(Date, nullable=False))
    priority: str = Field(sa_column=Column(String(255), nullable=False))
    assign_to_contact: UUID = Field(foreign_key="contacts.id")

    # Relationships
    contact: Optional["Contact"] = Relationship(
        back_populates="tasks",
        sa_relationship_kwargs={"foreign_keys": "[ContactTask.contact_id]"}
    )

    assign_to: Optional["Contact"] = Relationship(
        back_populates="assigned_tasks",
        sa_relationship_kwargs={"foreign_keys": "[ContactTask.assign_to_contact]"}
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

