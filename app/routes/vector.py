from fastapi import APIRouter, Depends
from app.vector.chroma import ChromaVectorStore
from app.vector.schemas import VectorSearchRequest, VectorSearchResult
from app.deps.auth import get_current_user

router = APIRouter(tags=["Vector DB"])


@router.post("/similarity-search")
async def similarity_search(
    payload: VectorSearchRequest,
    user=Depends(get_current_user)
):
    """
    Search vector database with optional filtering by ingestion type.
    
    Ingestion types:
    - 'file': Documents uploaded via /ingest/file
    - 'image': Images uploaded via /vision/upload
    - 'text': Direct text ingestion via /ingest/text
    
    If no ingestion_type is specified, searches all types.
    """
    store = ChromaVectorStore(collection_name="unified_docs")

    # Build filter with ChromaDB operators
    if payload.ingestion_type:
        filter_dict = {
            "$and": [
                {"user_id": {"$eq": user.id}},
                {"ingestion_type": {"$eq": payload.ingestion_type}}
            ]
        }
    else:
        filter_dict = {"user_id": {"$eq": user.id}}

    results = store.similarity_search(
        query=payload.query,
        k=payload.k,
        filter=filter_dict
    )

    return [
        {"content": r.page_content, "metadata": r.metadata}
        for r in results
    ]


@router.post("/semantic-search-with-score")
async def semantic_search_with_score(
    payload: VectorSearchRequest,
    user=Depends(get_current_user)
):
    """
    Search vector database with similarity scores and optional filtering.
    
    Returns results with similarity scores (0-1, higher is more similar).
    
    Ingestion types:
    - 'file': Documents uploaded via /ingest/file
    - 'image': Images uploaded via /vision/upload  
    - 'text': Direct text ingestion via /ingest/text
    """
    store = ChromaVectorStore(collection_name="unified_docs")

    # Build filter with ChromaDB operators
    if payload.ingestion_type:
        filter_dict = {
            "$and": [
                {"user_id": {"$eq": user.id}},
                {"ingestion_type": {"$eq": payload.ingestion_type}}
            ]
        }
    else:
        filter_dict = {"user_id": {"$eq": user.id}}

    results = store.similarity_search_with_score(
        query=payload.query,
        k=payload.k,
        filter=filter_dict
    )

    return [
        {
            "content": doc.page_content,
            "metadata": doc.metadata,
            "score": score
        }
        for doc, score in results
    ]
