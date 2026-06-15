"""SQLAlchemy ORM models.

These belong to the outer (infrastructure) layer and are mapped to/from the
domain entities by the repository implementations.
"""

from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True, index=True)
    name: Mapped[str] = mapped_column()
    hashed_password: Mapped[str] = mapped_column()
