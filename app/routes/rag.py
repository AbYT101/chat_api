from typing import List, Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from app.deps.auth import get_current_user
from app.ai.chains.rag_chain import RAGService

router = APIRouter(tags=["RAG"])


class RAGRequest(BaseModel):
    question: str
    model: str = "llama3.2:3b"
    k: int = 5
    ingestion_types: Optional[List[str]] = Field(
        default=None,
        description="Filter by ingestion types: 'file', 'image', 'text'. If None, searches all."
    )


@router.post("/query")
async def rag_query(
    payload: RAGRequest,
    user=Depends(get_current_user),
):
    """
    Query the vector database with optional filtering by ingestion type.
    
    Examples:
    - Search only in uploaded files: {"question": "...", "ingestion_types": ["file"]}
    - Search only in images: {"question": "...", "ingestion_types": ["image"]}
    - Search in files and text: {"question": "...", "ingestion_types": ["file", "text"]}
    - Search everything: {"question": "...", "ingestion_types": null}
    """
    answer = await RAGService.run(
        question=payload.question,
        user_id=user.id,
        model_name=payload.model,
        k=payload.k,
        ingestion_types=payload.ingestion_types,
    )

    return {
        "question": payload.question,
        "answer": answer,
        "model": payload.model,
        "searched_types": payload.ingestion_types or ["file", "image", "text"],
    }
