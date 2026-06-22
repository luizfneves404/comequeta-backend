"""Use case: register a new user."""

from core.entities.user import User
from core.interfaces.security import PasswordHasher
from core.interfaces.user_repository import UserRepository
from core.use_cases.errors import EmailAlreadyExistsError


class RegisterUser:
    """Create a new user account.

    Depends only on abstractions (UserRepository, PasswordHasher), so it can be
    unit-tested with in-memory fakes and no database.
    """

    def __init__(self, users: UserRepository, hasher: PasswordHasher) -> None:
        self._users = users
        self._hasher = hasher

    def execute(
        self,
        email: str,
        name: str,
        password: str,
        bio: str | None = None,
    ) -> User:
        if self._users.get_by_email(email) is not None:
            raise EmailAlreadyExistsError(email)

        user = User(
            id=None,
            email=email,
            name=name,
            hashed_password=self._hasher.hash(password),
            bio=bio,
        )
        return self._users.add(user)
