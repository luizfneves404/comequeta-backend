"""Adapter: password hashing backed by pwdlib (Argon2).

Implements the PasswordHasher port. passlib is no longer maintained, so this
uses pwdlib's recommended configuration (Argon2id).
"""

from pwdlib import PasswordHash

from app.interfaces.security import PasswordHasher


class PwdlibPasswordHasher(PasswordHasher):
    def __init__(self) -> None:
        self._hasher = PasswordHash.recommended()

    def hash(self, plain_password: str) -> str:
        return self._hasher.hash(plain_password)

    def verify(self, plain_password: str, hashed_password: str) -> bool:
        return self._hasher.verify(plain_password, hashed_password)
