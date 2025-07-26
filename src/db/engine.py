"""
SQLAlchemy Database Engine Module

Provides async database connection to Supabase PostgreSQL using SQLAlchemy.

IMPORTANT: This system exclusively uses Supavisor for connection pooling
with the following required parameters:
- raw_sql=true - Use raw SQL instead of ORM
- no_prepare=true - Disable prepared statements
- statement_cache_size=0 - Control statement caching

These parameters are non-negotiable and mandatory for all deployments.
"""

import logging
import uuid
from urllib.parse import quote_plus

from sqlalchemy.ext.asyncio import create_async_engine

# Import settings from central config (same as existing connection)
from src.config.settings import settings


class DatabaseConfig:
    """Configuration for Supabase database connection."""

    def __init__(self):
        # Extract project reference from Supabase URL
        self.supabase_url = settings.supabase_url
        if not self.supabase_url:
            raise ValueError("SUPABASE_URL environment variable is not set")

        # Handle URL format with or without protocol
        if "//" in self.supabase_url:
            self.project_ref = self.supabase_url.split("//")[1].split(".")[0]
        else:
            self.project_ref = self.supabase_url.split(".")[0]

        # Database connection parameters - use settings where available
        self.user = f"postgres.{self.project_ref}"
        self.password = settings.supabase_db_password or ""  # Ensure we have a string
        self.host = settings.supabase_db_host or f"db.{self.project_ref}.supabase.co"
        self.port = settings.supabase_db_port or "5432"
        self.dbname = settings.supabase_db_name  # This is already set in settings

        if not all([self.project_ref, self.password]):
            raise ValueError(
                "Missing required database configuration. "
                "Please ensure SUPABASE_URL and SUPABASE_DB_PASSWORD are set in .env"
            )

        # Try pooler connection first (IPv4 compatible)
        self.pooler_host = settings.supabase_pooler_host
        self.pooler_port = settings.supabase_pooler_port
        self.pooler_user = settings.supabase_pooler_user

    @property
    def async_connection_string(self) -> str:
        """Generate the SQLAlchemy connection string for asyncpg."""
        # Note: Supavisor connection parameters are handled in connect_args
        if all([self.pooler_host, self.pooler_port, self.pooler_user]):
            # Use connection pooler if available
            logging.info(f"Using pooler connection to {self.pooler_host}")
            return (
                f"postgresql+asyncpg://{self.pooler_user}:"
                f"{quote_plus(str(self.password))}"
                f"@{self.pooler_host}:{self.pooler_port}/{self.dbname}?sslmode=require"
            )

        # Fall back to direct connection if pooler not configured
        logging.info(f"Using direct connection to {self.host}")
        return (
            f"postgresql+asyncpg://{self.user}:{quote_plus(str(self.password))}"
            f"@{self.host}:{self.port}/{self.dbname}?sslmode=require"
        )

    @property
    def sync_connection_string(self) -> str:
        """Generate the SQLAlchemy connection string for psycopg2 (sync).
        ALWAYS returns the DIRECT connection string, bypassing the pooler.
        Used for Supabase MCP migrations and other synchronous tooling.
        """
        # ALWAYS use the direct connection host/port/user for sync operations
        logging.info(f"Generating DIRECT sync connection string to {self.host}")
        # Break into multiple lines to avoid line length issues
        base = f"postgresql://{self.user}:{quote_plus(str(self.password))}"
        connect = f"@{self.host}:{self.port}/{self.dbname}"
        params = "?sslmode=require"
        return base + connect + params

    @property
    def pooler_mode(self) -> bool:
        """Check if pooler connection details are configured in settings."""
        return all([self.pooler_host, self.pooler_port, self.pooler_user])


def get_supavisor_ready_url(db_url: str) -> str:
    """
    Enhance database URL with required Supavisor connection pooling parameters.

    Args:
        db_url: Original database URL

    Returns:
        Enhanced URL with connection pooling parameters
    """
    # NOTE: We now handle raw_sql via execution_options, so we only need
    # statement_cache_size in the URL if needed

    # Already has query parameters
    if "?" in db_url:
        return f"{db_url}&statement_cache_size=0"
    # No existing query parameters
    else:
        return f"{db_url}?statement_cache_size=0"


# Initialize database configuration
db_config = DatabaseConfig()

# Check if SQL echo is available in settings or use a default
sql_echo = getattr(settings, "sql_echo", False)


# Configure connect_args differently depending on connection type
def get_compatible_connect_args(is_async=True):
    """
    Get connection arguments compatible with the specified driver type.

    Args:
        is_async: Whether this is for an async connection (asyncpg) or sync (psycopg2)

    Returns:
        Dictionary of connection arguments
    """
    if is_async:
        # asyncpg specific parameters for Supavisor compatibility
        base_args = {
            "server_settings": {
                "search_path": "public",
                "application_name": "scraper_sky",
            },
            "prepared_statement_name_func": lambda: f"__asyncpg_{uuid.uuid4()}__",
            "ssl": "require",
            "command_timeout": settings.db_connection_timeout,
            "statement_cache_size": 0,
            "raw_sql": True,
            "no_prepare": True,
        }

        # When using connection pooler, add compatibility options
        if db_config.pooler_mode:
            base_args["server_settings"].update({"options": "-c search_path=public"})
    else:
        # psycopg2 specific parameters
        base_args = {
            "sslmode": "require",
        }

    return base_args


# Async connection arguments
connect_args = get_compatible_connect_args(is_async=True)

# Create the async engine with proper connection pooling settings
engine = create_async_engine(
    get_supavisor_ready_url(db_config.async_connection_string),
    pool_size=settings.db_min_pool_size,
    max_overflow=settings.db_max_pool_size - settings.db_min_pool_size,
    pool_timeout=settings.db_connection_timeout,
    pool_recycle=1800,
    echo=False,  # Set to True for SQL query logging in development
    connect_args=connect_args,
    # Required Supavisor parameters
    statement_cache_size=0,
    # Apply Supavisor compatibility options at the engine level
    execution_options={
        "isolation_level": "READ COMMITTED",
        "raw_sql": True,
        "no_prepare": True,
    },
)

# Log successful engine creation with info about Supavisor parameters
logging.info(
    "SQLAlchemy async engine created with Supavisor connection pooling parameters"
)
logging.info(f"Connected to: {db_config.host or db_config.pooler_host}")


# Function to get SQLAlchemy URL for Alembic migrations (sync)
def get_sync_url():
    """Get the synchronous SQLAlchemy URL for migrations."""
    return db_config.sync_connection_string


# Create a sync engine for direct database operations
_sync_engine = None


def get_sync_engine():
    """
    Get or create a synchronous SQLAlchemy engine.

    This is used for operations that require direct database access
    outside of the async context, such as in the db_service compatibility layer.

    Returns:
        SQLAlchemy Engine instance
    """
    global _sync_engine
    if _sync_engine is None:
        from sqlalchemy import create_engine

        # Use compatible connect args for synchronous connections
        sync_connect_args = get_compatible_connect_args(is_async=False)

        # Create engine with proper settings for Supavisor
        _sync_engine = create_engine(
            get_sync_url(),
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10,
            connect_args=sync_connect_args,
        )
        logging.info("Created synchronous SQLAlchemy engine")
    return _sync_engine
