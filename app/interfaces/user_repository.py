"""Port: persistence abstraction for the User entity.

Use cases depend on this Protocol, not on any concrete database. This is the
Dependency Inversion Principle in action: the inner layer defines the contract
and the outer layer (repositories) implements it.
"""

from typing import Protocol

from app.entities.user import User


class UserRepository(Protocol):
    def add(self, user: User) -> User:
        """Persist a new user and return it with its assigned id."""
        ...

    def get_by_email(self, email: str) -> User | None:
        """Return the user with the given email, or None if not found."""
        ...

    def get_by_id(self, user_id: int) -> User | None:
        """Return the user with the given id, or None if not found."""
        ...

    def list_others(self, exclude_user_id: int) -> list[User]:
        """Return all users except the one with `exclude_user_id`."""
        ...
