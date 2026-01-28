from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.deps.auth import get_current_user
from app.ai.chains.rag_chain import RAGService

router = APIRouter(tags=["RAG"])


class RAGRequest(BaseModel):
    question: str
    model: str = "llama3.2:3b"
    k: int = 5


@router.post("/query")
async def rag_query(
    payload: RAGRequest,
    user=Depends(get_current_user),
):
    answer = await RAGService.run(
        question=payload.question,
        user_id=user.id,
        model_name=payload.model,
        k=payload.k,
    )

    return {
        "question": payload.question,
        "answer": answer,
        "model": payload.model,
    }
