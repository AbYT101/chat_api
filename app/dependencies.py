from typing import AsyncGenerator
from fastapi import HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Yield an AsyncSession from your DB layer.
    This expects you to have app.db.async_session (callable returning AsyncSession).
    Replace or adapt to your project's DB setup.
    """
    try:
        from app.db import async_session  # adjust if your session factory lives elsewhere
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database session factory not found. Create app/db.py exporting async_session."
        )

    async with async_session() as session:
        yield session

async def get_current_user(request: Request):
    """
    Minimal placeholder for auth dependency.
    Replace with your real token decoding / user lookup.
    If Authorization header missing, returns 401.
    Otherwise returns a lightweight object with an `id` attribute so service code can run.
    """
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    # TODO: decode token and lookup real user. Returning dummy user for now.
    class _User:
        def __init__(self, id: int = 1):
            self.id = id

    return _User()