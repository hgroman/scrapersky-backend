"""
FIXED Async Session Manager - Proper Supabase Session Mode for Docker Containers

This module provides proper connection management for persistent Docker containers
using Supabase session mode (port 5432), not transaction mode.

CRITICAL FIXES:
1. Use session mode (port 5432) for persistent containers, not transaction mode (6543)
2. Remove transaction mode-specific settings that cause locking issues
3. Simplified session context managers that don't auto-commit
4. Proper connection pooling for session mode
"""

import logging
import os
import ssl
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from urllib.parse import quote_plus

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

logger = logging.getLogger(__name__)


def get_fixed_database_url() -> str:
    """
    Build proper connection string for Docker containers using SESSION MODE (port 5432).
    NOT transaction mode (6543) which is for serverless functions.
    """
    pooler_host = os.environ.get("SUPABASE_POOLER_HOST")
    pooler_user = os.environ.get("SUPABASE_POOLER_USER")
    password = os.environ.get("SUPABASE_DB_PASSWORD")

    # CRITICAL: Use port 5432 (session mode) for Docker containers
    pooler_port = "5432"  # NOT 6543 which is transaction mode
    dbname = "postgres"

    if not all([pooler_host, pooler_user, password]):
        raise ValueError("Missing required database connection environment variables")

    safe_password = quote_plus(str(password))

    connection_string = (
        f"postgresql+asyncpg://{pooler_user}:{safe_password}"
        f"@{pooler_host}:{pooler_port}/{dbname}"
    )

    logger.info(f"🔧 FIXED: Using SESSION MODE at {pooler_host}:{pooler_port}")
    return connection_string


# Configure SSL for Supabase
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

# FIXED: Proper connect_args for SESSION MODE (not transaction mode)
connect_args = {
    "ssl": ssl_context,
    "timeout": 30,
    # Remove transaction mode-specific settings that cause locking
}

# FIXED: Create engine with proper SESSION MODE settings
fixed_engine = create_async_engine(
    get_fixed_database_url(),
    echo=False,
    connect_args=connect_args,
    # Proper connection pooling for session mode
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800,
    # Remove transaction mode execution options
)

# Create session factory
fixed_session_factory = async_sessionmaker(
    fixed_engine,
    expire_on_commit=False,
    autoflush=True,  # Enable autoflush for proper ORM behavior
    autocommit=False,  # Manual transaction control
)


@asynccontextmanager
async def get_fixed_session() -> AsyncGenerator[AsyncSession, None]:
    """
    FIXED session manager - no auto-commit, proper transaction boundaries.

    Usage:
        async with get_fixed_session() as session:
            # Do work
            await session.commit()  # Manual commit when ready
    """
    session = fixed_session_factory()
    try:
        yield session
        # NO AUTO-COMMIT - let caller control transactions
    except Exception as e:
        await session.rollback()
        logger.error(f"Session error: {e}")
        raise
    finally:
        await session.close()


@asynccontextmanager
async def get_fixed_scheduler_session() -> AsyncGenerator[AsyncSession, None]:
    """
    FIXED session specifically for scheduler tasks with proper row locking.

    Usage:
        async with get_fixed_scheduler_session() as session:
            # Query with row locks
            # Make changes
            await session.commit()  # Explicit commit
    """
    session = fixed_session_factory()
    try:
        yield session
        # NO AUTO-COMMIT - scheduler controls when to commit
    except Exception as e:
        await session.rollback()
        logger.error(f"Scheduler session error: {e}")
        raise
    finally:
        await session.close()
