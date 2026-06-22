from infra.security.password_hasher import (
    PwdlibPasswordHasher,
)


def test_hash_is_not_plaintext_and_verifies() -> None:
    hasher = PwdlibPasswordHasher()

    hashed = hasher.hash("secret123")

    assert hashed != "secret123"
    assert hasher.verify("secret123", hashed)
    assert not hasher.verify("wrong-password", hashed)
