from __future__ import annotations


class DomainError(Exception):
    """Base class for domain-level errors (invariants, transitions, etc.)."""


class ValidationError(DomainError):
    pass


class InvalidStateTransition(DomainError):
    pass


class NotFoundError(DomainError):
    pass


class ConflictError(DomainError):
    pass
