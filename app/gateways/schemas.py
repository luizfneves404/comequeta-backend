"""HTTP request/response models (Pydantic).

These live in the gateway layer and isolate the wire format from the domain
entities.
"""

from pydantic import BaseModel, EmailStr, Field

from app.entities.user import User


class UserCreate(BaseModel):
    email: EmailStr
    name: str = Field(min_length=1, max_length=120)
    password: str = Field(min_length=8, max_length=128)


class UserRead(BaseModel):
    id: int
    email: EmailStr
    name: str

    @classmethod
    def from_entity(cls, user: User) -> UserRead:
        assert user.id is not None
        return cls(id=user.id, email=user.email, name=user.name)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
