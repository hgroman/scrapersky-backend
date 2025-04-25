"""
User Context Service

This service provides a centralized way to handle user context across all modules.
It abstracts away the details of how user IDs are obtained and validated,
providing a consistent interface for all modules that need user information.
"""

import logging
import os
import uuid
from typing import Any, Dict, Optional, Union

# Configure logging
logger = logging.getLogger(__name__)

class UserContextService:
    """
    Service for handling user context across the application.

    This service provides methods to:
    - Get a valid user ID for database operations
    - Validate user IDs
    - Handle fallbacks for missing user IDs
    """

    def __init__(self):
        """Initialize the UserContextService."""
        # Cache environment variables for better performance
        self._environment = os.getenv("ENVIRONMENT", "development")
        self._dev_user_id = os.getenv("DEV_USER_ID")
        self._system_user_id = os.getenv("SYSTEM_USER_ID")

        # Log configuration on startup
        self._log_configuration()

    def _log_configuration(self):
        """Log the current configuration for debugging."""
        logger.info(f"UserContextService initialized with environment: {self._environment}")
        logger.info(f"Development user ID available: {self._dev_user_id is not None}")
        logger.info(f"System user ID available: {self._system_user_id is not None}")

    def is_valid_uuid(self, user_id: Optional[str]) -> bool:
        """
        Check if a user ID is a valid UUID.

        Args:
            user_id: The user ID to validate

        Returns:
            True if the user ID is a valid UUID, False otherwise
        """
        if not user_id:
            return False

        try:
            uuid_obj = uuid.UUID(user_id)
            return True
        except (ValueError, AttributeError, TypeError):
            return False

    def get_valid_user_id(self,
                         user_id: Optional[str] = None,
                         current_user: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """
        Get a valid user ID for database operations.

        This method tries multiple sources for a valid user ID:
        1. The provided user_id parameter
        2. The current_user dictionary (from JWT authentication)
        3. Fallback to system or development user IDs based on environment

        Args:
            user_id: Optional explicit user ID
            current_user: Optional current user dictionary from authentication

        Returns:
            A valid user ID as a string, or None if no valid ID could be found

        Raises:
            ValueError: If no valid user ID could be determined and strict mode is enabled
        """
        # Try explicit user_id first
        if user_id:
            if self.is_valid_uuid(user_id):
                logger.debug(f"Using provided user_id: {user_id}")
                return str(uuid.UUID(user_id))  # Normalize UUID format
            elif user_id == "api_key_user":
                # Special case for API key authentication
                system_id = self._system_user_id or self._dev_user_id
                if system_id and self.is_valid_uuid(system_id):
                    logger.debug(f"Using system user ID for API key authentication: {system_id}")
                    return str(uuid.UUID(system_id))

        # Try current_user from JWT authentication
        if current_user and current_user.get('id'):
            user_id_from_jwt = current_user.get('id')
            if self.is_valid_uuid(user_id_from_jwt):
                logger.debug(f"Using user ID from JWT: {user_id_from_jwt}")
                return str(uuid.UUID(user_id_from_jwt))

        # Fallback to environment-specific defaults
        if self._environment == "development" and self._dev_user_id and self.is_valid_uuid(self._dev_user_id):
            logger.debug(f"Using development user ID: {self._dev_user_id}")
            return str(uuid.UUID(self._dev_user_id))

        if self._system_user_id and self.is_valid_uuid(self._system_user_id):
            logger.debug(f"Using system user ID: {self._system_user_id}")
            return str(uuid.UUID(self._system_user_id))

        # No valid user ID found
        logger.error("No valid user ID available")
        return None

    def get_user_name(self,
                     user_name: Optional[str] = None,
                     current_user: Optional[Dict[str, Any]] = None) -> str:
        """
        Get a user name for attribution.

        Args:
            user_name: Optional explicit user name
            current_user: Optional current user dictionary from authentication

        Returns:
            A user name string, defaulting to "System" if none provided
        """
        if user_name:
            return user_name

        if current_user and current_user.get('name'):
            return current_user.get('name') or "System"

        return "System"

    def get_tenant_id(self, current_user: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """
        Get the tenant ID from the current user context.

        Args:
            current_user: Current user dictionary from authentication

        Returns:
            The tenant ID as a string, or None if not available
        """
        if not current_user:
            return None

        # Extract tenant ID from user context
        tenant_id = None

        # Try different possible locations in the user object
        if current_user.get('tenant_id'):
            tenant_id = current_user.get('tenant_id')
        elif current_user.get('app_metadata', {}).get('tenant_id'):
            tenant_id = current_user.get('app_metadata', {}).get('tenant_id')
        elif current_user.get('user_metadata', {}).get('tenant_id'):
            tenant_id = current_user.get('user_metadata', {}).get('tenant_id')

        # Return the tenant ID if found, None otherwise
        return tenant_id

# Create a singleton instance
user_context_service = UserContextService()
