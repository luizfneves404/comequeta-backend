"""Domain entity: Message.

Pure domain object with no framework dependencies (no SQLAlchemy, no FastAPI).
Represents a single 1:1 chat message between two users.
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class Message:
    """A 1:1 chat message exchanged between two users.

    ``read_at`` is ``None`` until the recipient marks the conversation as read.
    """

    id: int | None
    sender_id: int
    recipient_id: int
    content: str
    created_at: datetime
    read_at: datetime | None = None
