"""
JWT Authentication Module

This module provides JWT authentication with Supabase, including:
- JWT token validation with proper audience handling
- API key fallback authentication
- Tenant ID resolution and validation
- Detailed error logging and debugging

Usage:
    from fastapi import Depends
    from src.auth.jwt_auth import get_current_user

    @router.get("/your-endpoint")
    async def your_endpoint(current_user: dict = Depends(get_current_user)):
        tenant_id = current_user.get("tenant_id")
        # Use tenant_id for data isolation
"""

from fastapi import Depends, HTTPException, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Optional
import logging
import uuid
import json
import jwt
import os
import base64

from ..db.sb_connection import db

# Configure logging
logger = logging.getLogger(__name__)

# Security setup for JWT authentication
security = HTTPBearer()

# Default tenant ID used as fallback
DEFAULT_TENANT_ID = "550e8400-e29b-41d4-a716-446655440000"

def is_valid_uuid(val: str) -> bool:
    """Check if a string is a valid UUID."""
    try:
        uuid.UUID(str(val))
        return True
    except (ValueError, AttributeError, TypeError):
        return False

def extract_api_key(credentials: str) -> Optional[str]:
    """Extract API key from credentials string, handling Bearer prefix."""
    if not credentials:
        return None

    # Strip 'Bearer ' prefix if present
    if credentials.startswith("Bearer "):
        credentials = credentials[7:]

    return credentials.strip()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    x_tenant_id: Optional[str] = Header(None)
) -> Dict:
    """
    Authenticate user via JWT token with fallback to API key.

    Args:
        credentials: The HTTP Authorization credentials
        x_tenant_id: Optional tenant ID header

    Returns:
        Dict containing user information including tenant_id

    Raises:
        HTTPException: If authentication fails
    """
    try:
        # Log authentication attempt
        auth_type = "Bearer token" if credentials.credentials.startswith("Bearer ") else "API key"
        logger.info(f"Authentication attempt using {auth_type}")

        # Extract API key if present (handling Bearer prefix)
        api_key = extract_api_key(credentials.credentials)

        # Get JWT secret from environment
        jwt_secret = os.getenv("SUPABASE_JWT_SECRET")
        if not jwt_secret:
            logger.error("SUPABASE_JWT_SECRET environment variable not configured")

            # Try to continue with API key authentication
            api_key_from_env = os.getenv("SCRAPER_API_KEY")
            if api_key and api_key_from_env and api_key == api_key_from_env:
                logger.info("Using API key authentication as fallback due to missing JWT secret")
                return {
                    "user_id": "api_key_user",
                    "tenant_id": DEFAULT_TENANT_ID,
                    "name": "API Key User",
                    "auth_method": "api_key"
                }
            raise ValueError("SUPABASE_JWT_SECRET not configured")

        # Check if the token is the API key fallback
        api_key_from_env = os.getenv("SCRAPER_API_KEY")
        if api_key and api_key_from_env and api_key == api_key_from_env:
            logger.info("Using API key authentication")
            return {
                "user_id": "api_key_user",
                "tenant_id": DEFAULT_TENANT_ID,
                "name": "API Key User",
                "auth_method": "api_key"
            }

        # Log token format for debugging
        token_parts = credentials.credentials.split('.')
        if len(token_parts) != 3:
            logger.error(f"Invalid JWT format: expected 3 parts, got {len(token_parts)}")
            # Try to continue with API key authentication
            api_key_from_env = os.getenv("SCRAPER_API_KEY")
            if api_key and api_key_from_env and api_key == api_key_from_env:
                logger.info("Using API key authentication as fallback due to invalid JWT format")
                return {
                    "user_id": "api_key_user",
                    "tenant_id": DEFAULT_TENANT_ID,
                    "name": "API Key User",
                    "auth_method": "api_key"
                }
            raise ValueError("Invalid JWT format")

        # Try to decode the JWT payload for debugging
        try:
            # Just decode the payload part without verification for debugging
            payload_part = token_parts[1]
            # Add padding if needed
            padding = '=' * (4 - len(payload_part) % 4) if len(payload_part) % 4 else ''
            payload_debug = json.loads(base64.b64decode(payload_part + padding).decode('utf-8'))
            # Log without sensitive content
            logger.info(f"JWT payload received with sub: {payload_debug.get('sub', 'not-present')}, exp: {payload_debug.get('exp', 'not-present')}")
        except Exception as debug_error:
            logger.warning(f"Could not decode JWT payload for debugging: {str(debug_error)}")

        # Decode the JWT token with verification
        try:
            payload = jwt.decode(
                credentials.credentials,
                jwt_secret,
                algorithms=["HS256"],
                audience="authenticated"  # Set the expected audience to match Supabase's JWT
            )
            logger.info(f"JWT decoded successfully. Audience: {payload.get('aud')}")
        except jwt.ExpiredSignatureError:
            logger.error("JWT token has expired")
            raise ValueError("Token expired")
        except jwt.InvalidAudienceError:
            logger.error(f"JWT has invalid audience")
            # Try with a different audience
            try:
                payload = jwt.decode(
                    credentials.credentials,
                    jwt_secret,
                    algorithms=["HS256"],
                    options={"verify_aud": False}  # Skip audience verification
                )
                logger.info(f"JWT decoded successfully with audience verification disabled")
            except Exception as retry_error:
                logger.error(f"JWT decode retry error: {str(retry_error)}")
                raise ValueError("Invalid token audience")
        except Exception as jwt_error:
            logger.error(f"JWT decode error: {str(jwt_error)}")
            raise ValueError(f"JWT decode error: {str(jwt_error)}")

        user_id = payload.get("sub")
        if not user_id:
            logger.error("User ID (sub) not found in JWT payload")
            raise ValueError("User ID not found in token")

        # Get user profile from Supabase
        try:
            with db.get_cursor() as cur:
                cur.execute("SELECT * FROM profiles WHERE id = %s", (user_id,))
                user_profile_tuple = cur.fetchone()

                # Get column names from cursor description
                columns = [desc[0] for desc in cur.description] if cur.description else []
        except Exception as db_error:
            logger.error(f"Database error when fetching user profile: {str(db_error)}")
            # Return default user info instead of failing
            return {
                "user_id": user_id,
                "tenant_id": payload.get("sub", DEFAULT_TENANT_ID),
                "name": "Unknown User",
                "auth_method": "jwt_no_profile"
            }

        if not user_profile_tuple:
            logger.info(f"No profile found for user {user_id}, using user_id as tenant_id")
            # If no profile exists, use user_id as tenant_id
            return {
                "user_id": user_id,
                "tenant_id": user_id,  # Use user_id as tenant_id
                "name": "Unknown User",
                "auth_method": "jwt_no_profile"
            }

        # Convert tuple to dictionary
        user_profile = dict(zip(columns, user_profile_tuple)) if columns else {}
        logger.info(f"User profile found for {user_id}")

        # Use tenant_id from header if provided and valid
        tenant_id = None
        if x_tenant_id and is_valid_uuid(x_tenant_id):
            tenant_id = x_tenant_id
            logger.info(f"Using tenant_id from header: {tenant_id}")
        else:
            # Otherwise use from profile or fallback to user_id
            tenant_id = user_profile.get("tenant_id", user_id)
            logger.info(f"Using tenant_id from profile: {tenant_id}")

        # Return user information
        return {
            "user_id": user_id,
            "tenant_id": tenant_id,
            "name": user_profile.get("name", "Unknown User"),
            "email": user_profile.get("email"),
            "auth_method": "jwt"
        }
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        # Last resort fallback to API key authentication
        api_key = extract_api_key(credentials.credentials) if hasattr(credentials, 'credentials') else None
        api_key_from_env = os.getenv("SCRAPER_API_KEY")
        if api_key and api_key_from_env and api_key == api_key_from_env:
            logger.info("Using API key authentication as last resort fallback")
            return {
                "user_id": "api_key_user",
                "tenant_id": DEFAULT_TENANT_ID,
                "name": "API Key User",
                "auth_method": "api_key_fallback"
            }
        raise HTTPException(
            status_code=401,
            detail=f"Invalid authentication credentials: {str(e)}"
        )

def validate_tenant_id(tenant_id: Optional[str], current_user: Dict) -> str:
    """
    Validate and normalize tenant ID, with fallback to user's tenant ID.

    Args:
        tenant_id: The tenant ID to validate
        current_user: The authenticated user information

    Returns:
        Normalized tenant ID string
    """
    # Use authenticated user's tenant_id if none provided
    if not tenant_id:
        tenant_id = current_user.get("tenant_id", DEFAULT_TENANT_ID)
        logger.info(f"Using tenant_id from authenticated user: {tenant_id}")

    # Ensure tenant_id is a valid UUID string
    try:
        uuid_obj = uuid.UUID(tenant_id)
        tenant_id = str(uuid_obj)  # Normalize the UUID format
        logger.info(f"Validated tenant_id as UUID: {tenant_id}")
    except ValueError:
        logger.warning(f"Invalid tenant_id format: {tenant_id}, using default")
        tenant_id = DEFAULT_TENANT_ID  # Fallback to default

    return tenant_id
