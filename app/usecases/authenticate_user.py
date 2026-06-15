"""Use case: authenticate a user and issue an access token."""

from app.interfaces.security import PasswordHasher, TokenProvider
from app.interfaces.user_repository import UserRepository
from app.usecases.errors import InvalidCredentials


class AuthenticateUser:
    """Verify credentials and return a signed access token.

    Depends only on abstractions, so it is unit-testable with fakes.
    """

    def __init__(
        self,
        users: UserRepository,
        hasher: PasswordHasher,
        tokens: TokenProvider,
    ) -> None:
        self._users = users
        self._hasher = hasher
        self._tokens = tokens

    def execute(self, email: str, password: str) -> str:
        user = self._users.get_by_email(email)
        if user is None or not self._hasher.verify(password, user.hashed_password):
            raise InvalidCredentials()

        assert user.id is not None  # persisted users always have an id
        return self._tokens.create_access_token(subject=str(user.id))
