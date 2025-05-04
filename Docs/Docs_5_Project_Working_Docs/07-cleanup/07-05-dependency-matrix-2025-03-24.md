# ScraperSky Backend Dependency Matrix

## Overview

This document provides a comprehensive dependency matrix showing which files in the ScraperSky backend codebase are actively used and which can be safely removed. The analysis is based on tracing dependencies from `main.py` through all active routers and their dependencies.

## Active Routers

Based on the imports in `main.py`, the following routers are actively being used:

1. `google_maps_router` (from `/src/routers/google_maps_api.py`)
2. `modernized_sitemap_router` (from `/src/routers/modernized_sitemap.py`)
3. `batch_page_scraper_router` (from `/src/routers/batch_page_scraper.py`)
4. `dev_tools_router` (from `/src/routers/dev_tools.py`)
5. `db_portal_router` (from `/src/routers/db_portal.py`)
6. `profile_router` (from `/src/routers/profile.py`)
7. SQLAlchemy routers (from `/src/routers/sqlalchemy/__init__.py`)

## Key Service Dependencies

These active routers depend on the following key services:

1. **Authentication and User Context**
   - `/src/auth/jwt_auth.py` - Used for JWT authentication
   - `/src/services/core/user_context_service.py` - Used for managing user context

2. **Database Services**
   - `/src/session/async_session.py` - Used for database session management
   - `/src/services/core/db_service.py` - Used for database operations

3. **Error Handling**
   - `/src/services/core/error_service.py` - Used for standardized error handling

4. **Domain-Specific Services**
   - `/src/services/places/places_service.py` - Used by Google Maps router
   - `/src/services/places/places_search_service.py` - Used by Google Maps router
   - `/src/services/places/places_storage_service.py` - Used by Google Maps router
   - `/src/services/sitemap/processing_service.py` - Used by Modernized Sitemap router
   - `/src/services/batch/batch_processor_service.py` - Used by Batch Page Scraper router
   - `/src/services/profile_service.py` - Used by Profile router
   - `/src/services/db_inspector.py` - Used by DB Portal router

5. **Core Utilities**
   - `/src/utils/db_helpers.py` - Used by multiple routers
   - `/src/core/response.py` - Used for standardized responses

## Duplicate Services

The following duplicate services have been identified:

| Primary Service | Duplicates | Status |
|-----------------|------------|--------|
| `/src/services/core/error_service.py` | `/src/services/error/error_service.py`<br>`/src/services/new/error_service.py` | Duplicates can be removed |
| `/src/services/core/validation_service.py` | `/src/services/validation/validation_service.py`<br>`/src/services/new/validation_service.py` | Duplicates can be removed |
| `/src/services/core/db_service.py` | `/src/services/db_service.py` | Duplicate can be removed |

## Backup Files

The following backup files can be safely removed:

1. `/src/session/async_session.py.bak`
2. `/src/services/sitemap/processing_service.py.bak`
3. `/src/routers/modernized_sitemap.bak.3.21.25.py`

## Obsolete Routers

The following routers are commented out in `main.py` and can be safely removed:

1. `/src/routers/page_scraper.py` - Marked as "removed (v2 API)"
2. `/src/routers/sitemap.py` - Marked as "obsolete, to be removed in v4.0"

## Full Dependency Graph

### 1. google_maps_router
```
/src/routers/google_maps_api.py
├── /src/session/async_session.py
├── /src/models.py (Place, PlaceSearch)
├── /src/auth/jwt_auth.py
├── /src/services/places/places_service.py
├── /src/services/places/places_search_service.py
├── /src/services/places/places_storage_service.py
├── /src/services/job_service.py
└── /src/config/settings.py
```

### 2. modernized_sitemap_router
```
/src/routers/modernized_sitemap.py
├── /src/session/async_session.py
├── /src/auth/jwt_auth.py
├── /src/services/sitemap/processing_service.py
├── /src/models/api_models.py
├── /src/services/batch/batch_processor_service.py
└── /src/config/settings.py
```

### 3. batch_page_scraper_router
```
/src/routers/batch_page_scraper.py
├── /src/session/async_session.py
├── /src/models.py
├── /src/auth/jwt_auth.py
├── /src/services/core/user_context_service.py
├── /src/services/page_scraper.py
├── /src/services/batch/batch_processor_service.py
├── /src/utils/db_helpers.py
└── /src/config/settings.py
```

### 4. dev_tools_router
```
/src/routers/dev_tools.py
├── /src/session/async_session.py
├── /src/auth/jwt_auth.py
├── /src/db/sitemap_handler.py
└── /src/services/core/user_context_service.py
```

### 5. db_portal_router
```
/src/routers/db_portal.py
├── /src/services/db_inspector.py
└── /src/session/async_session.py
```

### 6. profile_router
```
/src/routers/profile.py
├── /src/models/profile.py
├── /src/services/profile_service.py
├── /src/auth/jwt_auth.py
├── /src/models/tenant.py
├── /src/session/async_session.py
├── /src/utils/db_helpers.py
└── /src/core/response.py
```

### 7. SQLAlchemy Routers
```
/src/routers/sqlalchemy/__init__.py
└── (Simple test router with no significant dependencies)
```

## Common Service Dependencies

```
/src/services/error/error_service.py
├── Used to wrap all router endpoints
└── Provides standardized error handling
```

```
/src/session/async_session.py
├── Used for database session management
└── Used by all routers that interact with the database
```

```
/src/auth/jwt_auth.py
├── Used for authentication
└── Used by most routers
```

## Conclusion

This dependency matrix clearly shows which files are actively used in the application and which can be safely removed. By focusing on the active dependencies traced from `main.py`, we can confidently identify and remove unused, duplicate, and backup files to simplify the codebase.
