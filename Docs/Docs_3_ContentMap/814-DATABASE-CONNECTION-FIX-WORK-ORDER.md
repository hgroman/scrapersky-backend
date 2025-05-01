# Database Connection Fix Work Order

## Overview

This work order addresses the database connection error occurring in the ContentMap feature, specifically the `invalid connection option "command_timeout"` error. This issue is preventing successful database operations and needs to be fixed to ensure proper persistence of sitemap data.

## Problem Analysis

1. **Error Details**:

   ```
   psycopg2.ProgrammingError: invalid dsn: invalid connection option "command_timeout"
   ```

2. **Root Cause**:

   - The `command_timeout` parameter is being passed to both `psycopg2` and `asyncpg` connections in `src/db/engine.py`
   - While `command_timeout` is a valid parameter for `asyncpg`, it is not supported by `psycopg2`
   - This mismatch is causing the error when background tasks attempt to create new database connections

3. **Affected Components**:
   - Background processing in `src/services/sitemap/processing_service.py`
   - Database connection configuration in `src/db/engine.py`
   - Any other service using synchronous database connections

## Implementation Plan

### 1. Update Database Engine Configuration

Modify `src/db/engine.py` to handle connection parameters differently for synchronous and asynchronous connections:

```python
# For async connections (using asyncpg)
connect_args = {
    "ssl": "require",
    "command_timeout": settings.db_connection_timeout,  # Keep for asyncpg
    "server_settings": {
        "search_path": "public",
        "application_name": "scraper_sky"
    },
    "prepared_statement_name_func": lambda: f"__asyncpg_{uuid.uuid4()}__",
    "statement_cache_size": 0
}

# For sync connections (using psycopg2), don't include command_timeout
sync_connect_args = {
    "sslmode": "require",
    # Remove command_timeout here
    "prepared_statement_name_func": lambda: f"__psycopg2_stmt_{uuid.uuid4().hex}__"
}
```

### 2. Fix Synchronous Engine Creation

Update the `get_sync_engine()` function in `src/db/engine.py`:

```python
def get_sync_engine():
    """
    Get or create a synchronous SQLAlchemy engine.
    """
    global _sync_engine
    if _sync_engine is None:
        from sqlalchemy import create_engine
        import uuid

        # Generate unique prepared statement names to avoid conflicts
        prepared_statement_name_func = lambda: f"__psycopg2_stmt_{uuid.uuid4().hex}__"

        # Create engine with proper settings for Supavisor - remove command_timeout
        _sync_engine = create_engine(
            get_sync_url(),
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10,
            connect_args={
                "sslmode": "require",
                # command_timeout removed
                "prepared_statement_name_func": prepared_statement_name_func
            }
        )
        logging.info("Created synchronous SQLAlchemy engine")
    return _sync_engine
```

### 3. Implement Connection Parameter Compatibility Layer

Add a utility function to ensure connection parameters are compatible with the database driver:

```python
def get_compatible_connect_args(is_async=True):
    """
    Get connection arguments compatible with the specified driver type.

    Args:
        is_async: Whether this is for an async connection (asyncpg) or sync (psycopg2)

    Returns:
        Dictionary of connection arguments
    """
    base_args = {
        "server_settings": {
            "search_path": "public",
            "application_name": "scraper_sky"
        },
        "prepared_statement_name_func": lambda: f"__{'asyncpg' if is_async else 'psycopg2'}_{uuid.uuid4()}__",
    }

    if is_async:
        # asyncpg specific parameters
        base_args.update({
            "ssl": "require",
            "command_timeout": settings.db_connection_timeout,
            "statement_cache_size": 0
        })
    else:
        # psycopg2 specific parameters
        base_args.update({
            "sslmode": "require",
            # no command_timeout for psycopg2
        })

    # When using Supavisor pooler, add compatibility options
    if db_config.pgbouncer_mode:
        base_args["server_settings"].update({
            "options": "-c search_path=public"
        })

    return base_args
```

### 4. Update Database Session Creation

Ensure the session creation logic uses the appropriate connection parameters:

```python
# In src/db/session.py or equivalent

# For async sessions
async_engine = create_async_engine(
    get_supavisor_ready_url(db_config.async_connection_string),
    pool_size=settings.db_min_pool_size,
    max_overflow=settings.db_max_pool_size - settings.db_min_pool_size,
    pool_timeout=settings.db_connection_timeout,
    pool_recycle=1800,
    echo=sql_echo,
    connect_args=get_compatible_connect_args(is_async=True),
    execution_options={
        "isolation_level": "READ COMMITTED",
        "postgresql_expert_mode": True
    }
)

# For sync sessions
sync_engine = create_engine(
    get_sync_url(),
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    connect_args=get_compatible_connect_args(is_async=False)
)
```

## Testing Plan

1. **Unit Testing**:

   - Test creating both synchronous and asynchronous database connections
   - Verify parameter compatibility with both drivers

2. **Integration Testing**:

   - Test the ContentMap sitemap scanning feature
   - Monitor logs for database connection errors
   - Verify sitemap data is properly stored in the database

3. **Verification SQL Queries**:

   ```sql
   -- Check for sitemap files with the test job ID
   SELECT COUNT(*) FROM sitemap_files WHERE job_id = '<test_job_id>';

   -- Verify domain creation worked
   SELECT id, domain FROM domains WHERE domain = 'example.com';
   ```

## Deployment Steps

1. **Development Changes**:

   - Implement the changes to `src/db/engine.py`
   - Update session creation if needed

2. **Docker Environment**:

   - Rebuild the Docker container: `docker-compose build scrapersky`
   - Restart the service: `docker-compose restart scrapersky`

3. **Testing**:
   - Run a test scan: `curl -X POST "http://localhost:8000/api/v3/sitemap/scan" -H "Authorization: Bearer scraper_sky_2024" -H "X-Tenant-ID: 550e8400-e29b-41d4-a716-446655440000" -H "Content-Type: application/json" -d '{"base_url": "example.com", "tenant_id": "550e8400-e29b-41d4-a716-446655440000", "max_pages": 100}'`
   - Check job status after 10 seconds
   - Verify database records were created

## Success Criteria

The implementation is considered successful when:

1. No `invalid connection option "command_timeout"` errors appear in logs
2. Database connections are established successfully for both sync and async operations
3. ContentMap sitemap data is properly persisted to the database
4. Job status can be retrieved from both in-memory cache and database

## Additional Considerations

1. **Version Compatibility**:

   - Ensure the solution works with the current versions of psycopg2 and asyncpg
   - Document any version-specific requirements

2. **Error Handling**:

   - Improve error handling to provide clearer messages when connection issues occur
   - Add retry logic for transient database connection failures

3. **Documentation**:
   - Update documentation to reflect the connection parameter requirements
   - Document the differences between psycopg2 and asyncpg parameter handling

## Reference

- SQLAlchemy documentation: https://docs.sqlalchemy.org/en/20/dialects/postgresql.html
- asyncpg documentation: https://magicstack.github.io/asyncpg/current/
- psycopg2 documentation: https://www.psycopg.org/docs/
- Supabase connection guidelines (from README.md)
