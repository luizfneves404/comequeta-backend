"""Gateway: 1:1 chat routes (REST) and the WebSocket endpoint.

REST routes are authenticated with the existing JWT dependency. The WebSocket
endpoint validates the JWT passed as a query parameter (``?token=<jwt>``),
registers the connection in the in-process ConnectionManager and routes
inbound frames through the same SendMessage use case used by the REST API.
"""

from datetime import datetime
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    WebSocket,
    WebSocketDisconnect,
    status,
)
from jwt.exceptions import InvalidTokenError
from sqlalchemy.orm import Session

from app.config import settings
from app.dtos.schemas import (
    ConversationRead,
    MessageCreate,
    MessageRead,
)
from app.gateways.connection_manager import manager
from app.gateways.deps import (
    get_current_user,
    get_delete_conversation,
    get_list_conversation,
    get_list_conversations,
    get_mark_read,
    get_send_message,
)
from core.entities.user import User
from core.interfaces.security import TokenProvider
from core.use_cases.delete_conversation import DeleteConversation
from core.use_cases.errors import RecipientNotFoundError
from core.use_cases.list_conversation import ListConversation
from core.use_cases.list_conversations import ListConversations
from core.use_cases.mark_read import MarkRead
from core.use_cases.send_message import SendMessage
from infra.external_systems.db import get_session
from infra.external_systems.repositories.message_repository import (
    SqlMessageRepository,
)
from infra.external_systems.repositories.user_repository import (
    SqlAlchemyUserRepository,
)
from infra.external_systems.security.jwt_provider import JwtTokenProvider

router = APIRouter(prefix="/chat", tags=["chat"])


@router.get("/conversations", response_model=list[ConversationRead])
def list_conversations(
    current_user: Annotated[User, Depends(get_current_user)],
    use_case: Annotated[ListConversations, Depends(get_list_conversations)],
) -> list[ConversationRead]:
    assert current_user.id is not None
    summaries = use_case.execute(current_user.id)
    return [ConversationRead.from_entity(s) for s in summaries]


@router.get("/messages/{peer_id}", response_model=list[MessageRead])
def list_conversation(
    peer_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    use_case: Annotated[ListConversation, Depends(get_list_conversation)],
    before: datetime | None = None,
    limit: int = 50,
) -> list[MessageRead]:
    assert current_user.id is not None
    messages = use_case.execute(
        user_id=current_user.id,
        peer_id=peer_id,
        before=before,
        limit=limit,
    )
    return [MessageRead.from_entity(m) for m in messages]


@router.post(
    "/messages",
    response_model=MessageRead,
    status_code=status.HTTP_201_CREATED,
)
async def send_message(
    payload: MessageCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    use_case: Annotated[SendMessage, Depends(get_send_message)],
) -> MessageRead:
    assert current_user.id is not None
    try:
        message = use_case.execute(
            sender_id=current_user.id,
            recipient_id=payload.recipient_id,
            content=payload.content,
        )
    except RecipientNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipient not found",
        ) from None

    read = MessageRead.from_entity(message)
    frame = {"type": "message", "message": read.model_dump(mode="json")}
    await manager.send_to_user(message.recipient_id, frame)
    return read


@router.post(
    "/messages/{peer_id}/read", status_code=status.HTTP_204_NO_CONTENT
)
def mark_read(
    peer_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    use_case: Annotated[MarkRead, Depends(get_mark_read)],
) -> None:
    assert current_user.id is not None
    use_case.execute(user_id=current_user.id, peer_id=peer_id)


@router.delete("/messages/{peer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_conversation(
    peer_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    use_case: Annotated[DeleteConversation, Depends(get_delete_conversation)],
) -> None:
    """Delete the whole conversation with ``peer_id``."""
    assert current_user.id is not None
    use_case.execute(user_id=current_user.id, peer_id=peer_id)


def _token_provider() -> TokenProvider:
    return JwtTokenProvider(
        secret_key=settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
        expire_minutes=settings.access_token_expire_minutes,
    )


ws_router = APIRouter()


@ws_router.websocket("/ws/chat")
async def chat_websocket(
    websocket: WebSocket,
    token: Annotated[str, Query()],
    session: Annotated[Session, Depends(get_session)],
) -> None:
    tokens = _token_provider()
    users = SqlAlchemyUserRepository(session)
    try:
        subject = tokens.decode(token)
        user = users.get_by_id(int(subject))
    except InvalidTokenError, ValueError:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    if user is None or user.id is None:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    user_id = user.id
    send_message = SendMessage(SqlMessageRepository(session), users)
    await manager.connect(user_id, websocket)
    try:
        while True:
            frame = await websocket.receive_json()
            if frame.get("type") != "message":
                continue
            recipient_id = frame.get("recipient_id")
            content = frame.get("content")
            if not isinstance(recipient_id, int) or not isinstance(
                content, str
            ):
                continue
            try:
                message = send_message.execute(
                    sender_id=user_id,
                    recipient_id=recipient_id,
                    content=content,
                )
            except RecipientNotFoundError:
                await websocket.send_json(
                    {"type": "error", "detail": "Recipient not found"}
                )
                continue

            read = MessageRead.from_entity(message)
            out = {
                "type": "message",
                "message": read.model_dump(mode="json"),
            }
            await manager.send_to_user(recipient_id, out)
            await websocket.send_json(out)
    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(user_id, websocket)
