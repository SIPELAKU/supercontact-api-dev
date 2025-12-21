from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from datetime import date, datetime, timezone
from typing import Optional, List
from uuid import UUID, uuid4

from sqlalchemy import Column, String, Text
from sqlmodel import Relationship, SQLModel, Field, DateTime, desc
from sqlalchemy.dialects.postgresql import UUID as PGUUID



class ChatMessage(SQLModel, table=True):
    __tablename__ = "chat_messages"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    sender_id: UUID = Field(sa_column=Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False))
    receiver_id: UUID = Field(sa_column=Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False))
    message: str = Field(sa_column=Column(Text(), nullable=False))
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )

    # sender: "User" = Relationship(
    #     back_populates="sent_messages",
    #     sa_relationship_kwargs={
    #         "foreign_keys": [sender_id]
    #     }
    # )

    # receiver: "User" = Relationship(
    #     back_populates="received_messages",
    #     sa_relationship_kwargs={
    #         "foreign_keys": [receiver_id]
    #     }
    # )

    sender: "User" = Relationship(
        sa_relationship_kwargs={"primaryjoin": "ChatMessage.sender_id==User.id"}
    )

    receiver: "User" = Relationship(
        sa_relationship_kwargs={"primaryjoin": "ChatMessage.receiver_id==User.id"}
    )