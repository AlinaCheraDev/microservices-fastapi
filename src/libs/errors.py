"""Errors the service layer raises when a request can't be carried out.

They describe what went wrong in business terms, not HTTP: a service never imports
FastAPI. The global exception handler (still to be written) is the one place that
maps each class to a status code, e.g. NotFoundError -> 404, ConflictError -> 409.

Shared by every service, so the same kind of failure gets the same status everywhere.
"""


class DomainError(Exception):
    """Base class. `message` is safe to show to the client."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class NotFoundError(DomainError):
    """The requested thing doesn't exist, or was soft-deleted. -> 404"""


class ConflictError(DomainError):
    """The request clashes with existing data, e.g. an email already in use. -> 409"""


class InvalidInputError(DomainError):
    """Well-formed input that refers to something invalid, e.g. an unknown permission id. -> 422"""


class ForbiddenError(DomainError):
    """The caller may not do this, e.g. an admin deleting their own account. -> 403"""
