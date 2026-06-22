"""Gateway: user routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.dtos.schemas import LocationUpdate, NearbyUserRead, UserRead
from app.gateways.deps import (
    get_current_user,
    get_list_nearby_users,
    get_list_users,
    get_update_location,
)
from core.entities.user import User
from core.use_cases.list_nearby_users import ListNearbyUsers
from core.use_cases.list_users import ListUsers
from core.use_cases.update_location import UpdateLocation

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserRead)
def read_current_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> UserRead:
    return UserRead.from_entity(current_user)


@router.put("/me/location", status_code=status.HTTP_204_NO_CONTENT)
def update_my_location(
    payload: LocationUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    use_case: Annotated[UpdateLocation, Depends(get_update_location)],
) -> None:
    """Report the current user's position (called when they open the map)."""
    assert current_user.id is not None
    use_case.execute(current_user.id, payload.lat, payload.lng)


@router.get("/nearby", response_model=list[NearbyUserRead])
def list_nearby(
    lat: float,
    lng: float,
    current_user: Annotated[User, Depends(get_current_user)],
    use_case: Annotated[ListNearbyUsers, Depends(get_list_nearby_users)],
    radius_m: float = 500,
) -> list[NearbyUserRead]:
    """Other users with a reported position within ``radius_m``."""
    assert current_user.id is not None
    nearby = use_case.execute(current_user.id, lat, lng, radius_m)
    return [NearbyUserRead.from_entity(user) for user in nearby]


@router.get("", response_model=list[UserRead])
def list_users(
    current_user: Annotated[User, Depends(get_current_user)],
    use_case: Annotated[ListUsers, Depends(get_list_users)],
) -> list[UserRead]:
    """List other registered users, so the client can start a conversation."""
    assert current_user.id is not None
    return [
        UserRead.from_entity(user)
        for user in use_case.execute(current_user.id)
    ]
