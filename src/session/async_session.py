"""
Async Session Manager

This module provides an async session factory and contextmanager for
working with SQLAlchemy ORM in an asyncio context.

IMPORTANT: This system exclusively uses Supavisor for connection pooling
with the following required parameters:
- raw_sql=true - Use raw SQL instead of ORM
- no_prepare=true - Disable prepared statements
- statement_cache_size=0 - Control statement caching

These parameters are non-negotiable and mandatory for all deployments.
"""

import logging
import os
import socket
import ssl
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from urllib.parse import quote_plus
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from ..config.settings import settings

logger = logging.getLogger(__name__)


# Automatically detect environment based on hostname
def is_development_environment() -> bool:
    """
    Determine if the application is running in a development environment.

    Returns:
        True if running in development, False if in production
    """
    # Check explicit environment setting first
    if hasattr(settings, "environment") and settings.environment:
        return settings.environment.lower() in ("development", "dev", "local")

    # Check hostname
    hostname = socket.gethostname()
    is_dev = (
        "localhost" in hostname.lower()
        or "dev" in hostname.lower()
        or hostname == "127.0.0.1"
        or hostname.startswith("192.168.")
        or hostname.startswith("10.")
        or hostname.startswith("172.16.")
        or hostname.endswith(".local")
    )

    logger.info(
        f"Detected environment: {'Development' if is_dev else 'Production'} "
        f"based on hostname: {hostname}"
    )
    return is_dev


# Store the environment detection result
IS_DEVELOPMENT = is_development_environment()


# Build connection string from Supabase settings
def get_database_url() -> str:
    """
    Build a SQLAlchemy-compatible connection string from environment variables.
    Falls back to the original hardcoded string if environment variables are missing.
    """
    # Try to use environment variables first
    pooler_host = os.environ.get("SUPABASE_POOLER_HOST")
    pooler_port = os.environ.get("SUPABASE_POOLER_PORT")
    pooler_user = os.environ.get("SUPABASE_POOLER_USER")
    password = os.environ.get("SUPABASE_DB_PASSWORD")
    dbname = "postgres"  # Default database name for Supabase

    # Extract project reference from Supabase URL if available
    project_ref = None
    if settings.supabase_url:
        if "//" in settings.supabase_url:
            project_ref = settings.supabase_url.split("//")[1].split(".")[0]
        else:
            project_ref = settings.supabase_url.split(".")[0]

    # Check if all required env vars are available
    if all([pooler_host, pooler_port, pooler_user, password]):
        # Ensure password is a string before using quote_plus
        safe_password = str(password) if password is not None else ""

        # If pooler_user already includes project_ref, use it directly
        if pooler_user and "." in pooler_user:
            user_part = pooler_user
        # Otherwise, append project_ref if available
        elif project_ref:
            user_part = (
                f"{pooler_user}.{project_ref}"
                if pooler_user
                else f"postgres.{project_ref}"
            )
        else:
            user_part = pooler_user or "postgres"

        connection_string = (
            f"postgresql+asyncpg://{user_part}:{quote_plus(safe_password)}"
            f"@{pooler_host}:{pooler_port}/{dbname}?sslmode=require"
        )
        logger.info(
            f"Using Supabase Supavisor connection pooler at {pooler_host}:{pooler_port}"
        )
        return connection_string

    # Raise an error if environment variables are missing
    # (instead of using hardcoded fallback)
    raise ValueError(
        "Missing environment variables for database connection. "
        "Please set SUPABASE_POOLER_HOST, SUPABASE_POOLER_PORT, SUPABASE_POOLER_USER, "
        "and SUPABASE_DB_PASSWORD in your .env file."
    )


# Get database URL with no fallback - fail loudly if connection details are missing
try:
    DATABASE_URL = get_database_url()
    # Log the connection string with password redacted
    safe_url = DATABASE_URL
    if settings.supabase_db_password:
        safe_url = DATABASE_URL.replace(settings.supabase_db_password, "********")
    logger.info(f"Using database URL: {safe_url}")
except Exception as e:
    logger.critical(f"Failed to build database connection string: {str(e)}")
    raise

# Configure SSL context based on environment
if IS_DEVELOPMENT:
    # Development: Disable SSL verification for easier local development
    logger.warning(
        "Development environment detected: Disabling SSL certificate verification"
    )
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
else:
    # Production: Use proper SSL verification
    logger.info(
        "Production environment detected: Using strict SSL certificate verification"
    )
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = True
    ssl_context.verify_mode = ssl.CERT_REQUIRED

# Create connect_args with appropriate settings for Supavisor
connect_args = {
    "ssl": ssl_context,
    "timeout": settings.db_connection_timeout,
    # Generate unique prepared statement names for Supavisor compatibility
    "prepared_statement_name_func": lambda: f"__asyncpg_{uuid4()}__",
    # Required Supavisor connection parameters
    "server_settings": {"statement_cache_size": "0"},
    # Explicitly disable prepared statements for asyncpg 0.30.0
    "statement_cache_size": 0,
    "prepared_statement_cache_size": 0,
}

# Create async engine with environment-specific settings
# Connect args already contain statement_cache_size and prepared_statement_cache_size

engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL query logging in development
    connect_args=connect_args,
    # Use a proper connection pool for Supavisor instead of NullPool
    pool_size=5 if IS_DEVELOPMENT else settings.db_max_pool_size,
    max_overflow=5 if IS_DEVELOPMENT else 10,
    pool_timeout=settings.db_connection_timeout,
    pool_recycle=1800,  # Recycle connections after 30 minutes
    # Apply Supavisor compatibility options at the engine level
    execution_options={
        "isolation_level": "READ COMMITTED",
        "no_prepare": True,
        "raw_sql": True,
    },
)

# Create async session factory
async_session_factory = async_sessionmaker(
    engine,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


# Create a dedicated background task session factory with all the necessary
# compatibility settings for asyncpg 0.30.0
def get_background_task_session_factory():
    """
    Returns a session factory specifically configured for background tasks
    with all necessary asyncpg 0.30.0 compatibility settings applied.

    This function ensures that all background tasks get consistent connection
    settings that properly disable prepared statements.

    Returns:
        AsyncSession factory function
    """
    # The correct approach is to use the same engine since the connection parameters
    # are already set at the engine level in the connect_args
    return async_sessionmaker(
        engine, expire_on_commit=False, autoflush=False, autocommit=False
    )


# Create an instance of the background task session factory
background_task_session_factory = get_background_task_session_factory()


@asynccontextmanager
async def get_background_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Async context manager for background task database sessions.

    This should be used for ALL background tasks to ensure proper
    connection parameter handling with asyncpg 0.30.0.

    Example:
        async with get_background_session() as session:
            # Background task database operations
    """
    session = background_task_session_factory()
    try:
        yield session
        await session.commit()
    except Exception as e:
        await session.rollback()
        logger.error(f"Background task session error: {str(e)}")
        raise
    finally:
        await session.close()


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Async context manager for database sessions.

    Provides a SQLAlchemy AsyncSession and handles committing changes and
    rolling back on exceptions.

    Example:
        async with get_session() as session:
            result = await session.execute(query)
            session.add(new_record)
    """
    session = async_session_factory()
    try:
        yield session
        await session.commit()
    except Exception as e:
        await session.rollback()
        logger.error(f"Database session error: {str(e)}")
        raise
    finally:
        await session.close()


async def get_session_dependency() -> AsyncGenerator[AsyncSession, None]:
    """
    Get an async session for use as a FastAPI dependency.

    This function is designed to be used with FastAPI's dependency injection system.

    Example:
        @router.get("/items")
        async def get_items(session: AsyncSession = Depends(get_session_dependency)):
            result = await session.execute(select(Item))
            return result.scalars().all()
    """
    async with get_session() as session:
        yield session
