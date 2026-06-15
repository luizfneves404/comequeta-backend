"""Dependency injection wiring for the gateway layer.

This is the composition root: it builds the concrete adapters (SQLAlchemy
repository, pwdlib hasher, JWT provider) and injects them into use cases. The
inner layers never reference these factories.
"""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_session
from app.entities.user import User
from app.interfaces.security import PasswordHasher, TokenProvider
from app.interfaces.user_repository import UserRepository
from app.repositories.user_repository import SqlAlchemyUserRepository
from app.security.jwt_provider import JwtTokenProvider
from app.security.password_hasher import PwdlibPasswordHasher
from app.usecases.authenticate_user import AuthenticateUser
from app.usecases.register_user import RegisterUser

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_user_repository(
    session: Annotated[Session, Depends(get_session)],
) -> UserRepository:
    return SqlAlchemyUserRepository(session)


def get_password_hasher() -> PasswordHasher:
    return PwdlibPasswordHasher()


def get_token_provider() -> TokenProvider:
    return JwtTokenProvider(
        secret_key=settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
        expire_minutes=settings.access_token_expire_minutes,
    )


def get_register_user(
    users: Annotated[UserRepository, Depends(get_user_repository)],
    hasher: Annotated[PasswordHasher, Depends(get_password_hasher)],
) -> RegisterUser:
    return RegisterUser(users, hasher)


def get_authenticate_user(
    users: Annotated[UserRepository, Depends(get_user_repository)],
    hasher: Annotated[PasswordHasher, Depends(get_password_hasher)],
    tokens: Annotated[TokenProvider, Depends(get_token_provider)],
) -> AuthenticateUser:
    return AuthenticateUser(users, hasher, tokens)


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    users: Annotated[UserRepository, Depends(get_user_repository)],
    tokens: Annotated[TokenProvider, Depends(get_token_provider)],
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        subject = tokens.decode(token)
        user = users.get_by_id(int(subject))
    except (InvalidTokenError, ValueError):  # fmt: skip
        raise credentials_exception from None
    if user is None:
        raise credentials_exception
    return user
