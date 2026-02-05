from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
import json

from app.deps.db import get_db
from app.deps.auth import get_current_user
from app.models.user import User
from app.schemas.conversation import ConversationOut
from app.schemas.message import MessageCreate, MessageOut
from app.services.chat_service import ChatService
from app.schemas.message import MessageUpdate
from app.ai.chains.chat_chain import AIChatService

router = APIRouter(tags=["Chats"])


class ChatbotRequest(BaseModel):
    message: str
    model: str = "gpt-5-mini"


class ChatbotResponse(BaseModel):
    user_message: MessageOut
    ai_message: MessageOut


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


@router.put("/messages/{message_id}", response_model=MessageOut)
async def edit_message(
    message_id: int,
    payload: MessageUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await ChatService.update_message(
        db=db,
        user=user,
        message_id=message_id,
        content=payload.content,
    )


@router.delete("/messages/{message_id}", status_code=204)
async def delete_message(
    message_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await ChatService.delete_message(
        db=db,
        user=user,
        message_id=message_id,
    )


@router.post(
    "/conversations/{conversation_id}/chat",
    response_model=ChatbotResponse,
)
async def chat_with_ai(
    conversation_id: int,
    payload: ChatbotRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Send a message and get an AI response with conversation memory.
    This endpoint integrates the chatbot with memory capabilities.
    """
    # 1. Verify conversation ownership and save user message
    user_message = await ChatService.create_message(
        db=db,
        user=user,
        conversation_id=conversation_id,
        content=payload.message,
    )

    # 2. Generate AI response using the chain with memory
    ai_response = await AIChatService.generate_response(
        user_message=payload.message,
        conversation_id=conversation_id,
        model_name=payload.model,
    )

    # 3. Save AI response to database
    from app.models.message import Message
    ai_message = Message(
        conversation_id=conversation_id,
        sender_id=None,  # AI has no user ID
        role="assistant",
        content=ai_response,
        is_deleted=False,
    )
    db.add(ai_message)
    await db.commit()
    await db.refresh(ai_message)

    return ChatbotResponse(
        user_message=user_message,
        ai_message=ai_message,
    )


@router.post("/conversations/{conversation_id}/chat/stream")
async def chat_with_ai_stream(
    conversation_id: int,
    payload: ChatbotRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Send a message and get a streaming AI response with conversation memory.
    
    This endpoint streams the AI response word-by-word for a better UX.
    Uses Server-Sent Events (SSE) format.
    
    Response format (SSE):
    - event: message
      data: {"type": "user_message", "message_id": 123, ...}
    
    - event: token
      data: {"content": "Hello"}
    
    - event: done
      data: {"message_id": 124, "full_content": "..."}
    """
    # 1. Verify conversation ownership and save user message
    user_message = await ChatService.create_message(
        db=db,
        user=user,
        conversation_id=conversation_id,
        content=payload.message,
    )
    
    async def event_generator():
        # Send user message info first
        yield f"event: message\n"
        yield f"data: {json.dumps({'type': 'user_message', 'message_id': user_message.id, 'content': user_message.content})}\n\n"
        
        # Stream AI response
        full_response = ""
        async for chunk in AIChatService.generate_response_stream(
            user_message=payload.message,
            conversation_id=conversation_id,
            model_name=payload.model,
        ):
            full_response += chunk
            yield f"event: token\n"
            yield f"data: {json.dumps({'content': chunk})}\n\n"
        
        # Save AI response to database
        from app.models.message import Message
        ai_message = Message(
            conversation_id=conversation_id,
            sender_id=None,
            role="assistant",
            content=full_response,
            is_deleted=False,
        )
        db.add(ai_message)
        await db.commit()
        await db.refresh(ai_message)
        
        # Send completion event
        yield f"event: done\n"
        yield f"data: {json.dumps({'message_id': ai_message.id, 'full_content': full_response})}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        }
    )
