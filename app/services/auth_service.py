from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from app.models.user import User
from app.core.security import hash_password, verify_password, create_access_token
from datetime import datetime


class AuthService:
    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_by_username(db: AsyncSession, username: str) -> User | None:
        username = username.strip().lower()
        result = await db.execute(
            select(User).where(func.lower(User.username) == username)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def create_user(
        db: AsyncSession, email: str, username: str, password: str
    ) -> User:
        # enforce bcrypt 72-byte limit (measured in UTF-8 bytes)
        if len(password.encode("utf-8")) > 72:
            from fastapi import HTTPException, status

            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Password too long: must be at most 72 bytes (bcrypt limit).",
            )

        # basic sanitation and normalization
        email = email.strip().lower()
        username = username.strip().lower()

        user = User(
            email=email,
            username=username,
            hashed_password=hash_password(password),
            created_at=datetime.utcnow().isoformat(),
        )

        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def authenticate_user(user: User, password: str) -> bool:
        return verify_password(password, user.hashed_password)

    @staticmethod
    async def generate_token(user: User) -> str:
        return create_access_token({"sub": str(user.id)})
