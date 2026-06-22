import pytest

from core.use_cases.authenticate_user import AuthenticateUser
from core.use_cases.errors import InvalidCredentialsError
from core.use_cases.register_user import RegisterUser
from tests.fakes import (
    FakePasswordHasher,
    FakeTokenProvider,
    FakeUserRepository,
)


def make_context() -> AuthenticateUser:
    users = FakeUserRepository()
    hasher = FakePasswordHasher()
    RegisterUser(users, hasher).execute(
        email="ana@example.com", name="Ana", password="secret123"
    )
    return AuthenticateUser(users, hasher, FakeTokenProvider())


def test_returns_token_for_valid_credentials() -> None:
    authenticate = make_context()

    token = authenticate.execute(email="ana@example.com", password="secret123")

    # Subject is the user id (the first registered user gets id 1).
    assert token == "token::1"


def test_rejects_wrong_password() -> None:
    authenticate = make_context()

    with pytest.raises(InvalidCredentialsError):
        authenticate.execute(
            email="ana@example.com", password="wrong-password"
        )


def test_rejects_unknown_email() -> None:
    authenticate = make_context()

    with pytest.raises(InvalidCredentialsError):
        authenticate.execute(email="nobody@example.com", password="secret123")
