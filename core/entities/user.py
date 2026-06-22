"""Domain entity: User.

Pure domain object with no framework dependencies (no SQLAlchemy, no FastAPI,
no hashing library). This is the innermost layer of the architecture.
"""

from dataclasses import dataclass


@dataclass
class User:
    """A registered user of the application.

    The entity stores the already-hashed password; it does not know which
    hashing algorithm produced it — that is a concern of an outer layer.
    """

    id: int | None
    email: str
    name: str
    hashed_password: str
    # Free-text self description shown on the user's profile (optional).
    bio: str | None = None
    # Last reported position (set when the user opens the map).
    lat: float | None = None
    lng: float | None = None
