"""In-memory test doubles implementing the inner-layer ports.

Because the use cases depend only on the interfaces, they can be exercised with
these fakes — no database, no real crypto — which is the whole point of the
architecture.
"""

from dataclasses import replace
from datetime import datetime

from app.entities.conversation import ConversationSummary
from app.entities.message import Message
from app.entities.user import User
from app.interfaces.message_repository import MessageRepository
from app.interfaces.security import PasswordHasher, TokenProvider
from app.interfaces.user_repository import UserRepository


class FakeUserRepository(UserRepository):
    def __init__(self) -> None:
        self._users: dict[int, User] = {}
        self._next_id = 1

    def add(self, user: User) -> User:
        stored = replace(user, id=self._next_id)
        self._users[self._next_id] = stored
        self._next_id += 1
        return stored

    def get_by_email(self, email: str) -> User | None:
        return next(
            (u for u in self._users.values() if u.email == email), None
        )

    def get_by_id(self, user_id: int) -> User | None:
        return self._users.get(user_id)

    def list_others(self, exclude_user_id: int) -> list[User]:
        return [u for uid, u in self._users.items() if uid != exclude_user_id]

    def update_location(self, user_id: int, lat: float, lng: float) -> None:
        user = self._users.get(user_id)
        if user is not None:
            self._users[user_id] = replace(user, lat=lat, lng=lng)


class FakeMessageRepository(MessageRepository):
    def __init__(self) -> None:
        self._messages: list[Message] = []
        self._next_id = 1
        # Optional registry of peer_id -> name, for conversation summaries.
        self.names: dict[int, str] = {}

    def save(self, message: Message) -> Message:
        stored = replace(message, id=self._next_id)
        self._messages.append(stored)
        self._next_id += 1
        return stored

    def list_conversation(
        self,
        user_id: int,
        peer_id: int,
        before: datetime | None = None,
        limit: int = 50,
    ) -> list[Message]:
        pair = {user_id, peer_id}
        msgs = [
            m
            for m in self._messages
            if {m.sender_id, m.recipient_id} == pair
            and (before is None or m.created_at < before)
        ]
        msgs.sort(key=lambda m: m.created_at)
        return msgs[-limit:]

    def list_conversations(self, user_id: int) -> list[ConversationSummary]:
        last: dict[int, Message] = {}
        unread: dict[int, int] = {}
        for m in sorted(self._messages, key=lambda m: m.created_at):
            if user_id not in {m.sender_id, m.recipient_id}:
                continue
            peer = m.recipient_id if m.sender_id == user_id else m.sender_id
            last[peer] = m
            if m.recipient_id == user_id and m.read_at is None:
                unread[peer] = unread.get(peer, 0) + 1
        summaries = [
            ConversationSummary(
                peer_id=peer,
                peer_name=self.names.get(peer, ""),
                last_message=msg.content,
                last_at=msg.created_at,
                unread=unread.get(peer, 0),
            )
            for peer, msg in last.items()
        ]
        summaries.sort(key=lambda s: s.last_at, reverse=True)
        return summaries

    def mark_read(self, user_id: int, peer_id: int) -> int:
        count = 0
        now = datetime.now()
        for i, m in enumerate(self._messages):
            if (
                m.sender_id == peer_id
                and m.recipient_id == user_id
                and m.read_at is None
            ):
                self._messages[i] = replace(m, read_at=now)
                count += 1
        return count

    def delete_conversation(self, user_id: int, peer_id: int) -> int:
        pair = {user_id, peer_id}
        before = len(self._messages)
        self._messages = [
            m for m in self._messages if {m.sender_id, m.recipient_id} != pair
        ]
        return before - len(self._messages)


class FakePasswordHasher(PasswordHasher):
    """Reversible 'hash' for tests: prefix the plaintext."""

    def hash(self, plain_password: str) -> str:
        return f"hashed::{plain_password}"

    def verify(self, plain_password: str, hashed_password: str) -> bool:
        return hashed_password == f"hashed::{plain_password}"


class FakeTokenProvider(TokenProvider):
    def create_access_token(self, subject: str) -> str:
        return f"token::{subject}"

    def decode(self, token: str) -> str:
        return token.removeprefix("token::")
