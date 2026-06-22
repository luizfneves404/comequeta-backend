"""Use case: list a user's conversation summaries."""

from core.entities.conversation import ConversationSummary
from core.interfaces.message_repository import MessageRepository


class ListConversations:
    """Return one summary per peer the user has talked with."""

    def __init__(self, messages: MessageRepository) -> None:
        self._messages = messages

    def execute(self, user_id: int) -> list[ConversationSummary]:
        return self._messages.list_conversations(user_id)
