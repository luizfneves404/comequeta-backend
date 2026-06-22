"""Use case: list the message history of a 1:1 conversation."""

from datetime import datetime

from core.entities.message import Message
from core.interfaces.message_repository import MessageRepository


class ListConversation:
    """Return the message history between the user and a peer."""

    def __init__(self, messages: MessageRepository) -> None:
        self._messages = messages

    def execute(
        self,
        user_id: int,
        peer_id: int,
        before: datetime | None = None,
        limit: int = 50,
    ) -> list[Message]:
        return self._messages.list_conversation(
            user_id=user_id, peer_id=peer_id, before=before, limit=limit
        )
