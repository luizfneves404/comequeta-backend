"""Port: persistence abstraction for the User entity.

Use cases depend on this Protocol, not on any concrete database. This is the
Dependency Inversion Principle in action: the inner layer defines the contract
and the outer layer (repositories) implements it.
"""

from typing import Protocol

from core.entities.user import User


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

    def update_location(self, user_id: int, lat: float, lng: float) -> None:
        """Persist the user's last reported position."""
        ...

    def update_profile(
        self, user_id: int, name: str, bio: str | None
    ) -> User | None:
        """Update the user's editable profile fields and return the result.

        Returns the updated user, or None if no user has ``user_id``.
        """
        ...
