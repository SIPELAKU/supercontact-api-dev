from datetime import datetime
from sqlmodel import SQLModel
from uuid import UUID


class ChatMessageCreate(SQLModel):
    receiver_id: UUID
    message: str

class ChatMessageResponse(SQLModel):
    id: UUID
    sender_id: UUID
    receiver_id: UUID
    message: str
    created_at: datetime

    class Config:
        from_attributes = True