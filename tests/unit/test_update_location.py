from app.entities.user import User
from app.usecases.update_location import UpdateLocation
from tests.fakes import FakeUserRepository


def make_use_case() -> tuple[UpdateLocation, FakeUserRepository, int]:
    users = FakeUserRepository()
    ana = users.add(User(None, "ana@example.com", "Ana", "h"))
    assert ana.id is not None
    return UpdateLocation(users), users, ana.id


def test_persists_reported_position() -> None:
    update, users, ana = make_use_case()

    update.execute(ana, lat=-23.5, lng=-46.6)

    stored = users.get_by_id(ana)
    assert stored is not None
    assert stored.lat == -23.5
    assert stored.lng == -46.6


def test_overwrites_previous_position() -> None:
    update, users, ana = make_use_case()
    update.execute(ana, lat=-23.5, lng=-46.6)

    update.execute(ana, lat=10.0, lng=20.0)

    stored = users.get_by_id(ana)
    assert stored is not None
    assert (stored.lat, stored.lng) == (10.0, 20.0)


def test_unknown_user_is_a_noop() -> None:
    update, users, _ = make_use_case()

    # Must not raise for a non-existent user.
    update.execute(999, lat=1.0, lng=2.0)

    assert users.get_by_id(999) is None
