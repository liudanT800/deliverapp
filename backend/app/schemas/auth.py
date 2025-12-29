from pydantic import BaseModel, EmailStr

from app.schemas.base import CamelModel

class Token(CamelModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: EmailStr | None = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str

