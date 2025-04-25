"""
User Model Module

This module provides a model for representing an authenticated user.
"""
from typing import List, Optional

from pydantic import BaseModel, Field


class User(BaseModel):
    """
    Model representing an authenticated user.

    This model stores information about an authenticated user, including
    their ID, username, email, tenant ID, and roles.
    """

    id: str = Field(..., description="Unique identifier for the user")
    username: Optional[str] = Field(None, description="Username for the user")
    email: Optional[str] = Field(None, description="Email address for the user")
    tenant_id: Optional[str] = Field(None, description="Tenant ID that the user belongs to")
    roles: List[str] = Field(default_factory=list, description="Roles assigned to the user")

    def has_role(self, role: str) -> bool:
        """
        Check if the user has a specific role.

        Args:
            role: The role to check for

        Returns:
            True if the user has the role, False otherwise
        """
        return role in self.roles

    def is_admin(self) -> bool:
        """
        Check if the user has the admin role.

        Returns:
            True if the user is an admin, False otherwise
        """
        return self.has_role("admin")