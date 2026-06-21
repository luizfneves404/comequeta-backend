"""Adapter: SQLAlchemy implementation of the MessageRepository port."""

from datetime import datetime

from sqlalchemy import and_, or_, select, update
from sqlalchemy.orm import Session

from app.entities.conversation import ConversationSummary
from app.entities.message import Message
from app.interfaces.message_repository import MessageRepository
from app.repositories.models import MessageModel, UserModel


def _to_entity(model: MessageModel) -> Message:
    return Message(
        id=model.id,
        sender_id=model.sender_id,
        recipient_id=model.recipient_id,
        content=model.content,
        created_at=model.created_at,
        read_at=model.read_at,
    )


class SqlMessageRepository(MessageRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, message: Message) -> Message:
        model = MessageModel(
            sender_id=message.sender_id,
            recipient_id=message.recipient_id,
            content=message.content,
            created_at=message.created_at,
            read_at=message.read_at,
        )
        self._session.add(model)
        self._session.commit()
        self._session.refresh(model)
        return _to_entity(model)

    def list_conversation(
        self,
        user_id: int,
        peer_id: int,
        before: datetime | None = None,
        limit: int = 50,
    ) -> list[Message]:
        between = or_(
            and_(
                MessageModel.sender_id == user_id,
                MessageModel.recipient_id == peer_id,
            ),
            and_(
                MessageModel.sender_id == peer_id,
                MessageModel.recipient_id == user_id,
            ),
        )
        stmt = select(MessageModel).where(between)
        if before is not None:
            stmt = stmt.where(MessageModel.created_at < before)
        # Take the most recent ``limit`` within the window, then return them
        # oldest-first for natural display order.
        stmt = stmt.order_by(MessageModel.created_at.desc()).limit(limit)
        models = list(self._session.scalars(stmt))
        models.reverse()
        return [_to_entity(m) for m in models]

    def list_conversations(self, user_id: int) -> list[ConversationSummary]:
        stmt = (
            select(MessageModel)
            .where(
                or_(
                    MessageModel.sender_id == user_id,
                    MessageModel.recipient_id == user_id,
                )
            )
            .order_by(MessageModel.created_at.asc())
        )
        messages = list(self._session.scalars(stmt))

        last_by_peer: dict[int, MessageModel] = {}
        unread_by_peer: dict[int, int] = {}
        for m in messages:
            peer = m.recipient_id if m.sender_id == user_id else m.sender_id
            last_by_peer[peer] = m
            if m.recipient_id == user_id and m.read_at is None:
                unread_by_peer[peer] = unread_by_peer.get(peer, 0) + 1

        peer_ids = list(last_by_peer.keys())
        names: dict[int, str] = {}
        if peer_ids:
            rows = self._session.scalars(
                select(UserModel).where(UserModel.id.in_(peer_ids))
            )
            names = {u.id: u.name for u in rows}

        summaries = [
            ConversationSummary(
                peer_id=peer,
                peer_name=names.get(peer, ""),
                last_message=last.content,
                last_at=last.created_at,
                unread=unread_by_peer.get(peer, 0),
            )
            for peer, last in last_by_peer.items()
        ]
        summaries.sort(key=lambda s: s.last_at, reverse=True)
        return summaries

    def mark_read(self, user_id: int, peer_id: int) -> int:
        now = datetime.now()
        stmt = (
            update(MessageModel)
            .where(
                MessageModel.sender_id == peer_id,
                MessageModel.recipient_id == user_id,
                MessageModel.read_at.is_(None),
            )
            .values(read_at=now)
        )
        result = self._session.execute(stmt)
        self._session.commit()
        return result.rowcount  # ty: ignore[unresolved-attribute]
