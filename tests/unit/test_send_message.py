import pytest

from app.entities.user import User
from app.usecases.errors import RecipientNotFoundError
from app.usecases.send_message import SendMessage
from tests.fakes import FakeMessageRepository, FakeUserRepository


def make_use_case() -> tuple[SendMessage, FakeMessageRepository, int, int]:
    users = FakeUserRepository()
    sender = users.add(User(None, "a@x.com", "Ana", "h"))
    recipient = users.add(User(None, "b@x.com", "Bia", "h"))
    messages = FakeMessageRepository()
    assert sender.id is not None and recipient.id is not None
    return SendMessage(messages, users), messages, sender.id, recipient.id


def test_persists_message() -> None:
    send, messages, sender_id, recipient_id = make_use_case()

    msg = send.execute(sender_id, recipient_id, "hi")

    assert msg.id is not None
    assert msg.sender_id == sender_id
    assert msg.recipient_id == recipient_id
    assert msg.content == "hi"
    assert msg.read_at is None
    assert messages.list_conversation(sender_id, recipient_id) == [msg]


def test_rejects_unknown_recipient() -> None:
    send, _, sender_id, _ = make_use_case()

    with pytest.raises(RecipientNotFoundError):
        send.execute(sender_id, 9999, "hi")
