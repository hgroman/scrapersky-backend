# DATABASE CONSOLIDATION MASTER REFERENCE

**Date:** 2025-03-24
**Status:** COMPLETED
**Version:** 1.1

## 1. OVERVIEW & PURPOSE

This document serves as the master reference for the ScraperSky database service consolidation effort. It provides context, goals, approach, and progress tracking to ensure continuity throughout the simplification process. This document should be referenced at the start of any new AI session focused on database consolidation.

## 2. CRITICAL DIRECTIVE

**THE PRIMARY OBJECTIVE IS SIMPLIFICATION AND STANDARDIZATION:**

1. **SIMPLIFY** - Reduce code, not add more
2. **STANDARDIZE** - One consistent database connectivity pattern everywhere
3. **ELIMINATE REDUNDANCY** - Remove duplicate functionality, not create more
4. **CONSOLIDATE** - Use `services/core/db_service.py` as the single standard

**STRICTLY PROHIBITED:**
- Adding new functionality
- Creating new patterns
- Any form of scope creep
- Inventing new approaches

**THIS IS A CLEANUP AND STANDARDIZATION EFFORT ONLY**

## 3. KEY DOCUMENTS

| Document | Path | Purpose |
|----------|------|---------|
| Database Service Consolidation Plan | `/analysis_results/DATABASE_SERVICE_CONSOLIDATION_PLAN.md` | Detailed plan for standardization |
| Database Consolidation Progress | `/analysis_results/DATABASE_CONSOLIDATION_PROGRESS.md` | Tracking of progress made so far |
| Database Connection Standards | `/AI_GUIDES/07-DATABASE_CONNECTION_STANDARDS.md` | Mandatory connection standards |
| Transaction Pattern Reference | `/analysis_results/TRANSACTION_PATTERN_REFERENCE.md` | Reference for transaction handling |
| Database Routes Audit | `/DB_CONSOLIDATION/01-DATABASE-ROUTES-AUDIT.md` | Complete audit of current database access patterns |

## 4. DATABASE SERVICE TARGET STANDARDS

### Core Principle
> **"Routers own transaction boundaries, services are transaction-aware but do not create transactions."**

### Database Access Standard
All database access must use `services/core/db_service.py`, which provides standardized methods:
- `fetch_one()` - Fetch a single row
- `fetch_all()` - Fetch multiple rows
- `execute()` - Execute a query with no results
- `execute_many()` - Execute multiple queries

### Transaction Management Standard
- **Routers** must use `async with session.begin():` to own transaction boundaries
- **Services** must accept session parameters and not create transactions
- **Background tasks** must create their own sessions and manage their own transactions

### Connection Standard
- **ONLY** use Supavisor connection strings with proper format:
  `postgresql+asyncpg://postgres.your-project:password@aws-0-us-west-1.pooler.supabase.com:6543/postgres`
- **NEVER** use direct database connections or PgBouncer configurations
- **ALWAYS** configure proper pool parameters:
  ```python
  pool_pre_ping=True
  pool_size=5 (minimum)
  max_overflow=10 (recommended)
  ```
- ALL database-intensive endpoints MUST support connection pooling parameters:
  `raw_sql=true`, `no_prepare=true`, `statement_cache_size=0`

## 5. REFERENCE IMPLEMENTATION

Use `src/routers/google_maps_api.py` as the reference implementation. This file demonstrates:
1. Router-owned transactions
2. Transaction-aware services
3. Proper background task session management
4. Clean separation of concerns

## 6. COMPLETED STANDARDIZATION TARGETS

### HIGH PRIORITY - COMPLETED
- [✓] `src/db/sitemap_handler.py` - Replaced direct SQL with db_service
- [✓] `src/routers/sitemap_analyzer.py` - Updated transaction handling, fixed security issues
- [✓] `src/routers/db_portal.py` - Standardized on db_service, added transaction boundaries

### MEDIUM PRIORITY - COMPLETED
- [✓] `src/db/domain_handler.py` - Reviewed and updated to db_service
- [✓] `src/routers/modernized_sitemap.py` - Updated to use db_service consistently
- [✓] `src/services/db_inspector.py` - Standardized on db_service
- [✓] `src/routers/modernized_page_scraper.py` - Updated to use standardized session handling
- [✓] `src/routers/dev_tools.py` - Updated to follow standardized database access patterns

### LOW PRIORITY - COMPLETED
- [✓] `src/services/places/places_service.py` - Reviewed and updated for transaction-awareness
- [✓] `src/services/places/places_search_service.py` - Reviewed and updated for transaction-awareness
- [✓] `src/services/places/places_storage_service.py` - Reviewed and updated for transaction-awareness

## 7. PROGRESS TRACKING - COMPLETED

| File | Status | Notes | Date |
|------|--------|-------|------|
| `src/db/sitemap_handler.py` | ✅ Completed | Updated to be transaction-aware | 2025-03-24 |
| `src/routers/sitemap_analyzer.py` | ✅ Completed | Security issues fixed, transaction boundaries added | 2025-03-24 |
| `src/routers/db_portal.py` | ✅ Completed | Added transaction boundaries | 2025-03-24 |
| `src/db/domain_handler.py` | ✅ Completed | Updated to accept session parameter | 2025-03-24 |
| `src/routers/modernized_sitemap.py` | ✅ Completed | Updated to own transaction boundaries | 2025-03-24 |
| `src/services/db_inspector.py` | ✅ Completed | Updated to accept session parameter | 2025-03-24 |
| `src/routers/dev_tools.py` | ✅ Completed | Standardized session management | 2025-03-24 |
| `src/routers/google_maps_api.py` | ✅ Completed | Updated to use standardized session handling | 2025-03-24 |
| `src/routers/batch_page_scraper.py` | ✅ Completed | Added transaction boundaries | 2025-03-24 |
| `src/routers/modernized_page_scraper.py` | ✅ Completed | Updated to use standardized session handling | 2025-03-24 |
| `src/routers/profile.py` | ✅ Completed | Standardized session dependency | 2025-03-24 |

## 8. IMPLEMENTATION APPROACH

1. Start with highest priority files
2. For each file:
   - Study the current implementation
   - Identify database access patterns
   - Update to use `db_service` consistently
   - Ensure proper transaction boundaries
   - Test thoroughly
   - Update progress in this document
3. Move to next priority file

## 9. VERIFICATION CHECKLIST

For each updated file, verify:

- [ ] Uses `db_service` for all database operations
- [ ] Router owns transaction boundaries with `async with session.begin()`
- [ ] Services accept session parameter and don't create transactions
- [ ] Background tasks create their own sessions and manage transactions
- [ ] No direct database connections
- [ ] Proper error handling for transaction rollback
- [ ] No nested transactions