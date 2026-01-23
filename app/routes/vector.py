from fastapi import APIRouter, Depends
from app.vector.chroma import ChromaVectorStore
from app.vector.schemas import VectorSearchRequest
from app.deps.auth import get_current_user

router = APIRouter(prefix="/vector", tags=["vector"])


@router.post("/similarity-search")
async def similarity_search(
    payload: VectorSearchRequest, user=Depends(get_current_user)
):
    store = ChromaVectorStore(collection_name="file_docs")

    results = store.similarity_search(
        query=payload.query, k=payload.k, filter={"user_id": user.id}
    )

    return [{"content": r.page_content, "metadata": r.metadata} for r in results]
