"""SQLAlchemy ORM models.

These belong to the outer (infrastructure) layer and are mapped to/from the
domain entities by the repository implementations.
"""

from datetime import datetime

from sqlalchemy import ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column

from infra.external_systems.db import Base


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True, index=True)
    name: Mapped[str] = mapped_column()
    hashed_password: Mapped[str] = mapped_column()
    lat: Mapped[float | None] = mapped_column(default=None)
    lng: Mapped[float | None] = mapped_column(default=None)


class MessageModel(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    sender_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    recipient_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), index=True
    )
    content: Mapped[str] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(index=True)
    read_at: Mapped[datetime | None] = mapped_column(default=None)

    __table_args__ = (
        Index(
            "ix_messages_sender_recipient_created",
            "sender_id",
            "recipient_id",
            "created_at",
        ),
    )
