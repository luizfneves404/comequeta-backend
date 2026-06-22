"""Gateway: authentication routes (register + login)."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.gateways.deps import get_authenticate_user, get_register_user
from app.gateways.schemas import Token, UserCreate, UserRead
from app.usecases.authenticate_user import AuthenticateUser
from app.usecases.errors import (
    EmailAlreadyExistsError,
    InvalidCredentialsError,
)
from app.usecases.register_user import RegisterUser

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register", response_model=UserRead, status_code=status.HTTP_201_CREATED
)
def register(
    payload: UserCreate,
    register_user: Annotated[RegisterUser, Depends(get_register_user)],
) -> UserRead:
    try:
        user = register_user.execute(
            email=payload.email,
            name=payload.name,
            password=payload.password,
            bio=payload.bio,
        )
    except EmailAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        ) from None
    return UserRead.from_entity(user)


@router.post("/login", response_model=Token)
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    authenticate_user: Annotated[
        AuthenticateUser, Depends(get_authenticate_user)
    ],
) -> Token:
    # OAuth2PasswordRequestForm uses "username"; we treat it as the email.
    try:
        access_token = authenticate_user.execute(
            email=form_data.username,
            password=form_data.password,
        )
    except InvalidCredentialsError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None
    return Token(access_token=access_token)
