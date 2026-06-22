from app.entities.user import User
from app.usecases.list_nearby_users import ListNearbyUsers
from tests.fakes import FakeUserRepository

# Reference point (downtown São Paulo) used by all cases below.
_LAT, _LNG = -23.5, -46.6


def make_use_case() -> tuple[ListNearbyUsers, FakeUserRepository, int]:
    users = FakeUserRepository()
    me = users.add(User(None, "me@example.com", "Me", "h"))
    assert me.id is not None
    return ListNearbyUsers(users), users, me.id


def _add(users: FakeUserRepository, name: str, lat, lng) -> None:
    users.add(User(None, f"{name}@x.com", name, "h", lat=lat, lng=lng))


def test_includes_users_within_radius() -> None:
    nearby, users, me = make_use_case()
    _add(users, "Close", -23.5001, -46.6001)  # a few metres away

    result = nearby.execute(me, _LAT, _LNG, radius_m=500)

    assert [u.name for u in result] == ["Close"]


def test_excludes_users_outside_radius() -> None:
    nearby, users, me = make_use_case()
    _add(users, "Far", -23.9, -46.9)  # ~50 km away

    result = nearby.execute(me, _LAT, _LNG, radius_m=500)

    assert result == []


def test_excludes_users_without_a_reported_location() -> None:
    nearby, users, me = make_use_case()
    _add(users, "NoLoc", None, None)

    result = nearby.execute(me, _LAT, _LNG, radius_m=500)

    assert result == []


def test_excludes_the_requester_even_if_nearby() -> None:
    nearby, users, me = make_use_case()
    # Give the requester a location at the exact reference point.
    users.update_location(me, _LAT, _LNG)
    _add(users, "Close", _LAT, _LNG)

    result = nearby.execute(me, _LAT, _LNG, radius_m=500)

    assert [u.name for u in result] == ["Close"]
    assert all(u.id != me for u in result)
