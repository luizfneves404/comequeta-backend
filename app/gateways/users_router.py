"""Gateway: user routes."""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.entities.user import User
from app.gateways.deps import get_current_user, get_list_users
from app.gateways.schemas import UserRead
from app.usecases.list_users import ListUsers

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserRead)
def read_current_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> UserRead:
    return UserRead.from_entity(current_user)


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
