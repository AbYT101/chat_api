import uvicorn
from fastapi import FastAPI, Request
from app.routes import router
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import chat  # ensure this import matches your package layout
import logging
import traceback

def create_app() -> FastAPI:
    app = FastAPI(
        title="Chat App API",
        description="API for a chat application.",
        version="0.0.1",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    app.include_router(router.api_router)
    app.include_router(chat.router)  # mount chat routes
    
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        # log full traceback to stdout / console
        logging.exception("Unhandled exception on %s %s", request.method, request.url)
        tb = traceback.format_exc()
        # Return detail + traceback for debugging (remove in production)
        return JSONResponse(
            status_code=500,
            content={"detail": str(exc), "traceback": tb},
        )
        
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
        

    return app


app = create_app()

if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)
