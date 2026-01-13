from pydantic import BaseModel
from datetime import datetime

class ConversationOut(BaseModel):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
