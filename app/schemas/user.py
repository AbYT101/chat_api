from pydantic import BaseModel, EmailStr


# Signup
class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str


# User data response to clinet
class UserOut(BaseModel):
    id: int
    email: EmailStr
    username: str

    class Config:
        orm_mode = True
