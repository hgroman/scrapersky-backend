"""
Database Session Management Module

This module provides standardized session factory and connection management
for the ScraperSky application, ensuring proper transaction handling and
connection pooling compatible with Supavisor.
"""
import logging
import os
import ssl
import uuid
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from urllib.parse import parse_qs, urlparse

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import sessionmaker

from ..config.settings import settings

logger = logging.getLogger(__name__)


# NO DEFAULT TENANT ID - As per architectural mandate, JWT/tenant authentication
# happens ONLY at API gateway endpoints, while database operations NEVER handle JWT or tenant authentication.

def get_engine():
    """
    Create and configure the SQLAlchemy engine.
    """
    connection_string = get_db_url()

    # Determine environment-appropriate pool settings
    is_prod = os.getenv("ENVIRONMENT", "").lower() == "production"

    # Production values are more conservative than development
    pool_settings = {
        "pool_pre_ping": True,  # Always validate connections before use
        "pool_size": 10 if is_prod else 5,
        "max_overflow": 15 if is_prod else 10,
        "pool_recycle": 1800 if is_prod else 3600,  # 30 min in prod, 60 min in dev
        "pool_timeout": 30,
        "echo": getattr(settings, 'SQL_ECHO', False),
    }

    # CRITICAL: Supavisor connection pooling compatibility settings
    # As per README: ALWAYS USE SUPAVISOR CONNECTION POOLING WITH PROPER PARAMETERS
    connect_args = {
        "statement_cache_size": 0,        # CRITICAL for Supavisor compatibility
        "prepared_statement_cache_size": 0,  # CRITICAL for Supavisor compatibility
        "prepared_statement_name_func": lambda: f"__asyncpg_{uuid.uuid4()}__",  # Avoid prepared statement name conflicts
        # Server settings for PostgreSQL - minimal configuration as recommended by Supabase
        "server_settings": {
            "search_path": "public",
            "application_name": "scrapersky_backend"  # Identify application in logs
        },
        # SSL configuration
        "ssl": False  # We'll handle SSL context manually
    }

    # Create SSL context that matches sslmode=require behavior
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    connect_args["ssl"] = ssl_context

    # Development environment - log SSL configuration
    if os.getenv("ENVIRONMENT", "").lower() != "production":
        logger.warning("Development environment detected: Disabling SSL certificate verification")

    # Log connection parameters for diagnostics
    logger.info("Using Supavisor connection pooling parameters as required by architectural mandate")

    # Log the engine configuration for diagnostic purposes
    logger.info(f"Creating database engine with: pool_size={pool_settings['pool_size']}, "
                f"max_overflow={pool_settings['max_overflow']}, "
                f"recycle={pool_settings['pool_recycle']}s")

    engine = create_async_engine(
        connection_string,
        **pool_settings,
        connect_args=connect_args,
        execution_options={
            "isolation_level": "READ COMMITTED",
            "raw_sql": True,  # REQUIRED for Supavisor
            "no_prepare": True  # REQUIRED for Supavisor
        },
        future=True
    )

    return engine

def get_db_url() -> str:
    """
    Get database URL with a multi-layered fallback strategy.

    CRITICAL: According to the architectural mandate, JWT/tenant authentication
    happens ONLY at API gateway endpoints, while database operations NEVER handle
    JWT or tenant authentication.

    Order of precedence:
    1. environment variable DATABASE_URL
    2. settings.DATABASE_URL if available
    3. settings.db_url if available
    4. Construct from component settings if available
    5. Default to development database URL
    """
    # Try environment variable first (highest priority)
    db_url = os.getenv("DATABASE_URL")

    # Then check settings object with various possible attribute names
    if not db_url and settings:
        for attr in ["DATABASE_URL", "db_url", "database_url"]:
            if hasattr(settings, attr):
                db_url = getattr(settings, attr)
                if db_url:
                    break

    # If still no URL, try to construct from components
    if not db_url and settings:
        try:
            # For Supabase, format should be postgres.[project-ref]
            project_ref = getattr(settings, "SUPABASE_PROJECT_REF", "ddfldwzhdhhzhxywqnyz")
            components = {
                "user": f"postgres.{project_ref}",  # Include project reference in username
                "password": getattr(settings, "POSTGRES_PASSWORD", "postgres"),
                "host": getattr(settings, "POSTGRES_HOST", "localhost"),
                "port": getattr(settings, "POSTGRES_PORT", 5432),
                "database": getattr(settings, "POSTGRES_DB", "scrapersky")
            }
            db_url = f"postgresql+asyncpg://{components['user']}:{components['password']}@{components['host']}:{components['port']}/{components['database']}"
        except Exception as e:
            logger.warning(f"Failed to construct database URL from components: {e}")

    # Last resort - development default
    if not db_url:
        # For Supabase pooler, use the correct format with project reference
        if os.getenv("SUPABASE_POOLER_HOST"):
            # Get the pooler user from environment variable
            pooler_user = os.getenv('SUPABASE_POOLER_USER', '')

            # Ensure username has the correct format (postgres.[project-ref])
            # If it already has the correct format, use it as is
            if pooler_user and '.' in pooler_user and pooler_user.startswith('postgres.'):
                db_user = pooler_user  # Already in correct format
            else:
                # Need to format it correctly
                project_ref = os.getenv("SUPABASE_PROJECT_REF", "ddfldwzhdhhzhxywqnyz")
                db_user = f"postgres.{project_ref}"
                logger.warning(f"Reformatting pooler username to required format: {db_user}")

            db_host = os.getenv("SUPABASE_POOLER_HOST", "aws-0-us-west-1.pooler.supabase.com")
            db_port = os.getenv("SUPABASE_POOLER_PORT", "6543")
            db_password = os.getenv("SUPABASE_DB_PASSWORD", "")

            logger.warning("No DATABASE_URL found. Using Supabase pooler connection.")
            db_url = f"postgresql+asyncpg://{db_user}:{db_password}@{db_host}:{db_port}/postgres"
        else:
            # Local development fallback
            logger.warning("No DATABASE_URL found. Using local development default.")
            db_url = "postgresql+asyncpg://postgres:postgres@localhost:5432/scrapersky"

    # Ensure correct driver for async operations
    if db_url and not db_url.startswith(("postgresql+asyncpg://", "postgres+asyncpg://")):
        # Handle common format variations
        if db_url.startswith(("postgres://", "postgresql://")):
            db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)
            db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        else:
            # Unknown format, try to prepend the driver
            logger.warning(f"Unrecognized database URL format: {db_url}. Attempting to add asyncpg driver.")
            db_url = f"postgresql+asyncpg://{db_url.split('://', 1)[1]}" if "://" in db_url else f"postgresql+asyncpg://{db_url}"

    # CRITICAL: Ensure we're using the proper Supavisor connection format
    # Parse the URL to handle query parameters according to architectural mandate
    parsed_url = urlparse(db_url)
    query_params = parse_qs(parsed_url.query)

    # CRITICAL: According to architectural mandate, remove ALL tenant filtering from database operations
    # Per README: ALWAYS use Supavisor connection pooling with proper parameters

    # Add required parameters for Supavisor compatibility
    query_params['statement_cache_size'] = ['0']
    query_params['prepared_statement_cache_size'] = ['0']

    # Remove ALL tenant/JWT/role-related parameters as per architectural mandate
    tenant_related_params = [
        'tenant', 'tenant_id', 'role', 'user', 'user_id', 'jwt', 'claims',
        'auth', 'auth.role', 'auth.uid', 'auth.tenant', 'auth.claims'
    ]

    for param in tenant_related_params:
        if param in query_params:
            del query_params[param]
            logger.warning(f"Removed {param} from database URL as per architectural mandate")

    # Reconstruct the URL with the proper parameters for Supavisor
    from urllib.parse import urlencode
    clean_query = urlencode(query_params, doseq=True) if query_params else ''
    clean_url = parsed_url._replace(query=clean_query).geturl()

    # Log the database URL (with credentials redacted)
    logger.info(f"Using database connection: {clean_url.replace(clean_url.split('@')[0], '***CREDENTIALS_REDACTED***')}")

    # Log that we're using the Supavisor connection pooler as required
    logger.info("Using Supavisor connection pooler as required by architectural mandate")

    return clean_url

# Create a session factory using the engine
async_session_factory = async_sessionmaker(
    bind=get_engine(),
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency provider for database sessions.
    Usage: session: AsyncSession = Depends(get_db_session)

    This is the ONLY approved method for obtaining a database session
    in router endpoints.
    """
    session = async_session_factory()
    try:
        logger.debug("Creating new database session")
        yield session
        await session.commit()
        logger.debug("Session committed successfully")
    except Exception as e:
        logger.error(f"Exception during database session, rolling back: {e}", exc_info=True)
        await session.rollback()
        raise
    finally:
        logger.debug("Closing database session")
        await session.close()

async def get_session() -> AsyncSession:
    """
    Get a database session for use in background tasks.
    Usage: async with get_session() as session:

    This is the ONLY approved method for obtaining a database session
    in background tasks.
    """
    return async_session_factory()

# For use in implementations that manually create engines
get_async_engine = get_engine
async_session = get_session

@asynccontextmanager
async def transaction_context(session: AsyncSession):
    """
    Context manager for handling transactions.

    This utility provides a clean way to use transactions in router endpoints.
    It ensures that transactions are committed on success and rolled back on error.

    Args:
        session: The SQLAlchemy async session

    Example:
        ```python
        async with transaction_context(session):
            # Execute database operations
            result = await session.execute(query)
        ```
    """
    try:
        async with session.begin():
            logger.debug("Transaction started")
            yield
            logger.debug("Transaction committed")
    except Exception as e:
        logger.error(f"Transaction error: {e}")
        raise

@asynccontextmanager
async def get_session_context():
    """
    Create and manage a session context.

    This utility provides a clean way to obtain and use a database session.
    It ensures that sessions are properly closed after use.

    Example:
        ```python
        async with get_session_context() as session:
            # Execute database operations
            result = await session.execute(query)
        ```
    """
    session = async_session_factory()
    try:
        yield session
    finally:
        await session.close()
