from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

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
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at)
        )
        return result.scalars().all()
