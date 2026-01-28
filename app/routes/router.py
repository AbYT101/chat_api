from fastapi import APIRouter
from app.routes import auth, chats, vector, ingest, rag

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth")
api_router.include_router(chats.router, prefix="/chat")
api_router.include_router(ingest.router, prefix="/ingest")
api_router.include_router(vector.router, prefix="/vector")
api_router.include_router(rag.router, prefix="/rag")


@api_router.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok"}
