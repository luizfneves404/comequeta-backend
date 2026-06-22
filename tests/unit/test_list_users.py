from app.entities.user import User
from app.usecases.list_users import ListUsers
from tests.fakes import FakeUserRepository


def make_use_case() -> tuple[ListUsers, FakeUserRepository, dict[str, int]]:
    users = FakeUserRepository()
    ids: dict[str, int] = {}
    for name, email in [
        ("Ana", "ana@example.com"),
        ("Bruno", "bruno@example.com"),
        ("Carla", "carla@example.com"),
    ]:
        user = users.add(User(None, email, name, "h"))
        assert user.id is not None
        ids[name] = user.id
    return ListUsers(users), users, ids


def test_lists_everyone_except_the_requester() -> None:
    list_users, _, ids = make_use_case()

    others = list_users.execute(exclude_user_id=ids["Ana"])

    names = {u.name for u in others}
    assert names == {"Bruno", "Carla"}


def test_excludes_only_the_requester() -> None:
    list_users, _, ids = make_use_case()

    others = list_users.execute(exclude_user_id=ids["Bruno"])

    assert all(u.id != ids["Bruno"] for u in others)
    assert len(others) == 2


def test_empty_when_no_other_users() -> None:
    users = FakeUserRepository()
    solo = users.add(User(None, "solo@example.com", "Solo", "h"))
    assert solo.id is not None

    others = ListUsers(users).execute(exclude_user_id=solo.id)

    assert others == []
