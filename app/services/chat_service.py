from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_
from datetime import datetime
from fastapi import HTTPException, status

from app.models.conversation import Conversation
from app.models.message import Message
from app.models.user import User


class ChatService:

    @staticmethod
    async def create_conversation(db: AsyncSession, user: User) -> Conversation:
        conversation = Conversation(owner_id=user.id)
        db.add(conversation)
        await db.commit()
        await db.refresh(conversation)
        return conversation

    @staticmethod
    async def list_conversations(db: AsyncSession, user: User):
        result = await db.execute(
            select(Conversation).where(Conversation.owner_id == user.id)
        )
        return result.scalars().all()

    @staticmethod
    async def create_message(
        db: AsyncSession,
        user: User,
        conversation_id: int,
        content: str,
    ) -> Message:
        message = Message(
            conversation_id=conversation_id,
            sender_id=user.id,
            role="user",
            content=content,
            is_deleted=False,
        )
        db.add(message)
        await db.commit()
        await db.refresh(message)
        return message

    @staticmethod
    async def list_messages(
        db: AsyncSession,
        user: User,
        conversation_id: int,
        limit: int,
        offset: int,
    ):
        # Ownership check
        result = await db.execute(
            select(Conversation).where(
                Conversation.id == conversation_id,
                Conversation.owner_id == user.id,
            )
        )
        conversation = result.scalar_one_or_none()
        if not conversation:
            return None

        result = await db.execute(
            select(Message)
            .where(
                Message.conversation_id == conversation_id,
                or_(Message.is_deleted.is_(False), Message.is_deleted.is_(None)),
            )
            .order_by(Message.created_at)
            .limit(limit)
            .offset(offset)
        )
        return result.scalars().all()

    @staticmethod
    async def update_message(
        db,
        user,
        message_id: int,
        content: str,
    ):
        result = await db.execute(
            select(Message).where(
                Message.id == message_id,
                Message.sender_id == user.id,
                Message.role == "user",
                or_(Message.is_deleted.is_(False), Message.is_deleted.is_(None)),
            )
        )
        message = result.scalar_one_or_none()

        if not message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Message not found or not editable",
            )

        message.content = content
        message.edited_at = datetime.utcnow()

        await db.commit()
        await db.refresh(message)
        return message

    @staticmethod
    async def delete_message(
        db,
        user,
        message_id: int,
    ):
        result = await db.execute(
            select(Message).where(
                Message.id == message_id,
                Message.sender_id == user.id,
                Message.role == "user",
                or_(Message.is_deleted.is_(False), Message.is_deleted.is_(None)),
            )
        )
        message = result.scalar_one_or_none()

        if not message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Message not found or not deletable",
            )

        message.is_deleted = True
        message.content = "[deleted]"
        message.edited_at = datetime.utcnow()

        await db.commit()
        return
