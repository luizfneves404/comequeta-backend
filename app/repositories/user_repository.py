"""Adapter: SQLAlchemy implementation of the UserRepository port."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.entities.user import User
from app.interfaces.user_repository import UserRepository
from app.repositories.models import UserModel


def _to_entity(model: UserModel) -> User:
    return User(
        id=model.id,
        email=model.email,
        name=model.name,
        hashed_password=model.hashed_password,
        bio=model.bio,
        lat=model.lat,
        lng=model.lng,
    )


class SqlAlchemyUserRepository(UserRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, user: User) -> User:
        model = UserModel(
            email=user.email,
            name=user.name,
            hashed_password=user.hashed_password,
            bio=user.bio,
        )
        self._session.add(model)
        self._session.commit()
        self._session.refresh(model)
        return _to_entity(model)

    def get_by_email(self, email: str) -> User | None:
        model = self._session.scalar(
            select(UserModel).where(UserModel.email == email)
        )
        return _to_entity(model) if model is not None else None

    def get_by_id(self, user_id: int) -> User | None:
        model = self._session.get(UserModel, user_id)
        return _to_entity(model) if model is not None else None

    def list_others(self, exclude_user_id: int) -> list[User]:
        models = self._session.scalars(
            select(UserModel)
            .where(UserModel.id != exclude_user_id)
            .order_by(UserModel.name)
        ).all()
        return [_to_entity(m) for m in models]

    def update_location(self, user_id: int, lat: float, lng: float) -> None:
        model = self._session.get(UserModel, user_id)
        if model is None:
            return
        model.lat = lat
        model.lng = lng
        self._session.commit()

    def update_profile(
        self, user_id: int, name: str, bio: str | None
    ) -> User | None:
        model = self._session.get(UserModel, user_id)
        if model is None:
            return None
        model.name = name
        model.bio = bio
        self._session.commit()
        self._session.refresh(model)
        return _to_entity(model)
