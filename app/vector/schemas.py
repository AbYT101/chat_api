from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional


class VectorSearchRequest(BaseModel):
    query: str
    k: int = Field(gt=0, default=5, description="Number of results to return")
    ingestion_type: Optional[str] = Field(
        default=None,
        description="Filter by ingestion type: 'file', 'image', or 'text'"
    )


class VectorSearchResult(BaseModel):
    content: str
    metadata: Dict[str, Any]
    score: Optional[float] = None
