# SCRAPERSKY CONSOLIDATION PLAN

This document outlines a concrete plan to consolidate and simplify the ScraperSky backend codebase.

## HIGH-PRIORITY ACTIONS

### 1. CONSOLIDATE SERVICE IMPLEMENTATIONS

| Service Type | KEEP THIS | REMOVE THESE |
|--------------|-----------|--------------|
| Error Service | services/error/error_service.py | services/core/error_service.py<br>services/new/error_service.py |
| Validation Service | services/validation/validation_service.py | services/core/validation_service.py<br>services/new/validation_service.py |
| DB Service | services/core/db_service.py | services/db_service.py |
| Sitemap Service | services/sitemap/sitemap_service.py | services/sitemap_service.py |
| Auth Service | services/core/auth_service.py | auth/auth_service.py |

### 2. REMOVE OBSOLETE ROUTER FILES

| REMOVE | KEEP |
|--------|------|
| routers/page_scraper.py | routers/modernized_page_scraper.py |
| routers/sitemap.py | routers/modernized_sitemap.py |
| routers/modernized_sitemap.bak.3.21.25.py | |

### 3. STANDARDIZE DATABASE CONNECTION

KEEP ONLY:
- src/db/engine.py (SQLAlchemy engine configuration)
- src/db/session.py (Session management)
- src/models/* (SQLAlchemy ORM models)

REMOVE:
- src/db/async_sb_connection.py
- src/db/sb_connection.py
- src/db/sb_connection copy.py

## MEDIUM-PRIORITY ACTIONS

### 4. REMOVE TENANT ISOLATION CODE

Remove these files:
- src/middleware/tenant_middleware.py
- src/auth/tenant_isolation.py

Remove tenant isolation code from:
- src/auth/dependencies.py
- src/auth/jwt_auth.py
- src/routers/profile.py

### 5. CLEAN UP UNUSED FILES

Remove:
- src/utils/db_schema_helper.py
- src/utils/db_utils.py
- src/utils/scraper_api.py
- src/utils/sidebar.py
- src/tasks/email_scraper.py
- src/test_domain_scrape.py
- src/models/sidebar.py

## LOW-PRIORITY ACTIONS

### 6. STANDARDIZE TRANSACTION MANAGEMENT

Ensure all routes follow these patterns:
- Routers own transactions with `async with session.begin()`
- Services are transaction-aware (never create transactions)
- Background tasks create and manage their own sessions/transactions

### 7. UPDATE IMPORT STATEMENTS

After consolidating services:
1. Search for imports of removed files
2. Update them to import the kept files
3. Run tests to ensure functionality is maintained

Example:
```python
# From:
from src.services.core.error_service import handle_error

# To:
from src.services.error.error_service import handle_error
```

## EXPECTED OUTCOMES

After completing this consolidation:

1. Reduced codebase size (22+ files removed)
2. Clearer service boundaries
3. Single source of truth for each service type
4. Improved maintainability
5. Easier onboarding for new developers
6. Consistent transaction management
7. No redundant/confusing duplicate implementations
