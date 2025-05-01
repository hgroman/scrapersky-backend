# Supabase Connection Configuration Guide

## 🚨 MANDATORY REQUIREMENTS FOR ALL DEVELOPMENT 🚨

**ALWAYS USE SUPAVISOR CONNECTION POOLING FOR ALL DATABASE INTERACTIONS**

This requirement is **ABSOLUTELY NON-NEGOTIABLE** for the following critical reasons:

1. **Deployment Failures**: Applications WILL CRASH on render.com without proper connection pooling
2. **Data Loss**: Scraping results WILL NOT be saved properly without the correct configuration
3. **Performance Issues**: The application WILL EXPERIENCE severe slowdowns without proper pooling

**NO EXCEPTIONS ARE PERMITTED** for ANY development, including:
- All new API endpoints
- All modifications to existing endpoints
- All database migrations with Alembic
- All SQLAlchemy model definitions

See the **[Implementation Checklist](#implementation-checklist)** at the end of this document for a mandatory verification list that MUST be completed for all development.

## Overview

This document explains the proper configuration for connecting to Supabase databases in both development and production environments. It addresses the recent migration from PgBouncer to Supavisor and from IPv4 to IPv6, which has significant implications for database connectivity.

## Background: Supabase's Infrastructure Changes

In late 2023, Supabase announced two major infrastructure changes:

1. **Migration from PgBouncer to Supavisor**: Supabase deprecated PgBouncer in favor of their own connection pooler called Supavisor.
2. **Migration from IPv4 to IPv6**: Direct database connections (`db.projectref.supabase.co`) now resolve to IPv6 addresses instead of IPv4.

These changes required updates to connection strings and configuration parameters to ensure continued functionality.

## Connection Options

There are two primary ways to connect to a Supabase database:

### 1. Supavisor Connection Pooler (Recommended)

**Format**:

```
postgresql+asyncpg://[db-user].[project-ref]:[password]@aws-0-[aws-region].pooler.supabase.com:6543/[db-name]
```

**Example**:

```
postgresql+asyncpg://postgres.abcdefghijklm:password123@aws-0-us-west-1.pooler.supabase.com:6543/postgres
```

**Advantages**:

- Works in environments without IPv6 support
- Provides connection pooling for better performance
- Recommended by Supabase for all production use

**Configuration Parameters**:

- No need for `statement_cache_size=0` parameter (this was specific to PgBouncer)
- Standard SSL configuration works

### 2. Direct Database Connection

**Format**:

```
postgresql+asyncpg://postgres:[password]@db.[project-ref].supabase.co:5432/[db-name]
```

**Example**:

```
postgresql+asyncpg://postgres:password123@db.abcdefghijklm.supabase.co:5432/postgres
```

**Limitations**:

- Requires IPv6 support in your environment
- Not recommended for production use unless you've purchased the IPv4 add-on

## Implementation in ScraperSky

Our implementation in `src/session/async_session.py` handles both connection methods with appropriate fallbacks:

1. First, it checks for a `DATABASE_URL` environment variable
2. If not found, it tries to use Supavisor pooler configuration
3. As a last resort, it falls back to direct connection with a warning

### Key Code Components

```python
# Check for Supavisor pooler configuration (preferred)
pooler_host = settings.supabase_pooler_host
pooler_port = settings.supabase_pooler_port
pooler_user = settings.supabase_pooler_user
password = settings.supabase_db_password
project_ref = None

# Extract project reference from Supabase URL if available
if settings.supabase_url:
    if '//' in settings.supabase_url:
        project_ref = settings.supabase_url.split('//')[1].split('.')[0]
    else:
        project_ref = settings.supabase_url.split('.')[0]

# Use Supavisor pooler if available (preferred for production)
if all([pooler_host, pooler_port, pooler_user]):
    # Format: postgres://[db-user].[project-ref]:[db-password]@aws-0-[aws-region].pooler.supabase.com:6543/[db-name]

    # If pooler_user already includes project_ref, use it directly
    if pooler_user and '.' in pooler_user:
        user_part = pooler_user
    # Otherwise, append project_ref if available
    elif project_ref:
        user_part = f"{pooler_user}.{project_ref}" if pooler_user else f"postgres.{project_ref}"
    else:
        user_part = pooler_user or "postgres"

    connection_string = (
        f"postgresql+asyncpg://{user_part}:{quote_plus(password)}"
        f"@{pooler_host}:{pooler_port}/{dbname}"
    )
    logger.info(f"Using Supabase Supavisor connection pooler at {pooler_host}:{pooler_port}")
    return connection_string
```

## Environment-Specific Configurations

Our implementation includes environment-specific configurations to handle different requirements:

### Development Environment

In development environments, we:

1. **Disable SSL Certificate Verification**: This makes local development easier, especially when using self-signed certificates.
2. **Use Smaller Connection Pool**: We use a smaller connection pool size (5 connections) to conserve resources.
3. **Provide Clear Logging**: We log detailed information about the connection configuration.

```python
# Configure SSL context based on environment
if IS_DEVELOPMENT:
    # Development: Disable SSL verification for easier local development
    logger.warning("Development environment detected: Disabling SSL certificate verification")
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
else:
    # Production: Use proper SSL verification
    logger.info("Production environment detected: Using strict SSL certificate verification")
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = True
    ssl_context.verify_mode = ssl.CERT_REQUIRED

# Create async engine with environment-specific settings
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL query logging in development
    # Use different pool sizes based on environment
    pool_size=5 if IS_DEVELOPMENT else settings.db_max_pool_size,
    max_overflow=5 if IS_DEVELOPMENT else 10,
    pool_timeout=settings.db_connection_timeout,
    pool_recycle=1800,
    connect_args=connect_args
)
```

### Production Environment

In production environments, we:

1. **Enable Strict SSL Verification**: This ensures secure connections to the database.
2. **Use Larger Connection Pool**: We use the configured `db_max_pool_size` (default: 10) for better performance.
3. **Prioritize Supavisor**: We strongly prefer using Supavisor for production environments.

## Common Issues and Solutions

### 1. PgBouncer vs. Supavisor Parameter Differences

**Issue**: PgBouncer required `statement_cache_size=0` to disable prepared statements, but this parameter causes errors with Supavisor.

**Solution**: Remove the `statement_cache_size` parameter when using Supavisor.

### 2. IPv6 Compatibility

**Issue**: Direct database connections now use IPv6, which may not be supported in all environments.

**Solution**: Use Supavisor connection pooler, which continues to support IPv4.

### 3. Connection String Format

**Issue**: The connection string format has changed with Supavisor.

**Solution**: Update connection strings to use the new format:

- Old (PgBouncer): `postgresql://postgres:[password]@db.[project-ref].supabase.co:6543/postgres`
- New (Supavisor): `postgresql://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres`

## Recommendations

1. **Always Use Supavisor in Production**: This ensures compatibility with environments that don't support IPv6.

2. **Set Environment Variables**: Configure your environment with the following variables:

   - `SUPABASE_POOLER_HOST`: The Supavisor host (e.g., `aws-0-us-west-1.pooler.supabase.com`)
   - `SUPABASE_POOLER_PORT`: The Supavisor port (typically `6543`)
   - `SUPABASE_POOLER_USER`: The database user with project reference (e.g., `postgres.abcdefghijklm`)
   - `SUPABASE_DB_PASSWORD`: Your database password

3. **Monitor Connection Usage**: Keep an eye on connection usage to ensure you're not hitting limits.

4. **Use Health Checks**: Implement database health checks to quickly identify connection issues.

## Implementation Checklist

The following checklist MUST be completed for ALL development that interacts with the database:

### 1. Database Connection Configuration
- [ ] Using Supavisor connection string format: `postgresql+asyncpg://postgres.project-ref:password@aws-0-region.pooler.supabase.com:6543/postgres`
- [ ] Connection pooling properly configured with appropriate pool size
- [ ] SSL context properly configured
- [ ] NOT using PgBouncer-specific parameters that conflict with Supavisor

### 2. API Endpoint Implementation
- [ ] ALL endpoints support connection pooling parameters:
  - [ ] `raw_sql=true` parameter implemented
  - [ ] `no_prepare=true` parameter implemented
  - [ ] `statement_cache_size=0` parameter implemented
- [ ] Complex database operations have raw SQL alternatives to avoid prepared statement issues
- [ ] Type conversions handled properly when converting between string IDs and database types

### 3. SQLAlchemy Model Verification
- [ ] ALL models verified against actual database schema using `scripts/db/inspect_table.py`
- [ ] No columns in models that don't exist in the database
- [ ] All relationships properly configured with appropriate parameters
- [ ] Self-referential relationships include `single_parent=True` parameter

### 4. Alembic Migration Verification
- [ ] Migration uses the same connection pooling configuration as the main application
- [ ] Migration includes proper error handling for connection issues
- [ ] Migration is tested in a development environment before deployment

## Conclusion

By properly configuring SQLAlchemy to use Supabase's Supavisor connection pooler, we've ensured that our application can reliably connect to the database in both development and production environments. This approach handles the recent infrastructure changes at Supabase and provides a robust solution for database connectivity.

The implementation in `src/session/async_session.py` provides a flexible, environment-aware configuration that prioritizes the recommended connection methods while maintaining backward compatibility where possible.

**FINAL REMINDER: ALWAYS USE SUPAVISOR CONNECTION POOLING WITH PROPER PARAMETERS**

Failure to follow these requirements will result in:
1. Application failures in production
2. Data loss during scraping operations
3. Performance degradation and timeout errors
4. Connection pool exhaustion and cascading failures

There are NO exceptions to these requirements. Full compliance is MANDATORY for all development.
