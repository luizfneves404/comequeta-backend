"""Application-level errors.

These are framework-agnostic: use cases raise them and the gateway layer maps
them to HTTP responses. The inner layers stay unaware of HTTP.
"""


class ApplicationError(Exception):
    """Base class for errors raised by use cases."""


class EmailAlreadyExistsError(ApplicationError):
    """Raised when registering a user with an email that is already taken."""


class InvalidCredentialsError(ApplicationError):
    """Raised when authentication fails (unknown email or wrong password)."""
