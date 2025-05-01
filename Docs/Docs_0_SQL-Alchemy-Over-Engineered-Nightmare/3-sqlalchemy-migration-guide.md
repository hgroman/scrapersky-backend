# ScraperSky SQLAlchemy Migration Guide

## Migration Overview

We're implementing SQLAlchemy to replace the custom database connections in `sb_connection.py` and `async_sb_connection.py`. This migration will standardize database access patterns, leverage industry best practices, and simplify the codebase.

## Technical Approach

1. Implement async SQLAlchemy with asyncpg
2. Reverse-engineer existing tables into SQLAlchemy models
3. Create a generic service layer for database operations
4. Set up Alembic for future schema migrations
5. Migrate scrapers one by one, starting with sitemap_scraper.py

## Current Progress

- ✅ Reviewed modernization context and SQLAlchemy roadmap
- ✅ Clarified implementation details:
  - Using async SQLAlchemy exclusively with asyncpg
  - Need to model domains, places_staging, and jobs tables
  - Will use Alembic for future migrations
  - Must maintain API compatibility
  - Will implement appropriate connection pooling
- ✅ Created core SQLAlchemy infrastructure:
  - `src/db/engine.py` - Database engine with connection pooling
  - `src/db/session.py` - Async session management
  - `src/models/base.py` - Base model definitions
- ✅ Created initial models:
  - `src/models/domain.py` - Domain model
  - `src/models/job.py` - Job model
- ✅ Created service layer:
  - `src/services/domain_service.py` - Domain service
  - `src/services/job_service.py` - Job service

## Next Steps

1. Set up Alembic for migrations:

   - Initialize Alembic
   - Create first migration script matching current schema

2. Update first endpoint (sitemap_scraper.py):

   - Convert route to use SQLAlchemy
   - Test endpoint functionality

3. Update remaining endpoints:

   - Convert remaining scrapers one by one
   - Verify functionality with tests

4. Complete migration:
   - Remove old database connections
   - Document new patterns for development

## Implementation Files

### Database Engine (`src/db/engine.py`)

- Created database connection configuration
- Set up SQLAlchemy async engine
- Implemented connection pooling settings
- Handled both direct and pooler connections

### Session Management (`src/db/session.py`)

- Created async session factory
- Implemented FastAPI dependency for endpoints
- Created context managers for services
- Added transaction context manager

### Models

- Created Base model with common fields (id, created_at, updated_at)
- Implemented Domain model with tenant isolation
- Implemented Job model with relationship to Domain
- Added serialization support (to_dict methods)

### Services

- Created DomainService for domain operations
- Created JobService for job operations
- Implemented consistent tenant isolation
- Added proper UUID handling

## Technical Decisions

### Async Implementation

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

engine = create_async_engine(
    f"postgresql+asyncpg://{username}:{password}@{host}:{port}/{database}",
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800,
    echo=True  # For development
)

async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Usage pattern
async with async_session() as session:
    # Database operations
    await session.commit()
```

### Connection Pooling

- Base pool size: 5 connections
- Max overflow: 10 additional connections (15 total)
- Connection timeout: 30 seconds
- Connection recycle: 30 minutes

### Models Structure

We'll create models for:

- `domains` - Website domain information
- `places_staging` - Location data from places scraper
- `jobs` - Background job tracking

All models include tenant isolation via tenant_id fields.

## References

- [SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org/en/20/)
- [SQLAlchemy Async Documentation](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [Alembic Documentation](https://alembic.sqlalchemy.org/en/latest/)
