"""Gateway: user routes."""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.entities.user import User
from app.gateways.deps import get_current_user
from app.gateways.schemas import UserRead

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserRead)
def read_current_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> UserRead:
    return UserRead.from_entity(current_user)
