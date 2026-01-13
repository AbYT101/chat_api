from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.user import UserCreate, UserDTO, UserLogin, TokenResponse
from app.services.auth_service import AuthService

from app.deps.db import get_db


router = APIRouter(tags=["Auth"])


@router.post("/signup", response_model=UserDTO)
async def signup(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    existing_email = await AuthService.get_user_by_email(db, user_in.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    existing_username = await AuthService.get_user_by_username(db, user_in.username)
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken"
        )

    user = await AuthService.create_user(
        db, user_in.email, user_in.username, user_in.password
    )
    return user


@router.post("/login", response_model=TokenResponse)
async def login(user_in: UserLogin, db: AsyncSession = Depends(get_db)):
    user = await AuthService.get_user_by_username(db, user_in.username)
    if not user or not await AuthService.authenticate_user(user, user_in.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )

    token = await AuthService.generate_token(user)
    return {"access_token": token, "token_type": "bearer"}
