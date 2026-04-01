from fastapi import APIRouter, Depends, status, Response
from sqlalchemy.ext.asyncio import AsyncSession
import logging

# Use the SAME dependencies your working routes use
from app.deps.auth import get_current_user
from app.deps.db import get_db

from app.services.chat_service import ChatService

router = APIRouter(prefix="/chat/conversations", tags=["chat"])


@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conversation_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    try:
        await ChatService.delete_conversation(db, user, conversation_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except Exception as exc:
        logging.exception("DELETE /chat/conversations/%s failed", conversation_id)
        raise