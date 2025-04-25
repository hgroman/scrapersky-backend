"""
Authentication Service Module

This module provides simplified authentication functions for the application.
RBAC functionality has been removed to simplify the authentication system.
JWT authentication is used for all routes.
"""

import logging
import os
import uuid
from functools import lru_cache
from typing import Callable, Dict, List, Optional

from fastapi import Depends, HTTPException

from .jwt_auth import get_current_user

# Configure logging
logger = logging.getLogger(__name__)

# Default system user ID for API key authentication
DEFAULT_SYSTEM_USER_ID = "00000000-0000-0000-0000-000000000000"
SYSTEM_USER_ID = os.getenv("SYSTEM_USER_ID", DEFAULT_SYSTEM_USER_ID)

class AuthService:
    """
    Authentication service with JWT-only authentication.
    RBAC functionality has been removed for simplification.
    
    Note: This class preserves the method signatures from the original RBAC implementation
    to minimize changes required in router files, but the implementations have been simplified.
    """

    @staticmethod
    def _get_valid_user_id(user_id: str) -> str:
        """
        Get a valid UUID for the user ID.

        Args:
            user_id: The user ID to validate

        Returns:
            A valid UUID string
        """
        # If user_id is "api_key_user", use the system user ID
        if user_id == "api_key_user":
            return SYSTEM_USER_ID

        # Check if user_id is a valid UUID
        try:
            return str(uuid.UUID(user_id))
        except (ValueError, TypeError):
            # If not, use the system user ID
            logger.warning(f"Invalid user ID format: {user_id}. Using system user ID.")
            return SYSTEM_USER_ID

    @staticmethod
    async def get_user_permissions(user_id: str, tenant_id: str, role: Optional[str] = None) -> List[str]:
        """
        Simplified permission checker that provides a compatibility layer for RBAC removal.
        Always returns an admin permission set for authenticated users.

        Args:
            user_id: The user ID (not used in simplified implementation)
            tenant_id: The tenant ID (not used in simplified implementation)
            role: The user's role (not used in simplified implementation)

        Returns:
            List containing basic permissions for all authenticated users
        """
        # For future RBAC reintegration, restore the original implementation
        # that uses rbac_service.get_user_permissions()
        
        # Since RBAC is removed, return admin permissions for all authenticated users
        logger.debug(f"RBAC removed: Using simplified permissions for user {user_id}")
        return ["authenticated", "basic_access", "tenant_access"]

    @staticmethod
    async def check_permission(user: Dict, permission: str) -> bool:
        """
        Simplified permission check that always returns True for authenticated users.

        Args:
            user: The user dictionary from JWT
            permission: The permission to check (ignored in simplified implementation)

        Returns:
            True for all authenticated users
        """
        # API key users and authenticated users all have access
        # For future RBAC reintegration, restore permission checks using RBAC service
        
        logger.debug(f"RBAC removed: Permission {permission} check bypassed")
        return True

    @staticmethod
    def require_permission(permission: str) -> Callable:
        """
        Simplified dependency function that only checks if the user is authenticated.
        The specific permission is ignored in this simplified implementation.

        Args:
            permission: The permission name (ignored in simplified implementation)

        Returns:
            Dependency function that only verifies authentication via JWT
        """
        async def check_permission_dependency(current_user: Dict = Depends(get_current_user)) -> Dict:
            # For future RBAC reintegration, restore permission checks here
            logger.debug(f"RBAC removed: Permission '{permission}' requirement bypassed")
            
            # Just return the authenticated user without permission check
            return current_user

        return check_permission_dependency

    @staticmethod
    async def get_tenant_features(tenant_id: str) -> Dict[str, bool]:
        """
        Simplified feature flag check that assumes all features are enabled.

        Args:
            tenant_id: The tenant ID (ignored in simplified implementation)

        Returns:
            Dictionary with all requested features enabled
        """
        # For future RBAC reintegration, restore feature flag checks using feature_service
        logger.debug(f"RBAC removed: Using simplified feature flags for tenant {tenant_id}")
        
        # Return all features enabled by default
        return {"all_features": True}

    @staticmethod
    async def check_feature_enabled(tenant_id: str, feature_name: str) -> bool:
        """
        Simplified feature check that always returns True.

        Args:
            tenant_id: The tenant ID (ignored in simplified implementation)
            feature_name: The feature name (ignored in simplified implementation)

        Returns:
            True for all features
        """
        # For future RBAC reintegration, restore feature checks using feature_service
        logger.debug(f"RBAC removed: Feature '{feature_name}' check bypassed for tenant {tenant_id}")
        
        # All features are enabled in simplified implementation
        return True

    @staticmethod
    def require_feature(feature_name: str) -> Callable:
        """
        Simplified dependency function that only checks if the user is authenticated.
        The specific feature is ignored in this simplified implementation.

        Args:
            feature_name: The feature name (ignored in simplified implementation)

        Returns:
            Dependency function that only verifies authentication via JWT
        """
        async def check_feature_dependency(current_user: Dict = Depends(get_current_user)) -> Dict:
            # For future RBAC reintegration, restore feature checks here
            logger.debug(f"RBAC removed: Feature '{feature_name}' requirement bypassed")
            
            # Just return the authenticated user without feature check
            return current_user

        return check_feature_dependency

    @staticmethod
    def clear_cache():
        """
        Cache clearing stub for compatibility with existing code.
        """
        logger.debug("RBAC removed: Cache clearing bypassed (no cache exists)")
        pass