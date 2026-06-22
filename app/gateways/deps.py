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
from core.entities.user import User
from core.interfaces.message_repository import MessageRepository
from core.interfaces.security import PasswordHasher, TokenProvider
from core.interfaces.user_repository import UserRepository
from core.use_cases.authenticate_user import AuthenticateUser
from core.use_cases.delete_conversation import DeleteConversation
from core.use_cases.list_conversation import ListConversation
from core.use_cases.list_conversations import ListConversations
from core.use_cases.list_nearby_users import ListNearbyUsers
from core.use_cases.list_users import ListUsers
from core.use_cases.mark_read import MarkRead
from core.use_cases.register_user import RegisterUser
from core.use_cases.send_message import SendMessage
from core.use_cases.update_location import UpdateLocation
from infra.external_systems.db import get_session
from infra.external_systems.repositories.message_repository import (
    SqlMessageRepository,
)
from infra.external_systems.repositories.user_repository import (
    SqlAlchemyUserRepository,
)
from infra.external_systems.security.jwt_provider import JwtTokenProvider
from infra.external_systems.security.password_hasher import (
    PwdlibPasswordHasher,
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_user_repository(
    session: Annotated[Session, Depends(get_session)],
) -> UserRepository:
    return SqlAlchemyUserRepository(session)


def get_list_users(
    users: Annotated[UserRepository, Depends(get_user_repository)],
) -> ListUsers:
    return ListUsers(users)


def get_list_nearby_users(
    users: Annotated[UserRepository, Depends(get_user_repository)],
) -> ListNearbyUsers:
    return ListNearbyUsers(users)


def get_update_location(
    users: Annotated[UserRepository, Depends(get_user_repository)],
) -> UpdateLocation:
    return UpdateLocation(users)


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


def get_message_repository(
    session: Annotated[Session, Depends(get_session)],
) -> MessageRepository:
    return SqlMessageRepository(session)


def get_send_message(
    messages: Annotated[MessageRepository, Depends(get_message_repository)],
    users: Annotated[UserRepository, Depends(get_user_repository)],
) -> SendMessage:
    return SendMessage(messages, users)


def get_list_conversation(
    messages: Annotated[MessageRepository, Depends(get_message_repository)],
) -> ListConversation:
    return ListConversation(messages)


def get_list_conversations(
    messages: Annotated[MessageRepository, Depends(get_message_repository)],
) -> ListConversations:
    return ListConversations(messages)


def get_mark_read(
    messages: Annotated[MessageRepository, Depends(get_message_repository)],
) -> MarkRead:
    return MarkRead(messages)


def get_delete_conversation(
    messages: Annotated[MessageRepository, Depends(get_message_repository)],
) -> DeleteConversation:
    return DeleteConversation(messages)


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
