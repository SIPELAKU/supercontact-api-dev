from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from pydantic import ConfigDict
from sqlmodel import SQLModel, Field, Relationship

class UserDevice(SQLModel, table=True):
    __tablename__ = "user_devices"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)

    browser: str
    device: str
    location: Optional[str]

    last_activity: datetime = Field(
        default_factory=datetime.utcnow
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow
    )

    user: "User" = Relationship(back_populates="device")