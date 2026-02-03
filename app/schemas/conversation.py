from pydantic import BaseModel, ConfigDict
from datetime import datetime

class ConversationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime
