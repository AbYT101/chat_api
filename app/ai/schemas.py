from pydantic import BaseModel
from typing import Optional


class ChatRequest(BaseModel):
    message: str
    model: str = "llama3.2:3b"
    context: Optional[str] = None
