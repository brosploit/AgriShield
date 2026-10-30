"""AgriShield AI - FastAPI Dependencies

Provides database session injection, JWT authentication, user context,
role-based authorization, and rate limiting.
"""

from datetime import datetime, timezone
from typing import Generator, List, Union
from fastapi import Depends, Header, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
import jwt

from app.core.config import settings
from app.core.database import SessionLocal, get_db
from app.core.exceptions import (
    AuthenticationFailedException,
    EntityNotFoundException,
    InvalidTokenException,
    PermissionDeniedException,
    RateLimitExceededException,
)
from app.core.permissions import UserRole
from app.core.security import decode_token
from app.models.user import User

# HTTP Bearer scheme
security_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Validate Bearer JWT access token and return active User instance."""
    if not credentials or not credentials.credentials:
        raise AuthenticationFailedException("Authentication required. Please provide a Bearer token.")

    token = credentials.credentials
    try:
        payload = decode_token(token)
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token has expired. Please refresh your token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except (jwt.InvalidTokenError, Exception):
        raise InvalidTokenException("Invalid or corrupted authentication token.")

    token_type = payload.get("type")
    if token_type != "access":
        raise InvalidTokenException("Invalid token type. Access token expected.")

    user_id = payload.get("sub")
    if not user_id:
        raise InvalidTokenException("Token missing subject identifier.")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise EntityNotFoundException("User", user_id)

    if not user.is_active:
        raise PermissionDeniedException("Account has been deactivated. Please contact support.")

    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Ensure current user is active."""
    if not current_user.is_active:
        raise PermissionDeniedException("Account inactive.")
    return current_user


def require_roles(allowed_roles: List[Union[UserRole, str]]):
    """Dependency factory restricting endpoint access to specific roles.

    Platform Admin always passes.
    """
    valid_roles = [r.value if isinstance(r, UserRole) else r for r in allowed_roles]

    def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        user_role = current_user.role
        if isinstance(user_role, UserRole):
            user_role = user_role.value

        if user_role == UserRole.PLATFORM_ADMIN.value:
            return current_user

        if user_role not in valid_roles:
            raise PermissionDeniedException(
                f"Access forbidden: Required role in {valid_roles}, current role is '{user_role}'."
            )
        return current_user

    return role_checker


# In-memory sliding rate limiter per client IP
_rate_limit_store = {}


class RateLimiter:
    """In-memory rate limiter for low-bandwidth rural operations."""

    def __init__(self, max_requests: int = 60, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds

    def __call__(self, request: Request):
        client_ip = request.client.host if request.client else "unknown"
        now = datetime.now(timezone.utc).timestamp()
        history = _rate_limit_store.setdefault(client_ip, [])

        # Filter timestamps outside window
        history = [ts for ts in history if now - ts < self.window_seconds]
        _rate_limit_store[client_ip] = history

        if len(history) >= self.max_requests:
            raise RateLimitExceededException(retry_after=int(self.window_seconds - (now - history[0])))

        history.append(now)

