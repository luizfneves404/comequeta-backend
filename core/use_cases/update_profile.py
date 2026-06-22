"""Use case: update the current user's editable profile fields.

Lets a user change their display name and bio. Depends only on the
UserRepository abstraction, so it is unit-testable with fakes.
"""

from core.entities.user import User
from core.interfaces.user_repository import UserRepository
from core.use_cases.errors import UserNotFoundError


class UpdateProfile:
    def __init__(self, users: UserRepository) -> None:
        self._users = users

    def execute(self, user_id: int, name: str, bio: str | None) -> User:
        updated = self._users.update_profile(user_id, name, bio)
        if updated is None:
            raise UserNotFoundError(user_id)
        return updated
