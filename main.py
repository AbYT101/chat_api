import uvicorn
from fastapi import FastAPI
from app.routes import auth


def create_app() -> FastAPI:
    app = FastAPI(
        title="Chat App API",
        description="API for a chat application.",
        version="0.0.1",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    app.include_router(auth.router, prefix="/auth", tags=["Auth"])

    @app.get("/health")
    async def health():
        return {"status": "OK."}

    return app


app = create_app()

if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)
