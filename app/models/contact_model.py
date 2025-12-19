from datetime import date, datetime, timezone
from typing import Optional, List
from uuid import UUID, uuid4

from sqlalchemy import Column, String, Text
from sqlmodel import Relationship, SQLModel, Field, DateTime, desc


class ContactTask(SQLModel, table=True):
    __tablename__ = "contact_tasks"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    contact_id: UUID = Field(foreign_key="contacts.id")
    task_name: str = Field(sa_column=Column(String(255), nullable=False))
    task_date: date = Field(sa_column=Column(DateTime(timezone=True), nullable=False))
    priority: str = Field(sa_column=Column(String(255), nullable=False))
    assign_to: UUID = Field(foreign_key="users.id")

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            onupdate=lambda: datetime.now(timezone.utc),
        ),
    )

    # Relationships
    contact: Optional["Contact"] = Relationship(
        back_populates="tasks",
        sa_relationship_kwargs={"foreign_keys": "[ContactTask.contact_id]"}
    )

    user: "User" = Relationship(back_populates="contact_tasks")


class ContactNote(SQLModel, table=True):
    __tablename__ = "contact_notes"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id")
    contact_id: UUID = Field(foreign_key="contacts.id")
    note: str = Field(sa_column=Column(Text, nullable=False))

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            onupdate=lambda: datetime.now(timezone.utc),
        ),
    )

    contact: Optional["Contact"] = Relationship(
        back_populates="notes",
        sa_relationship_kwargs={"foreign_keys": "[ContactNote.contact_id]"}
    )
    user: "User" = Relationship(back_populates="contact_notes")


class Contact(SQLModel, table=True):
    __tablename__ = "contacts"

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    name: str = Field(sa_column=Column(String(255), nullable=False))
    email: str = Field(sa_column=Column(String(255), nullable=False, unique=True))
    company: str = Field(sa_column=Column(String(255), nullable=False))
    phone: Optional[str] = Field(sa_column=Column(String(30), nullable=True))
    job_title: Optional[str] = Field(sa_column=Column(String(30), nullable=True))
    address: Optional[str] = Field(sa_column=Column(Text(), nullable=True))

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            onupdate=lambda: datetime.now(timezone.utc),
        ),
    )

    lead: Optional["Lead"] = Relationship(back_populates="contact")
    pipeline: Optional["Pipeline"] = Relationship(back_populates="contact")
    tasks: List["ContactTask"] = Relationship(
        back_populates="contact",
        sa_relationship_kwargs={"foreign_keys": "[ContactTask.contact_id]", "cascade": "all, delete-orphan"}
    )
    notes: List["ContactNote"] = Relationship(
        back_populates="contact",
        sa_relationship_kwargs={
            "foreign_keys": "[ContactNote.contact_id]",
            "cascade": "all, delete-orphan",
            "order_by": desc(ContactNote.created_at)
        }
    )

    @property
    def last_contacted(self) -> Optional["ContactNote"]:
        if self.notes:
            return self.notes[0]
        return None
