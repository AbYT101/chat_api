from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class MessageCreate(BaseModel):
    content: str


class MessageUpdate(BaseModel):
    content: str


class MessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    role: str
    content: str
    is_deleted: bool
    created_at: datetime
    edited_at: Optional[datetime]
