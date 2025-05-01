# Router Files Audit Results

## Overview
This audit examines router files for database access patterns to ensure they follow our standardized approach:
- Routers should own transaction boundaries with `async with session.begin()`
- Sessions should be injected via dependency
- No direct session creation within the router
- Services should be transaction-aware, not transaction-creating

## Files Requiring Updates

### 1. `dev_tools.py`
- **Issues Found:**
  - Creates sessions directly using `get_session()` (lines 439, 577)
  - Direct SQL queries without proper transaction boundaries (lines 302, 446, 545-546)
  - Mixes service calls and direct SQL execution
  - Inconsistent transaction boundary ownership
- **Required Changes:**
  - Implement session dependency in endpoints
  - Establish consistent transaction boundaries with `async with session.begin()`
  - Update service calls to pass session parameter

### 2. `google_maps_api.py`
- **Issues Found:**
  - Creates new sessions in background tasks (lines 164, 279)
  - Inconsistent transaction boundary management
  - Contains inline SQL execution
  - Mixed responsibility model for transaction management
- **Required Changes:**
  - Update background tasks to follow the pattern where they create and manage their own sessions
  - Make service methods transaction-aware but not transaction-creating
  - Ensure router endpoints own transaction boundaries

### 3. `modernized_page_scraper.py`
- **Issues Found:**
  - Imports session directly from db module (line 13)
  - Inconsistent transaction boundary management
  - Unclear responsibility delineation between router and services
- **Required Changes:**
  - Standardize on session dependency in endpoint functions
  - Make router explicitly own transaction boundaries
  - Update service calls to be transaction-aware

### 4. `batch_page_scraper.py`
- **Issues Found:**
  - Creates new sessions in background tasks (lines 173, 279)
  - Mixed transaction boundary responsibility model
  - Inconsistent transaction pattern
- **Required Changes:**
  - Update to consistent transaction boundary ownership by router
  - Ensure background tasks properly create and manage their own sessions
  - Ensure services accept but don't create sessions

### 5. `profile.py`
- **Issues Found:**
  - Handles transactions in the router (lines 63, 108, 154)
  - Passes session to service methods without clear delineation of responsibility
- **Required Changes:**
  - Explicit transaction boundary management
  - Consistent pattern across all endpoints
  - Ensure services are transaction-aware but not transaction-creating

## Completed Files

1. ✅ `sitemap_analyzer.py`
2. ✅ `modernized_sitemap.py`
3. ✅ `db_portal.py`

## Next Steps

1. Prioritize updates based on usage and complexity
2. Create tests for each updated file
3. Update documentation to reflect changes
4. Implement the changes in this order:
   - `dev_tools.py` (contains the most database access issues)
   - `google_maps_api.py` and `batch_page_scraper.py` (background task issues)
   - `modernized_page_scraper.py` and `profile.py` (transaction boundary issues)
