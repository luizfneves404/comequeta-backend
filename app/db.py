"""SQLAlchemy engine, session factory and the declarative base.

This is infrastructure (a detail), kept out of the inner layers. Repositories
depend on the ORM session; use cases and entities never import from here.
"""

from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings

# check_same_thread=False is needed for SQLite when the connection is shared
# across FastAPI's threadpool. Harmless for our single-process MVP.
connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}

engine = create_engine(settings.database_url, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    """Declarative base for all ORM models."""


def get_session() -> Iterator[Session]:
    """FastAPI dependency that yields a transactional database session."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
