import uvicorn
from fastapi import FastAPI


def create_app() -> FastAPI:
    app = FastAPI(
        title="Chat App API",
        description="API for a chat application.",
        version="0.0.1",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    @app.get("/health")
    async def health():
        return {"status": "OK."}
    
    return app

app = create_app()

if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)
