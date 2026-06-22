from app.entities.user import User
from app.usecases.delete_conversation import DeleteConversation
from app.usecases.list_conversation import ListConversation
from app.usecases.send_message import SendMessage
from tests.fakes import FakeMessageRepository, FakeUserRepository


def setup() -> tuple[FakeMessageRepository, FakeUserRepository, int, int, int]:
    users = FakeUserRepository()
    ana = users.add(User(None, "a@x.com", "Ana", "h"))
    bia = users.add(User(None, "b@x.com", "Bia", "h"))
    caio = users.add(User(None, "c@x.com", "Caio", "h"))
    messages = FakeMessageRepository()
    assert ana.id is not None and bia.id is not None and caio.id is not None
    return messages, users, ana.id, bia.id, caio.id


def test_deletes_all_messages_between_the_pair() -> None:
    messages, users, ana, bia, _ = setup()
    send = SendMessage(messages, users)
    send.execute(ana, bia, "oi")
    send.execute(bia, ana, "olá")

    deleted = DeleteConversation(messages).execute(ana, bia)

    assert deleted == 2
    assert ListConversation(messages).execute(ana, bia) == []


def test_only_deletes_the_targeted_conversation() -> None:
    messages, users, ana, bia, caio = setup()
    send = SendMessage(messages, users)
    send.execute(ana, bia, "para bia")
    send.execute(ana, caio, "para caio")

    deleted = DeleteConversation(messages).execute(ana, bia)

    assert deleted == 1
    # The Ana<->Caio conversation is untouched.
    remaining = ListConversation(messages).execute(ana, caio)
    assert [m.content for m in remaining] == ["para caio"]


def test_deleting_empty_conversation_returns_zero() -> None:
    messages, _, ana, bia, _ = setup()

    deleted = DeleteConversation(messages).execute(ana, bia)

    assert deleted == 0
