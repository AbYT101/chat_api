from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
import os
from app.core.config import settings

DATABASE_URL = getattr(settings, "DATABASE_URL", None) or os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set (use postgresql+asyncpg://...).")

engine = create_async_engine(DATABASE_URL, future=True, echo=True)
async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
