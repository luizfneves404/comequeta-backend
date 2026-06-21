"""Use case: send a 1:1 message."""

from datetime import UTC, datetime

from app.entities.message import Message
from app.interfaces.message_repository import MessageRepository
from app.interfaces.user_repository import UserRepository
from app.usecases.errors import RecipientNotFoundError


class SendMessage:
    """Validate the recipient exists and persist a new message.

    Depends only on abstractions, so it is unit-testable with fakes.
    """

    def __init__(
        self, messages: MessageRepository, users: UserRepository
    ) -> None:
        self._messages = messages
        self._users = users

    def execute(
        self, sender_id: int, recipient_id: int, content: str
    ) -> Message:
        if self._users.get_by_id(recipient_id) is None:
            raise RecipientNotFoundError(recipient_id)

        message = Message(
            id=None,
            sender_id=sender_id,
            recipient_id=recipient_id,
            content=content,
            created_at=datetime.now(UTC),
            read_at=None,
        )
        return self._messages.save(message)
