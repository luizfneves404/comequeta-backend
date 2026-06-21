"""Port: persistence abstraction for the Message entity.

Use cases depend on this Protocol, not on any concrete database. This keeps
the application rules independent of SQLAlchemy (Dependency Inversion).
"""

from datetime import datetime
from typing import Protocol

from app.entities.conversation import ConversationSummary
from app.entities.message import Message


class MessageRepository(Protocol):
    def save(self, message: Message) -> Message:
        """Persist a new message and return it with its assigned id."""
        ...

    def list_conversation(
        self,
        user_id: int,
        peer_id: int,
        before: datetime | None = None,
        limit: int = 50,
    ) -> list[Message]:
        """Return messages exchanged between ``user_id`` and ``peer_id``.

        Only messages created strictly before ``before`` are returned when it
        is given. Results are ordered oldest-first and capped at ``limit``
        (the most recent ``limit`` messages within the window).
        """
        ...

    def list_conversations(self, user_id: int) -> list[ConversationSummary]:
        """Return one summary per peer the user has talked with."""
        ...

    def mark_read(self, user_id: int, peer_id: int) -> int:
        """Mark messages from ``peer_id`` to ``user_id`` as read.

        Returns the number of messages updated.
        """
        ...

    def delete_conversation(self, user_id: int, peer_id: int) -> int:
        """Delete every message exchanged between the two users.

        Returns the number of messages deleted.
        """
        ...
