from datetime import datetime

from pydantic import EmailStr

from app.schemas.base import CamelModel


class UserBase(CamelModel):
    email: EmailStr
    full_name: str
    phone: str | None = None
    campus: str | None = None


class UserCreate(UserBase):
    password: str


class UserUpdate(CamelModel):
    full_name: str | None = None
    phone: str | None = None
    campus: str | None = None


class UserRead(UserBase):
    id: int
    role: str
    verified: bool
    credit_score: float
    created_at: datetime


