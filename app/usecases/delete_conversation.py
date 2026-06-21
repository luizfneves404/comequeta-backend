"""Use case: delete a 1:1 conversation (all messages between two users)."""

from app.interfaces.message_repository import MessageRepository


class DeleteConversation:
    def __init__(self, messages: MessageRepository) -> None:
        self._messages = messages

    def execute(self, user_id: int, peer_id: int) -> int:
        return self._messages.delete_conversation(user_id, peer_id)
