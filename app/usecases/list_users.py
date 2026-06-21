"""Use case: list the registered users other than the requester.

Powers the "start a new conversation" picker on the client, so a user can chat
with any other real account.
"""

from app.entities.user import User
from app.interfaces.user_repository import UserRepository


class ListUsers:
    def __init__(self, users: UserRepository) -> None:
        self._users = users

    def execute(self, exclude_user_id: int) -> list[User]:
        return self._users.list_others(exclude_user_id)
