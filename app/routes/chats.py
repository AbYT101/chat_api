from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps.db import get_db
from app.deps.auth import get_current_user
from app.models.user import User
from app.schemas.conversation import ConversationOut
from app.schemas.message import MessageCreate, MessageOut
from app.services.chat_service import ChatService

router = APIRouter(tags=["Chats"])


@router.post("/conversations", response_model=ConversationOut)
async def create_conversation(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await ChatService.create_conversation(db, user)


@router.get("/conversations", response_model=list[ConversationOut])
async def list_conversations(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await ChatService.list_conversations(db, user)


@router.post(
    "/conversations/{conversation_id}/messages",
    response_model=MessageOut,
)
async def send_message(
    conversation_id: int,
    message: MessageCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await ChatService.create_message(
        db=db,
        user=user,
        conversation_id=conversation_id,
        content=message.content,
    )


@router.get(
    "/conversations/{conversation_id}/messages",
    response_model=list[MessageOut],
)
async def get_messages(
    conversation_id: int,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    messages = await ChatService.list_messages(db, user, conversation_id, limit, offset)
    if messages is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )
    return messages
