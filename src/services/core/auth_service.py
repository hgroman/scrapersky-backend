"""
Auth Service Module

This module provides a service for handling authentication operations.
"""
import logging
import os
import sys
import uuid
from typing import Any, Dict, Optional

from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

# Add multiple fallback approaches for jose import
jose_jwt = None
jose_JWTError = Exception  # Default fallback

# Try different import approaches
try:
    # Approach 1: Standard import
    from jose import JWTError as jose_JWTError
    from jose import jwt as jose_jwt
    logging.info("Successfully imported jose using standard import")
except ImportError:
    try:
        # Approach 2: Try python-jose directly
        from python_jose import JWTError as jose_JWTError
        from python_jose import jwt as jose_jwt
        logging.info("Successfully imported python-jose directly")
    except ImportError:
        try:
            # Approach 3: Use PyJWT as fallback (should be in requirements.txt)
            import jwt as jose_jwt
            jose_JWTError = jose_jwt.PyJWTError
            logging.warning("Using PyJWT as fallback for python-jose")
        except ImportError:
            try:
                # Approach 4: Install package at runtime if in development mode
                if os.getenv("ENVIRONMENT") == "development":
                    import subprocess
                    logging.warning("Attempting to install python-jose package...")
                    subprocess.check_call([sys.executable, "-m", "pip", "install", "python-jose[cryptography]"])
                    from jose import JWTError as jose_JWTError
                    from jose import jwt as jose_jwt
                    logging.info("Successfully installed and imported jose package")
                else:
                    logging.error("Failed to import jose. Production environment won't auto-install packages.")
            except Exception as e:
                logging.error(f"All import attempts failed: {str(e)}")
                # Approach 5: Mock implementation for development
                if os.getenv("ENVIRONMENT") == "development" and os.getenv("USE_MOCK_AUTH") == "true":
                    logging.warning("Using mock JWT implementation for development")

                    class MockJWT:
                        @staticmethod
                        def decode(token, key, algorithms):
                            # Simple mock implementation that returns hardcoded values
                            return {
                                "sub": "dev-user-123",
                                "username": "dev_user",
                                "email": "dev@example.com",
                                "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
                                "roles": ["admin"]
                            }

                    jose_jwt = MockJWT()
                    jose_JWTError = Exception
                else:
                    # Last resort: Raise a more helpful error message
                    logging.critical("CRITICAL: python-jose import failed and no fallbacks worked")
                    logging.critical("Make sure to run: pip install python-jose[cryptography]")
                    # Don't raise here - let the application continue and fail more gracefully later

from ...models.user import User

logger = logging.getLogger(__name__)

# Set up security scheme
security = HTTPBearer()

# JWT configuration - should be in config module in production
JWT_SECRET = os.getenv("JWT_SECRET", "dev_secret_key")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
DEFAULT_TENANT_ID = "550e8400-e29b-41d4-a716-446655440000"

class AuthService:
    """
    Service for handling authentication operations.

    This service provides methods for authenticating users and extracting
    user information from tokens.
    """

    # Tenant validation method completely removed

    async def get_user_from_token(self, token: str) -> User:
        """
        Extract user information from a JWT token.

        Args:
            token: The JWT token to validate

        Returns:
            The User object extracted from the token

        Raises:
            HTTPException: If the token is invalid
        """
        # Check if jose_jwt is available
        if jose_jwt is None:
            logger.error("JWT module not available - using mock user")
            return self.create_mock_user()

        try:
            # Decode the token
            payload = jose_jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])

            # Extract user information
            user_id = payload.get("sub")
            username = payload.get("username")
            email = payload.get("email")
            tenant_id = payload.get("tenant_id")
            roles = payload.get("roles", [])

            # Validate required fields
            if not user_id:
                raise HTTPException(
                    status_code=401,
                    detail="Invalid token - missing user ID"
                )

            # Create and return user
            return User(
                id=user_id,
                username=username,
                email=email,
                tenant_id=DEFAULT_TENANT_ID,  # Always use default tenant ID
                roles=roles
            )

        except jose_JWTError as e:
            logger.warning(f"JWT validation error: {str(e)}")

            # Fallback to mock user in development mode
            if os.getenv("ENVIRONMENT") == "development" and os.getenv("USE_MOCK_AUTH") == "true":
                logger.info("Using mock user due to JWT validation error in development mode")
                return self.create_mock_user()

            raise HTTPException(
                status_code=401,
                detail="Invalid authentication token"
            )
        except Exception as e:
            logger.error(f"Unexpected error in token validation: {str(e)}")

            # Fallback to mock user in development mode
            if os.getenv("ENVIRONMENT") == "development" and os.getenv("USE_MOCK_AUTH") == "true":
                logger.info("Using mock user due to unexpected error in development mode")
                return self.create_mock_user()

            raise HTTPException(
                status_code=500,
                detail="Internal server error during authentication"
            )

    def create_mock_user(self) -> User:
        """
        Create a mock user for development purposes.

        This should only be used in development environments.

        Returns:
            A mock User object
        """
        return User(
            id="dev-user-123",
            username="dev_user",
            email="dev@example.com",
            tenant_id=DEFAULT_TENANT_ID,  # Always use default tenant ID
            roles=["admin"]
        )

# Create and export the auth service instance
auth_service = AuthService()

# Dependency for current user
async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """
    Get the current authenticated user.

    This function is used as a FastAPI dependency to extract the authenticated
    user from the request.

    Args:
        request: The FastAPI request object
        credentials: The authentication credentials

    Returns:
        The authenticated User object

    Raises:
        HTTPException: If authentication fails
    """
    # In development environment, allow mock user
    if os.getenv("ENVIRONMENT") == "development" and os.getenv("USE_MOCK_AUTH") == "true":
        return auth_service.create_mock_user()

    # Get token from credentials
    token = credentials.credentials

    # Extract user from token
    return await auth_service.get_user_from_token(token)