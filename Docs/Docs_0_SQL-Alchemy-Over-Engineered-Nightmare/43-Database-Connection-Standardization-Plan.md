# Database Connection Standardization Plan

## 1. Current Situation Analysis

The ScraperSky backend currently has **two parallel database connection systems** that are causing critical issues:

### 1.1 Legacy Connection System (`sb_connection.py`)

- Uses direct `psycopg2` connections to Supabase
- Properly configured with connection pooling
- Currently used by:
  - `src/routers/admin.py`
  - `src/routers/rbac.py` (legacy router)
  - `src/routers/db_portal.py`
  - Other legacy routers that haven't been modernized

### 1.2 SQLAlchemy Connection System (`async_session.py`)

- Uses SQLAlchemy ORM with `asyncpg`
- **IMPROPERLY CONFIGURED**: Falls back to a non-existent local PostgreSQL instance
- Currently used by:
  - `src/router_factory/rbac_router.py` (new router)
  - `src/router_factory/feature_router.py`
  - Other modernized routers using the router factory pattern

### 1.3 Critical Issues

1. **Connection Configuration Failure**: SQLAlchemy is not properly configured to use Supabase
2. **Silent Fallback**: Instead of failing loudly, it silently falls back to a non-existent local database
3. **Inconsistent Access Patterns**: Some components use direct connections, others use SQLAlchemy
4. **Partial Implementation**: SQLAlchemy models and services are correctly implemented but can't connect

## 2. Root Cause Analysis

The root cause of these issues is in `src/session/async_session.py`:

```python
# Get database URL from environment variable with fallback
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/scrapersky"
)
```

This code:

1. Attempts to get a `DATABASE_URL` environment variable
2. If not found, silently falls back to a local PostgreSQL connection
3. Does not leverage the properly configured Supabase connection details in `settings`

The correct approach should be:

1. Use the Supabase connection details from `settings`
2. Fail loudly if connection details are missing
3. No fallback to a non-existent local database

## 3. Comprehensive Inventory of Database Access

### 3.1 Components Using Legacy Connection (`sb_connection.py`)

| Component                | File                             | Status                                               |
| ------------------------ | -------------------------------- | ---------------------------------------------------- |
| Admin Router             | `src/routers/admin.py`           | Using direct `db` import from `sb_connection`        |
| Legacy RBAC Router       | `src/routers/rbac.py`            | Using direct `db` import from `sb_connection`        |
| DB Portal                | `src/routers/db_portal.py`       | Using direct `db` import from `sb_connection`        |
| Email Scanner            | `src/routers/email_scanner.py`   | Using direct `db` import from `sb_connection`        |
| Dev Tools                | `src/routers/dev_tools.py`       | Using direct `db` import from `sb_connection`        |
| Sitemap Scraper (Legacy) | `src/routers/sitemap_scraper.py` | Partially migrated, still has some direct `db` usage |

### 3.2 Components Using SQLAlchemy (`async_session.py`)

| Component               | File                                            | Status                                         |
| ----------------------- | ----------------------------------------------- | ---------------------------------------------- |
| RBAC Router Factory     | `src/router_factory/rbac_router.py`             | Using SQLAlchemy with `get_session_dependency` |
| Feature Router Factory  | `src/router_factory/feature_router.py`          | Using SQLAlchemy with `get_session_dependency` |
| Sitemap Analyzer Router | `src/router_factory/sitemap_analyzer_router.py` | Using SQLAlchemy with `get_session_dependency` |
| Google Maps API Router  | `src/router_factory/google_maps_api.py`         | Using SQLAlchemy with `get_session_dependency` |
| Modernized Page Scraper | `src/routers/modernized_page_scraper.py`        | Using SQLAlchemy with `get_session_dependency` |

## 4. Standardization Plan

### 4.1 Fix SQLAlchemy Connection Configuration

1. **Update `async_session.py` to use Supabase connection details**:

```python
"""
Async Session Manager

This module provides an async session factory and contextmanager for
working with SQLAlchemy ORM in an asyncio context.
"""
import os
import logging
from typing import AsyncGenerator, Optional
from contextlib import asynccontextmanager
from urllib.parse import quote_plus

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base, sessionmaker

from ..config.settings import settings

logger = logging.getLogger(__name__)

# Build connection string from Supabase settings
def get_database_url() -> str:
    """
    Build a SQLAlchemy-compatible connection string from Supabase settings.
    Raises an exception if required settings are missing.
    """
    # Check for pooler configuration first (preferred for production)
    pooler_host = settings.supabase_pooler_host
    pooler_port = settings.supabase_pooler_port
    pooler_user = settings.supabase_pooler_user
    password = settings.supabase_db_password
    dbname = settings.supabase_db_name or "postgres"

    # Include connection timeout from settings
    timeout_param = f"connect_timeout={settings.db_connection_timeout}"

    # Validate required settings
    if not password:
        raise ValueError("SUPABASE_DB_PASSWORD is required but not set")

    # Try pooler connection first (IPv4 compatible)
    if all([pooler_host, pooler_port, pooler_user]):
        connection_string = (
            f"postgresql+asyncpg://{pooler_user}:{quote_plus(password)}"
            f"@{pooler_host}:{pooler_port}/{dbname}"
            f"?sslmode=require&{timeout_param}"
        )
        logger.info(f"Using Supabase connection pooler at {pooler_host}:{pooler_port}")
        return connection_string

    # Fall back to direct connection if pooler not configured
    # Get project reference from Supabase URL
    supabase_url = settings.supabase_url
    if not supabase_url:
        raise ValueError("SUPABASE_URL is required but not set")

    # Handle URL format with or without protocol
    if '//' in supabase_url:
        project_ref = supabase_url.split('//')[1].split('.')[0]
    else:
        project_ref = supabase_url.split('.')[0]

    # Build connection parameters
    user = f"postgres.{project_ref}"
    host = f"db.{project_ref}.supabase.co"
    port = "5432"

    connection_string = (
        f"postgresql+asyncpg://{user}:{quote_plus(password)}"
        f"@{host}:{port}/{dbname}"
        f"?sslmode=require&{timeout_param}"
    )
    logger.info(f"Using direct Supabase connection at {host}:{port}")
    return connection_string

# Get database URL with no fallback - fail loudly if connection details are missing
try:
    DATABASE_URL = get_database_url()
    # Log the connection string with password redacted
    safe_url = DATABASE_URL.replace(settings.supabase_db_password, "********") if settings.supabase_db_password else DATABASE_URL
    logger.info(f"Using database URL: {safe_url}")
except Exception as e:
    logger.critical(f"Failed to build database connection string: {str(e)}")
    raise

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL query logging
    pool_size=settings.db_max_pool_size,
    max_overflow=10,
    pool_timeout=settings.db_connection_timeout,
    pool_recycle=1800,
)

# Create async session factory
async_session_factory = async_sessionmaker(
    engine,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)

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
```

2. **Add Health Check for Database Connection**:

Create a new file `src/health/db_health.py`:

```python
"""
Database Health Check

This module provides health check functions for database connections.
"""
import logging
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

async def check_database_connection(session: AsyncSession) -> bool:
    """
    Check if the database connection is working.

    Args:
        session: SQLAlchemy async session

    Returns:
        True if connection is working, False otherwise
    """
    try:
        # Execute a simple query to check connection
        result = await session.execute(text("SELECT 1"))
        return result.scalar() == 1
    except Exception as e:
        logger.error(f"Database connection check failed: {str(e)}")
        return False
```

3. **Add Database Health Check to Main Application**:

Update `src/main.py` to include a database health check endpoint:

```python
from src.session.async_session import get_session
from src.health.db_health import check_database_connection

@app.get("/health/database", tags=["health"])
async def database_health():
    """Check database connection health."""
    async with get_session() as session:
        is_healthy = await check_database_connection(session)
        if not is_healthy:
            return JSONResponse(
                status_code=500,
                content={"status": "error", "message": "Database connection failed"}
            )
        return {"status": "ok", "message": "Database connection successful"}
```

### 4.2 Migration Plan for Legacy Components

#### Phase 1: Verify SQLAlchemy Connection (Immediate)

1. Implement the SQLAlchemy connection fix described above
2. Add the database health check endpoint
3. Test the connection with:
   ```bash
   curl -v http://localhost:8000/health/database
   ```
4. Verify that the RBAC router works:
   ```bash
   curl -v http://localhost:8000/api/v2/role_based_access_control/roles -H "X-Tenant-Id: 550e8400-e29b-41d4-a716-446655440000"
   ```

#### Phase 2: Migrate Legacy Routers (Short-term)

For each legacy router still using `sb_connection.py`:

1. Create SQLAlchemy models for the data it accesses
2. Create a service that uses SQLAlchemy instead of direct database access
3. Update the router to use the new service with SQLAlchemy
4. Test thoroughly to ensure functionality is preserved

Priority order for migration:

1. `src/routers/admin.py` - Critical for admin dashboard functionality
2. `src/routers/rbac.py` - Important for security features
3. `src/routers/db_portal.py` - Database management functionality
4. `src/routers/email_scanner.py` - Email scanning functionality
5. `src/routers/dev_tools.py` - Development tools

#### Phase 3: Deprecate Legacy Connection (Medium-term)

1. Add deprecation warnings to `sb_connection.py`:

   ```python
   import warnings

   warnings.warn(
       "sb_connection.py is deprecated and will be removed in a future version. "
       "Use SQLAlchemy with async_session.py instead.",
       DeprecationWarning,
       stacklevel=2
   )
   ```

2. Create a migration guide for any remaining code using `sb_connection.py`

3. Set a timeline for complete removal of `sb_connection.py`

#### Phase 4: Complete Removal (Long-term)

1. Verify that no components are using `sb_connection.py`
2. Remove `sb_connection.py` from the codebase
3. Update documentation to reflect the standardized SQLAlchemy approach

## 5. Lessons Learned

### 5.1 Critical Mistakes to Avoid

1. **Silent Fallbacks**: Never silently fall back to a default connection string. Fail loudly if required configuration is missing.

2. **Parallel Systems**: Avoid having two parallel database connection systems. Standardize on one approach.

3. **Incomplete Migrations**: Don't start using a new database access pattern without ensuring it's properly configured.

4. **Missing Validation**: Always validate connection details before attempting to connect.

5. **Inadequate Logging**: Log connection details (with sensitive information redacted) to aid in troubleshooting.

### 5.2 Best Practices to Follow

1. **Single Source of Truth**: Use a single configuration source (settings) for all database connection details.

2. **Connection Pooling**: Always use connection pooling for production environments.

3. **Health Checks**: Implement health check endpoints to verify database connectivity.

4. **Graceful Degradation**: If a database connection fails, provide a clear error message rather than silently failing.

5. **Comprehensive Testing**: Test database connections in all environments (development, staging, production).

## 6. Implementation Timeline

| Phase | Task                                 | Timeline    | Dependencies                     |
| ----- | ------------------------------------ | ----------- | -------------------------------- |
| 1     | Fix SQLAlchemy Connection            | Immediate   | None                             |
| 1     | Add Database Health Check            | Immediate   | SQLAlchemy Connection Fix        |
| 1     | Test RBAC Router                     | Immediate   | SQLAlchemy Connection Fix        |
| 2     | Migrate Admin Router                 | Short-term  | SQLAlchemy Connection Fix        |
| 2     | Migrate Legacy RBAC Router           | Short-term  | SQLAlchemy Connection Fix        |
| 2     | Migrate DB Portal                    | Short-term  | SQLAlchemy Connection Fix        |
| 2     | Migrate Email Scanner                | Medium-term | SQLAlchemy Connection Fix        |
| 2     | Migrate Dev Tools                    | Medium-term | SQLAlchemy Connection Fix        |
| 3     | Add Deprecation Warnings             | Medium-term | All Critical Components Migrated |
| 3     | Create Migration Guide               | Medium-term | Deprecation Warnings Added       |
| 4     | Verify No Usage of Legacy Connection | Long-term   | All Components Migrated          |
| 4     | Remove Legacy Connection             | Long-term   | No Usage Verification            |

## 7. Conclusion

The current database connection issues stem from an incomplete migration to SQLAlchemy with improper configuration. By fixing the SQLAlchemy connection configuration and systematically migrating all components to use it, we can standardize on a single, robust database access pattern.

This plan provides a clear path forward to resolve the immediate issues and complete the migration to SQLAlchemy as outlined in the modernization plan. By following this plan, we will ensure that all components use a consistent, properly configured database connection mechanism.
