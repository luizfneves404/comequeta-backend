import pytest
from jwt.exceptions import InvalidTokenError

from infra.external_systems.security.jwt_provider import JwtTokenProvider


def make_provider(expire_minutes: int = 60) -> JwtTokenProvider:
    return JwtTokenProvider(
        secret_key="test-secret-key-at-least-32-bytes-long!",
        algorithm="HS256",
        expire_minutes=expire_minutes,
    )


def test_roundtrip_encodes_and_decodes_subject() -> None:
    provider = make_provider()

    token = provider.create_access_token(subject="42")

    assert provider.decode(token) == "42"


def test_rejects_token_signed_with_other_secret() -> None:
    token = make_provider().create_access_token(subject="42")
    other = JwtTokenProvider(
        secret_key="a-different-secret-key-32-bytes-long!!!",
        algorithm="HS256",
        expire_minutes=60,
    )

    with pytest.raises(InvalidTokenError):
        other.decode(token)


def test_rejects_expired_token() -> None:
    provider = make_provider(expire_minutes=-1)
    token = provider.create_access_token(subject="42")

    with pytest.raises(InvalidTokenError):
        provider.decode(token)


def test_rejects_malformed_token() -> None:
    with pytest.raises(InvalidTokenError):
        make_provider().decode("not-a-jwt")
