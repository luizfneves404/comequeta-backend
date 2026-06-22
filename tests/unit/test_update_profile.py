import pytest

from core.entities.user import User
from core.use_cases.errors import UserNotFoundError
from core.use_cases.update_profile import UpdateProfile
from tests.fakes import FakeUserRepository


def make_use_case() -> tuple[UpdateProfile, FakeUserRepository, int]:
    users = FakeUserRepository()
    ana = users.add(User(None, "ana@example.com", "Ana", "h"))
    assert ana.id is not None
    return UpdateProfile(users), users, ana.id


def test_updates_name_and_bio() -> None:
    update, users, ana = make_use_case()

    result = update.execute(ana, name="Ana Maria", bio="Vizinha do 201.")

    assert result.name == "Ana Maria"
    assert result.bio == "Vizinha do 201."
    stored = users.get_by_id(ana)
    assert stored is not None
    assert stored.name == "Ana Maria"
    assert stored.bio == "Vizinha do 201."


def test_can_clear_bio() -> None:
    update, users, ana = make_use_case()
    update.execute(ana, name="Ana", bio="texto")

    result = update.execute(ana, name="Ana", bio=None)

    assert result.bio is None


def test_does_not_change_other_fields() -> None:
    update, users, ana = make_use_case()

    update.execute(ana, name="Ana", bio="oi")

    stored = users.get_by_id(ana)
    assert stored is not None
    # Email and password are untouched by a profile update.
    assert stored.email == "ana@example.com"
    assert stored.hashed_password == "h"


def test_raises_for_unknown_user() -> None:
    update, _, _ = make_use_case()

    with pytest.raises(UserNotFoundError):
        update.execute(999, name="Ghost", bio=None)
