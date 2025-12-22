from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.chat_repository import ChatRepository
from fastapi import WebSocket, WebSocketDisconnect
from app.services.connectionmanager_service import manager
from sqlmodel.ext.asyncio.session import AsyncSession
from app.db.session import get_async_session
from app.core import auth_require
from app.services.chat_service import ChatService
from app.schemas.chat_schema import ChatMessageCreate, ChatMessageResponse
from uuid import UUID

router = APIRouter(prefix="/chat", tags=["Chat"])

@router.get("/{target_id}", response_model=list[ChatMessageResponse])
async def get_chat(
    target_id: UUID,
    db: AsyncSession = Depends(get_async_session),
    current_user=Depends(auth_require),
):
    repo = ChatRepository(db)
    messages = await repo.get_conversation(
        user_id=current_user.id,
        target_id=target_id
    )

    return [
        ChatMessageResponse.model_validate(
            msg[0] if isinstance(msg, tuple) else msg
        )
        for msg in messages
    ]

@router.websocket("/ws/chat/{user_id}")
async def websocket_chat(
    websocket: WebSocket,
    user_id: UUID,
    db: AsyncSession = Depends(get_async_session),
):
    await manager.connect(user_id, websocket)
    repo = ChatRepository(db)
    service = ChatService(repo)

    try:
        while True:
            data = await websocket.receive_json()

            chat = await service.send_message(
                sender_id=user_id,
                receiver_id=data["receiver_id"],
                message=data["message"]
            )

            payload = {
                "id": str(chat.id),
                "sender_id": chat.sender_id,
                "receiver_id": chat.receiver_id,
                "message": chat.message,
                "created_at": chat.created_at.isoformat()
            }

            await manager.send_personal_message(chat.receiver_id, payload)

            await manager.send_personal_message(chat.sender_id, payload)

    except WebSocketDisconnect:
        manager.disconnect(user_id, websocket)

@router.post("/")
async def send_chat(
    payload: ChatMessageCreate,
    db: AsyncSession = Depends(get_async_session),
    # receiver_id: UUID,
    current_user=Depends(auth_require),
):
    repo = ChatRepository(db)
    service = ChatService(repo)

    return await service.send_message(
        sender_id=current_user.id,
        receiver_id=payload.receiver_id,
        message=payload.message,
    )

