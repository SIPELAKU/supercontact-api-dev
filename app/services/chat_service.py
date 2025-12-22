from app.models.chat_model import ChatMessage
from app.repositories.chat_repository import ChatRepository
from uuid import UUID

class ChatService:
    def __init__(self, repo: ChatRepository):
        self.repo = repo

    async def send_message(self, sender_id: UUID, receiver_id: UUID, message: str):
        chat = ChatMessage(
            sender_id=sender_id,
            receiver_id=receiver_id,
            message=message
        )
        return await self.repo.create(chat)

