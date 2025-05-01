# Immediate Directive: Prohibition of Direct psycopg2 Database Connections

## Executive Order

**EFFECTIVE IMMEDIATELY: All direct psycopg2/asyncpg database connections are PROHIBITED.**

The continued presence of direct database connections using psycopg2 or asyncpg APIs is undermining our modernization efforts and causing critical transaction errors. This directive reinforces the absolute mandate that **all** database operations must use SQLAlchemy ORM exclusively.

## Critical Issues Identified

Recent implementation attempts revealed persistent transaction errors stemming from mixed usage of connection methods:

1. ❌ **Transaction conflicts between pgbouncer and SQLAlchemy**: Errors like "A transaction is already begun on this Session" indicate transaction nesting issues.

2. ❌ **Orphaned transaction blocks**: Errors showing "current transaction is aborted, commands ignored until end of transaction block" indicate incomplete transaction management.

3. ❌ **Connection pooling conflicts**: The system is experiencing conflicts between SQLAlchemy's connection pool and pgbouncer's connection management.

## Implementation Requirements (MANDATORY)

1. **✅ ELIMINATE ALL DIRECT CONNECTIONS**:

   - Remove ALL instances of direct psycopg2/asyncpg connections
   - Remove ALL manual connection string construction
   - Remove ALL custom connection handlers

2. **✅ DATABASE URL STANDARDIZATION**:

   - Use ONLY the standardized `get_db_url()` function from settings
   - Ensure connection strings respect the pool_size and max_overflow settings

3. **✅ SESSION FACTORY USAGE**:

   - Use ONLY `get_db_session()` or `async_session_factory()` for obtaining database sessions
   - NEVER manually create engine or connection objects

4. **✅ PROPER CONNECTION POOL CONFIGURATION**:
   - Update to the Supavisor-compatible connection configuration
   - Set proper pool_pre_ping, pool_size, and max_overflow values

## Implementation Plan

1. **IMMEDIATELY**: Update all database usage to follow transaction patterns documented in `16-TRANSACTION-MANAGEMENT-COMPREHENSIVE-GUIDE.md`

2. **IMMEDIATELY**: Replace pgbouncer-specific connection string with Supavisor-compatible configuration:

```python
# CORRECT CONNECTION CONFIGURATION
from sqlalchemy.ext.asyncio import create_async_engine

def get_engine():
    connection_string = settings.get_db_url()

    # Proper connection pool configuration for Supavisor
    engine = create_async_engine(
        connection_string,
        pool_pre_ping=True,  # Check connection validity before using
        pool_size=5,         # Maintain reasonable pool size
        max_overflow=10,     # Allow for spikes in connection needs
        echo=settings.SQL_ECHO,
        future=True
    )

    return engine
```

3. **IMMEDIATELY**: Update background task handling to create isolated sessions with proper transaction boundaries

## Verification Requirements

ALL code changes MUST be verified against these criteria:

1. ✅ No direct imports of psycopg2 or asyncpg
2. ✅ No manual construction of connection strings
3. ✅ Session objects obtained ONLY via proper factory methods
4. ✅ Proper transaction boundaries (routers own transactions, services don't)
5. ✅ Proper session closure in background tasks
6. ✅ Supavisor-compatible pool configuration

## Confirmation of Success

Implementation success is ONLY confirmed when ALL of the following are true:

1. ✅ Database operations complete successfully
2. ✅ Data is successfully persisted to the database
3. ✅ No transaction errors appear in logs
4. ✅ Sitemap scraping process completes end-to-end with data insertion

## Non-Negotiable Mandate

This directive is NON-NEGOTIABLE. Any continued use of direct psycopg2/asyncpg connections or bypassing SQLAlchemy ORM is STRICTLY FORBIDDEN and will result in immediate rejection of code contributions.

Maintaining database operation standardization is CRITICAL for the stability, security, and scalability of the ScraperSky platform.
