from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.chat_model import ChatMessage
from uuid import UUID, uuid4

class ChatRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: ChatMessage):
        self.db.add(data)
        await self.db.commit()
        await self.db.refresh(data)
        return data

    # async def get_conversation(self, user_id: UUID, target_id: UUID):
    #     q = select(ChatMessage).where(
    #         ((ChatMessage.sender_id == user_id) & (ChatMessage.receiver_id == target_id)) |
    #         ((ChatMessage.sender_id == target_id) & (ChatMessage.receiver_id == user_id))
    #     ).order_by(ChatMessage.created_at)

    #     result = await self.db.exec(q)
    #     return result.all()

    async def get_conversation(self, user_id: UUID, target_id: UUID):
        q = select(ChatMessage).where(
            ((ChatMessage.sender_id == user_id) & (ChatMessage.receiver_id == target_id)) |
            ((ChatMessage.sender_id == target_id) & (ChatMessage.receiver_id == user_id))
        ).order_by(ChatMessage.created_at)

        result = await self.db.exec(q)
        return result.scalars().all()

