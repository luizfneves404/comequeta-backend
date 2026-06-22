"""Use case: persist the current user's last reported position."""

from core.interfaces.user_repository import UserRepository


class UpdateLocation:
    def __init__(self, users: UserRepository) -> None:
        self._users = users

    def execute(self, user_id: int, lat: float, lng: float) -> None:
        self._users.update_location(user_id, lat, lng)
