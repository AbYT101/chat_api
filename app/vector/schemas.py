from pydantic import BaseModel, Field
from typing import Dict, Any, List


class VectorSearchRequest(BaseModel):
    query: str
    k: int = Field(gt=0, default=5)
    filters: Dict[str, Any] | None = None


class VectorSearchResult(BaseModel):
    content: str
    metadata: Dict[str, Any]
