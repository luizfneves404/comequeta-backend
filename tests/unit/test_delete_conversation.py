from core.entities.user import User
from core.use_cases.delete_conversation import DeleteConversation
from core.use_cases.list_conversation import ListConversation
from core.use_cases.send_message import SendMessage
from tests.fakes import FakeMessageRepository, FakeUserRepository


def setup() -> tuple[FakeMessageRepository, FakeUserRepository, int, int]:
    users = FakeUserRepository()
    ana = users.add(User(None, "a@x.com", "Ana", "h"))
    bia = users.add(User(None, "b@x.com", "Bia", "h"))
    messages = FakeMessageRepository()
    assert ana.id is not None and bia.id is not None
    return messages, users, ana.id, bia.id


def test_delete_conversation_removes_messages_between_pair() -> None:
    messages, users, ana, bia = setup()
    send = SendMessage(messages, users)
    send.execute(ana, bia, "first")
    send.execute(bia, ana, "second")

    deleted = DeleteConversation(messages).execute(ana, bia)

    assert deleted == 2
    assert ListConversation(messages).execute(ana, bia) == []


def test_delete_conversation_leaves_other_conversations_untouched() -> None:
    messages, users, ana, bia = setup()
    carla = users.add(User(None, "c@x.com", "Carla", "h"))
    assert carla.id is not None
    send = SendMessage(messages, users)
    send.execute(ana, bia, "to bia")
    send.execute(ana, carla.id, "to carla")

    deleted = DeleteConversation(messages).execute(ana, bia)

    assert deleted == 1
    assert ListConversation(messages).execute(ana, carla.id) != []


def test_delete_conversation_with_no_messages_returns_zero() -> None:
    messages, _, ana, bia = setup()

    deleted = DeleteConversation(messages).execute(ana, bia)

    assert deleted == 0
