from pydantic import BaseModel
from typing import Dict, Any, List


class VectorSearchRequest(BaseModel):
    query: str
    k: int
    filters: Dict[str, Any] | None = None


class VectorSearchResult(BaseModel):
    content: str
    metadata: Dict[str, Any]
