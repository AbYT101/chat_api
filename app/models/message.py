from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
from typing import Optional

class Message(BaseModel):
    id: UUID = UUID()
    conversation_id: UUID
    sender_id: UUID
    content: str
    role: str
    created_at: str
    updated_at: str
    is_deleted: bool = False
    is_edited: bool = False


