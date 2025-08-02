"""
JWT Authentication Module

This module provides JWT authentication for the application.
All tenant isolation, RBAC, and feature flag functionality has been removed.
"""

import logging
import os
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from ..config.settings import settings

logger = logging.getLogger(__name__)

# --- JWT Configuration ---
# IMPORTANT: The application will NOT start if JWT_SECRET_KEY is not set in the environment.
# This is a security measure to prevent using a default/weak key.
try:
    SECRET_KEY = os.environ["JWT_SECRET_KEY"]
except KeyError:
    logger.error("FATAL: JWT_SECRET_KEY environment variable not set.")
    raise

ALGORITHM = "HS256"  # As per Supabase default
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "30"))

# Log the configuration on startup to aid debugging
logger.info(
    f"JWT Auth Initialized. Algorithm: {ALGORITHM}, Secret Key Hint: '{SECRET_KEY[:8]}...'."
)

# Default tenant for development/testing
DEFAULT_TENANT_ID = os.getenv(
    "DEFAULT_TENANT_ID", "550e8400-e29b-41d4-a716-446655440000"
)

# OAuth2 scheme for Swagger UI authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/token")


def create_access_token(
    data: Dict[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT access token.
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> Dict[str, Any]:
    """
    Decode and validate a JWT token.
    """
    try:
        payload = jwt.decode(
            token, SECRET_KEY, algorithms=[ALGORITHM], audience="authenticated"
        )
        return payload
    except JWTError as e:
        logger.error(f"JWT decode error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """
    Get the current user from JWT token.
    """
    # Remove Bearer prefix if present
    if token.startswith("Bearer "):
        token = token[7:]  # Remove "Bearer " prefix

    # --- SECURITY WARNING: DEVELOPMENT ONLY ---
    # This block provides a bypass for JWT validation in development environments.
    # It uses a hardcoded token ('scraper_sky_2024') and should NEVER be enabled in staging or production.
    # The primary purpose is to allow backend testing without a live frontend session.
    if token == "scraper_sky_2024" and settings.environment.lower() in [
        "development",
        "dev",
    ]:
        logger.info("Using development token for authentication")

        # --- DEVELOPMENT TOKEN USER ID CHANGE (2025-04-11) ---
        # Previous hardcoded value "00000000-0000-0000-0000-000000000000"
        # caused ForeignKeyViolationError on commit because this UUID
        # does not exist in the 'users' table.
        # Changed to use the primary test user ID documented in
        # Docs/Docs_1_AI_GUIDES/10-TEST_USER_INFORMATION.md
        # This ensures operations requiring a valid 'updated_by' or 'created_by'
        # foreign key reference can succeed in the development environment.
        # -------------------------------------------------------

        dev_user_uuid = (
            "5905e9fe-6c61-4694-b09a-6602017b000a"  # From 10-TEST_USER_INFORMATION.md
        )
        return {
            "user_id": dev_user_uuid,
            "id": dev_user_uuid,
            "sub": dev_user_uuid,  # Add sub field for consistency with JWT standard
            "tenant_id": DEFAULT_TENANT_ID,
            "exp": datetime.utcnow() + timedelta(days=30),
        }

    payload = decode_token(token)

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create standardized user object
    user = {
        "user_id": user_id,
        "id": user_id,
        "sub": user_id,  # Include sub field for compatibility with routers expecting JWT standard fields
        "tenant_id": DEFAULT_TENANT_ID,
        "exp": payload.get("exp"),
    }

    return user


async def get_current_active_user(
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Get the current active user.
    """
    if current_user.get("disabled"):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
