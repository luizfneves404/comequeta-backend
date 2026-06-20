"""In-memory test doubles implementing the inner-layer ports.

Because the use cases depend only on the interfaces, they can be exercised with
these fakes — no database, no real crypto — which is the whole point of the
architecture.
"""

from dataclasses import replace

from app.entities.user import User
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
