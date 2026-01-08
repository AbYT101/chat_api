from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.user import User
from app.core.security import hash_password, verify_password, create_access_token


class AuthService:
    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
        result = db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    @staticmethod
    async def create_user(
        db: AsyncSession, username: str, email: str, password: str
    ) -> User:
        user = User(
            email=email, username=username, hashed_password=hash_password(password)
        )

        db.add(user)
        await db.refresh(user)
        return user

    @staticmethod
    async def authenticate_user(user: User, password: str) -> bool:
        return verify_password(password, user.hashed_password)

    @staticmethod
    async def generate_token(user: User) -> str:
        return create_access_token({"sub": str(user.id)})
