from sqlalchemy import Column, Integer, ForeignKey, Text, String, DateTime, Boolean, func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    role = Column(String, nullable=False)  # user | assistant | system
    content = Column(Text, nullable=False)

    is_deleted = Column(Boolean, default=False)
    edited_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    conversation = relationship("Conversation", back_populates="messages")
