"""AgriShield AI - Role-Based Access Control (RBAC) & Permissions

Defines standard roles and access verification utilities.
"""

from enum import Enum
from typing import List
from app.core.exceptions import PermissionDeniedException


class UserRole(str, Enum):
    FARMER = "farmer"
    BUYER = "buyer"
    TRANSPORTER = "transporter"
    COOPERATIVE_ADMIN = "cooperative_admin"
    PLATFORM_ADMIN = "platform_admin"


class RoleChecker:
    """Dependency for checking whether the authenticated user has any of the required roles."""

    def __init__(self, allowed_roles: List[UserRole]):
        self.allowed_roles = [r.value if isinstance(r, UserRole) else r for r in allowed_roles]

    def __call__(self, current_user) -> bool:
        user_role = current_user.role
        if isinstance(user_role, UserRole):
            user_role = user_role.value

        # Platform administrator always has superuser bypass privileges
        if user_role == UserRole.PLATFORM_ADMIN.value:
            return True

        if user_role not in self.allowed_roles:
            raise PermissionDeniedException(
                f"Operation requires one of the following roles: {', '.join(self.allowed_roles)}. Current role: {user_role}"
            )
        return True

