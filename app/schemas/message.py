from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class MessageCreate(BaseModel):
    content: str


class MessageUpdate(BaseModel):
    content: str


class MessageOut(BaseModel):
    id: int
    role: str
    content: str
    is_deleted: bool
    created_at: datetime
    edited_at: Optional[datetime]

    class Config:
        orm_mode = True
