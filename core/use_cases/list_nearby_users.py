"""Use case: list other users whose reported position is within a radius.

Powers the proximity map (US03/US04): a user sees — and is seen by — only the
people within their radius, using each user's last reported location.
"""

import math

from core.entities.user import User
from core.interfaces.user_repository import UserRepository

_EARTH_RADIUS_M = 6_371_000.0


def _haversine_meters(
    lat1: float, lng1: float, lat2: float, lng2: float
) -> float:
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lng2 - lng1)
    a = (
        math.sin(d_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    )
    return _EARTH_RADIUS_M * 2 * math.asin(min(1.0, math.sqrt(a)))


class ListNearbyUsers:
    def __init__(self, users: UserRepository) -> None:
        self._users = users

    def execute(
        self,
        exclude_user_id: int,
        lat: float,
        lng: float,
        radius_m: float,
    ) -> list[User]:
        nearby: list[User] = []
        for user in self._users.list_others(exclude_user_id):
            if user.lat is None or user.lng is None:
                continue
            if _haversine_meters(lat, lng, user.lat, user.lng) <= radius_m:
                nearby.append(user)
        return nearby
