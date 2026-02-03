from fastapi import APIRouter, UploadFile, Depends
from uuid import uuid4
from pydantic import BaseModel
from app.vector.chroma import ChromaVectorStore
from app.vector.utils import chunk_text
from app.deps.auth import get_current_user


router = APIRouter(tags=["Ingest"])


class TextIngestRequest(BaseModel):
    content: str
    title: str | None = None


@router.post("/file")
async def ingest_file(file: UploadFile, user=Depends(get_current_user)):
    """Ingest a text file into the vector database"""
    content = (await file.read()).decode("utf-8")

    chunks = chunk_text(content)

    # Use unified collection with ingestion_type metadata
    vector_store = ChromaVectorStore(collection_name="unified_docs")

    texts = []
    metadatas = []
    ids = []

    for chunk in chunks:
        texts.append(chunk)
        metadatas.append({
            "user_id": user.id,
            "ingestion_type": "file",
            "source": file.filename,
        })
        ids.append(str(uuid4()))

    vector_store.upsert(texts, metadatas, ids)

    return {
        "chunks_ingested": len(chunks),
        "ingestion_type": "file",
        "source": file.filename,
    }


@router.post("/text")
async def ingest_text(payload: TextIngestRequest, user=Depends(get_current_user)):
    """Ingest raw text into the vector database"""
    chunks = chunk_text(payload.content)

    # Use unified collection with ingestion_type metadata
    vector_store = ChromaVectorStore(collection_name="unified_docs")

    texts = []
    metadatas = []
    ids = []

    for chunk in chunks:
        texts.append(chunk)
        metadatas.append({
            "user_id": user.id,
            "ingestion_type": "text",
            "source": payload.title or "direct_text_input",
        })
        ids.append(str(uuid4()))

    vector_store.upsert(texts, metadatas, ids)

    return {
        "chunks_ingested": len(chunks),
        "ingestion_type": "text",
        "source": payload.title or "direct_text_input",
    }
