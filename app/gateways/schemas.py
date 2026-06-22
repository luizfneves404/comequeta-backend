"""HTTP request/response models (Pydantic).

These live in the gateway layer and isolate the wire format from the domain
entities.
"""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.entities.conversation import ConversationSummary
from app.entities.message import Message
from app.entities.user import User


class UserCreate(BaseModel):
    email: EmailStr
    name: str = Field(min_length=1, max_length=120)
    password: str = Field(min_length=8, max_length=128)
    bio: str | None = Field(default=None, max_length=500)


class ProfileUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    bio: str | None = Field(default=None, max_length=500)


class UserRead(BaseModel):
    id: int
    email: EmailStr
    name: str
    bio: str | None = None

    @classmethod
    def from_entity(cls, user: User) -> UserRead:
        assert user.id is not None
        return cls(id=user.id, email=user.email, name=user.name, bio=user.bio)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LocationUpdate(BaseModel):
    lat: float = Field(ge=-90, le=90)
    lng: float = Field(ge=-180, le=180)


class NearbyUserRead(BaseModel):
    id: int
    name: str
    lat: float
    lng: float

    @classmethod
    def from_entity(cls, user: User) -> NearbyUserRead:
        assert (
            user.id is not None
            and user.lat is not None
            and user.lng is not None
        )
        return cls(id=user.id, name=user.name, lat=user.lat, lng=user.lng)


class MessageCreate(BaseModel):
    recipient_id: int
    content: str = Field(min_length=1, max_length=4000)


class MessageRead(BaseModel):
    id: int
    sender_id: int
    recipient_id: int
    content: str
    created_at: datetime
    read_at: datetime | None

    @classmethod
    def from_entity(cls, message: Message) -> MessageRead:
        assert message.id is not None
        return cls(
            id=message.id,
            sender_id=message.sender_id,
            recipient_id=message.recipient_id,
            content=message.content,
            created_at=message.created_at,
            read_at=message.read_at,
        )


class ConversationRead(BaseModel):
    peer_id: int
    peer_name: str
    last_message: str
    last_at: datetime
    unread: int

    @classmethod
    def from_entity(cls, summary: ConversationSummary) -> ConversationRead:
        return cls(
            peer_id=summary.peer_id,
            peer_name=summary.peer_name,
            last_message=summary.last_message,
            last_at=summary.last_at,
            unread=summary.unread,
        )
