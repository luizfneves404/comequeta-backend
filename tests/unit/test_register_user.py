import pytest

from app.usecases.errors import EmailAlreadyExistsError
from app.usecases.register_user import RegisterUser
from tests.fakes import FakePasswordHasher, FakeUserRepository


def make_use_case() -> tuple[RegisterUser, FakeUserRepository]:
    users = FakeUserRepository()
    return RegisterUser(users, FakePasswordHasher()), users


def test_registers_user_with_hashed_password() -> None:
    register, users = make_use_case()

    user = register.execute(
        email="ana@example.com", name="Ana", password="secret123"
    )

    assert user.id is not None
    assert user.email == "ana@example.com"
    assert user.name == "Ana"
    # The stored password must be hashed, never the plaintext.
    assert user.hashed_password == "hashed::secret123"
    assert users.get_by_id(user.id) == user


def test_registers_user_with_bio() -> None:
    register, users = make_use_case()

    user = register.execute(
        email="ana@example.com",
        name="Ana",
        password="secret123",
        bio="Adoro plantar e trocar mudas.",
    )

    assert user.bio == "Adoro plantar e trocar mudas."
    assert user.id is not None
    assert users.get_by_id(user.id) == user


def test_bio_defaults_to_none_when_omitted() -> None:
    register, _ = make_use_case()

    user = register.execute(
        email="ana@example.com", name="Ana", password="secret123"
    )

    assert user.bio is None


def test_rejects_duplicate_email() -> None:
    register, _ = make_use_case()
    register.execute(email="ana@example.com", name="Ana", password="secret123")

    with pytest.raises(EmailAlreadyExistsError):
        register.execute(
            email="ana@example.com", name="Other", password="another12"
        )
