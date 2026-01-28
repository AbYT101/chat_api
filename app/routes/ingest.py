from fastapi import APIRouter, UploadFile, Depends
from uuid import uuid4
from app.vector.chroma import ChromaVectorStore
from app.vector.utils import chunk_text
from app.deps.auth import get_current_user


router = APIRouter(tags=["Ingest"])


@router.post("/file")
async def ingest_file(file: UploadFile, user=Depends(get_current_user)):
    content = (await file.read()).decode("utf-8")

    chunks = chunk_text(content)

    vector_store = ChromaVectorStore(collection_name="file_docs")

    texts = []
    metadatas = []
    ids = []

    for chunk in chunks:
        texts.append(chunk)
        metadatas.append(
            {"user_id": user.id, "source": "file", "filename": file.filename}
        )
        ids.append(str(uuid4()))

    vector_store.upsert(texts, metadatas, ids)

    return {"chunks_ingested": len(chunks)}
