from fastapi import APIRouter
from app.routes import auth, chats

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth")
api_router.include_router(chats.router, prefix="/chat")

@api_router.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok"}
