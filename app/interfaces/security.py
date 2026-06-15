"""Ports for security concerns: password hashing and token issuing.

Use cases depend on these abstractions; concrete adapters live in app/security.
"""

from typing import Protocol


class PasswordHasher(Protocol):
    def hash(self, plain_password: str) -> str:
        """Return a secure hash for the given plaintext password."""
        ...

    def verify(self, plain_password: str, hashed_password: str) -> bool:
        """Return True if the plaintext matches the stored hash."""
        ...


class TokenProvider(Protocol):
    def create_access_token(self, subject: str) -> str:
        """Issue a signed access token identifying the given subject."""
        ...

    def decode(self, token: str) -> str:
        """Return the subject encoded in the token.

        Raises InvalidTokenError (or a subclass) if the token is invalid or
        expired.
        """
        ...
