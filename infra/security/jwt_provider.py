"""Adapter: JWT access tokens backed by PyJWT.

Implements the TokenProvider port.
"""

from datetime import UTC, datetime, timedelta

import jwt
from jwt.exceptions import InvalidTokenError

from core.interfaces.security import TokenProvider


class JwtTokenProvider(TokenProvider):
    def __init__(
        self, secret_key: str, algorithm: str, expire_minutes: int
    ) -> None:
        self._secret_key = secret_key
        self._algorithm = algorithm
        self._expire_minutes = expire_minutes

    def create_access_token(self, subject: str) -> str:
        now = datetime.now(UTC)
        payload = {
            "sub": subject,
            "iat": now,
            "exp": now + timedelta(minutes=self._expire_minutes),
        }
        return jwt.encode(payload, self._secret_key, algorithm=self._algorithm)

    def decode(self, token: str) -> str:
        payload = jwt.decode(
            token, self._secret_key, algorithms=[self._algorithm]
        )
        subject = payload.get("sub")
        if not isinstance(subject, str):
            raise InvalidTokenError("Token is missing the subject claim")
        return subject
