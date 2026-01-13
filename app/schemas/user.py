from pydantic import BaseModel, EmailStr, Field


# Signup
class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=6)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# User data response to client
class UserDTO(BaseModel):
    id: int
    email: EmailStr
    username: str

    class Config:
        orm_mode = True
