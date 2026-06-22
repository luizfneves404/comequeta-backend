from core.entities.user import User
from core.use_cases.list_nearby_users import ListNearbyUsers
from core.use_cases.list_users import ListUsers
from core.use_cases.update_location import UpdateLocation
from tests.fakes import FakeUserRepository


def setup() -> tuple[FakeUserRepository, int, int]:
    users = FakeUserRepository()
    ana = users.add(User(None, "a@x.com", "Ana", "h"))
    bia = users.add(User(None, "b@x.com", "Bia", "h"))
    assert ana.id is not None and bia.id is not None
    return users, ana.id, bia.id


def test_list_users_excludes_requester() -> None:
    users, ana, bia = setup()

    others = ListUsers(users).execute(ana)

    assert [u.id for u in others] == [bia]


def test_update_location_persists_position() -> None:
    users, ana, _ = setup()

    UpdateLocation(users).execute(ana, lat=-22.9, lng=-43.2)

    updated = users.get_by_id(ana)
    assert updated is not None
    assert updated.lat == -22.9
    assert updated.lng == -43.2


def test_list_nearby_users_filters_by_radius() -> None:
    users, ana, bia = setup()
    UpdateLocation(users).execute(ana, lat=-22.9068, lng=-43.1729)
    UpdateLocation(users).execute(bia, lat=-22.9068, lng=-43.1729)
    carla = users.add(User(None, "c@x.com", "Carla", "h"))
    assert carla.id is not None
    UpdateLocation(users).execute(carla.id, lat=40.7128, lng=-74.0060)

    nearby = ListNearbyUsers(users).execute(
        exclude_user_id=ana, lat=-22.9068, lng=-43.1729, radius_m=1_000
    )

    assert [u.id for u in nearby] == [bia]


def test_list_nearby_users_ignores_users_without_location() -> None:
    users, ana, _ = setup()

    nearby = ListNearbyUsers(users).execute(
        exclude_user_id=ana, lat=-22.9068, lng=-43.1729, radius_m=1_000
    )

    assert nearby == []
