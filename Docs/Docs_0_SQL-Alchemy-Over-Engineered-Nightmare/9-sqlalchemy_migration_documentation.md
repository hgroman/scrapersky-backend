# SQLAlchemy Migration Documentation

## Overview

This document tracks the changes made to migrate certain components of the ScraperSky application to use SQLAlchemy. It documents disabled components, modified files, and dependencies that were adjusted to make the SQLAlchemy endpoints functional.

## Date: June 24, 2024

## Issues Encountered

1. **Settings Configuration Issues**:

   - The application was attempting to access settings attributes that did not exist
   - Several attribute errors for fields like `db_min_pool_size`, `db_max_pool_size`, and `db_connection_timeout`
   - Pydantic validation errors for extra fields in Settings class

2. **Import Errors**:

   - Model imports failing (ChatRequest, ChatResponse, PlacesSearchRequest, SitemapAnalyzerRequest)
   - Circular dependencies between routers and database connection modules

3. **URL/Connection String Issues**:
   - Problems with `quote_plus` function usage on potentially None values
   - Type errors related to URL encoding

## Changes Made

### 1. Disabled Routers

The following routers were temporarily disabled to allow the application to start:

```python
# from .chat import router as chat_router  # Missing model dependencies
# from .email_scanner import router as email_scanner_router  # sb_connection dependency
# from .places_scraper import router as places_router  # Missing model dependencies
# from .sitemap_analyzer import router as sitemap_analyzer_router  # Missing model dependencies
```

> **Note:** Email router was confirmed to have never worked properly, so keeping it disabled is acceptable until explicitly brought back online.

### 2. Modified Database Connection Files

#### src/db/sb_connection.py

- Used `getattr()` with default values for accessing settings:

  ```python
  # Before
  self.min_conn = min_conn if min_conn is not None else settings.db_min_pool_size

  # After
  self.min_conn = min_conn if min_conn is not None else getattr(settings, 'db_min_pool_size', 1)
  ```

- Fixed `quote_plus` usage by ensuring string conversion and handling None values:

  ```python
  # Before
  f"postgresql://{self.user}:{quote_plus(self.password)}"

  # After
  f"postgresql://{self.user}:{quote_plus(str(self.password)) if self.password else ''}"
  ```

- Added default cache TTL value:
  ```python
  cache_ttl = getattr(settings, 'cache_ttl', 3600)  # Default 1 hour if not in settings
  ```

#### src/db/engine.py

- Added default value for `db_connection_timeout`:

  ```python
  "command_timeout": getattr(settings, 'db_connection_timeout', 30)  # Default 30 seconds
  ```

- Fixed the same `quote_plus` issues as in sb_connection.py with proper string conversion

#### src/config/settings.py

- Fixed the `validate()` method to correctly return `None` instead of `True` to match its type annotation

### 3. Other Changes

- Ensured the app runs on port 8005 to avoid conflicts with other instances
- Added proper error handling for missing or optional settings

## Components Still Needing Attention

### To Re-enable in Future:

1. **Chat Router**:

   - Need to implement or import the missing `ChatRequest` and `ChatResponse` models

2. **Places Scraper Router**:

   - Need to implement or import the missing `PlacesSearchRequest`, `PlacesSearchResponse`, and `PlacesStatusResponse` models

3. **Sitemap Analyzer Router**:

   - Need to implement or import the missing `SitemapAnalyzerRequest` model

4. **Email Scanner Router**:
   - Noted as never having worked correctly
   - Will need significant work to make functional

## Testing

The SQLAlchemy components of the application are now running successfully.

Testing to date has included:

- Basic application startup
- Verification of running Uvicorn processes
- Successful health check endpoint test at `/api/v1/sqlalchemy-test/health`

We've created two ways to test the SQLAlchemy components:

1. **Main Application**:

   - Includes SQLAlchemy routers alongside existing routers
   - Running on port 8005

2. **Standalone Test Application**:
   - Created `test_sqlalchemy_app.py` for isolated testing
   - Running on port 8007
   - Provides a clean environment for testing SQLAlchemy endpoints without interference from other components

Additional testing needed:

- Direct API endpoint testing with sample data
- Integration testing with frontend components
- Performance benchmarks compared to previous implementation

## Next Steps

1. Complete SQLAlchemy migration for remaining components
2. Implement missing models or create alternative model import strategy
3. Gradually re-enable disabled routers as dependencies are resolved
4. Create comprehensive tests for the migrated components
5. Update documentation as changes progress

## Questions for Further Investigation

1. Are the models for disabled routers planned to be migrated or recreated?
2. Should the settings module be extended to include the previously missing fields?
3. What is the priority order for bringing disabled routers back online?

---

**Document maintained by:** Henry Groman
**Last Updated:** June 24, 2024
