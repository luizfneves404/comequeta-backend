"""Use case: mark a conversation's incoming messages as read."""

from core.interfaces.message_repository import MessageRepository


class MarkRead:
    """Mark messages from a peer to the user as read."""

    def __init__(self, messages: MessageRepository) -> None:
        self._messages = messages

    def execute(self, user_id: int, peer_id: int) -> int:
        return self._messages.mark_read(user_id=user_id, peer_id=peer_id)
