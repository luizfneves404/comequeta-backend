from core.entities.user import User
from core.use_cases.list_conversation import ListConversation
from core.use_cases.list_conversations import ListConversations
from core.use_cases.mark_read import MarkRead
from core.use_cases.send_message import SendMessage
from tests.fakes import FakeMessageRepository, FakeUserRepository


def setup() -> tuple[FakeMessageRepository, FakeUserRepository, int, int]:
    users = FakeUserRepository()
    ana = users.add(User(None, "a@x.com", "Ana", "h"))
    bia = users.add(User(None, "b@x.com", "Bia", "h"))
    messages = FakeMessageRepository()
    assert ana.id is not None and bia.id is not None
    messages.names = {ana.id: "Ana", bia.id: "Bia"}
    return messages, users, ana.id, bia.id


def test_history_returns_messages_in_order() -> None:
    messages, users, ana, bia = setup()
    send = SendMessage(messages, users)
    send.execute(ana, bia, "first")
    send.execute(bia, ana, "second")

    history = ListConversation(messages).execute(ana, bia)

    assert [m.content for m in history] == ["first", "second"]


def test_conversations_summary_has_unread_counts() -> None:
    messages, users, ana, bia = setup()
    send = SendMessage(messages, users)
    send.execute(bia, ana, "u1")
    send.execute(bia, ana, "u2")

    summaries = ListConversations(messages).execute(ana)

    assert len(summaries) == 1
    summary = summaries[0]
    assert summary.peer_id == bia
    assert summary.peer_name == "Bia"
    assert summary.last_message == "u2"
    assert summary.unread == 2


def test_mark_read_clears_unread() -> None:
    messages, users, ana, bia = setup()
    send = SendMessage(messages, users)
    send.execute(bia, ana, "u1")

    updated = MarkRead(messages).execute(user_id=ana, peer_id=bia)

    assert updated == 1
    summaries = ListConversations(messages).execute(ana)
    assert summaries[0].unread == 0
