"""AgriShield AI - Custom Domain Exceptions

Provides standard, structured exception classes for centralized handling.
"""

from typing import Any, Dict, Optional


class AgriShieldException(Exception):
    """Base exception for all AgriShield application errors."""

    def __init__(
        self,
        message: str = "An unexpected error occurred",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class EntityNotFoundException(AgriShieldException):
    """Raised when a requested resource does not exist."""

    def __init__(self, entity_name: str, identifier: Any):
        super().__init__(
            message=f"{entity_name} with identifier '{identifier}' was not found.",
            status_code=404,
            details={"entity": entity_name, "identifier": str(identifier)},
        )


class EntityAlreadyExistsException(AgriShieldException):
    """Raised when attempting to create a duplicate unique resource."""

    def __init__(self, entity_name: str, field: str, value: Any):
        super().__init__(
            message=f"{entity_name} with {field} '{value}' already exists.",
            status_code=409,
            details={"entity": entity_name, "field": field, "value": str(value)},
        )


class AuthenticationFailedException(AgriShieldException):
    """Raised when authentication credentials are invalid."""

    def __init__(self, message: str = "Invalid email/phone or password."):
        super().__init__(
            message=message,
            status_code=401,
            details={"headers": {"WWW-Authenticate": "Bearer"}},
        )


class PermissionDeniedException(AgriShieldException):
    """Raised when user lacks the required role or permission."""

    def __init__(self, message: str = "Permission denied for this operation."):
        super().__init__(
            message=message,
            status_code=403,
            details={"error": "forbidden"},
        )


class InvalidTokenException(AgriShieldException):
    """Raised when a JWT token is invalid or tampered with."""

    def __init__(self, message: str = "Could not validate authentication token."):
        super().__init__(
            message=message,
            status_code=401,
            details={"headers": {"WWW-Authenticate": "Bearer"}},
        )


class TokenRevokedException(AgriShieldException):
    """Raised when a JWT or refresh token has been revoked / logged out."""

    def __init__(self, message: str = "Token has been revoked. Please log in again."):
        super().__init__(
            message=message,
            status_code=401,
            details={"headers": {"WWW-Authenticate": "Bearer"}},
        )


class DoubleAllocationException(AgriShieldException):
    """Raised when attempting to allocate more surplus quantity than available."""

    def __init__(self, listing_id: Any, requested_qty: float, available_qty: float):
        super().__init__(
            message=f"Transaction conflict: Requested {requested_qty} exceeds available {available_qty}.",
            status_code=409,
            details={
                "listing_id": str(listing_id),
                "requested_qty": requested_qty,
                "available_qty": available_qty,
            },
        )


class StorageTamperException(AgriShieldException):
    """Raised when storage verification hash checks detect data tampering."""

    def __init__(self, batch_id: Any, message: str = "Cryptographic integrity check failed."):
        super().__init__(
            message=f"Storage batch '{batch_id}': {message}",
            status_code=409,
            details={"batch_id": str(batch_id), "verification_status": "TAMPERED"},
        )


class RateLimitExceededException(AgriShieldException):
    """Raised when user or client exceeds request rate limits."""

    def __init__(self, retry_after: int = 60):
        super().__init__(
            message=f"Too many requests. Please retry in {retry_after} seconds.",
            status_code=429,
            details={"retry_after": retry_after},
        )

