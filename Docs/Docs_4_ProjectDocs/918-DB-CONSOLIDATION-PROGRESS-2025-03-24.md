# DATABASE SERVICE CONSOLIDATION PROGRESS

## ⚠️ MANDATORY DIRECTIVES ⚠️

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

## GOAL
Standardize on `services/core/db_service.py` for all database operations to ensure consistent transaction handling and connection management.

## KEY PATTERNS TO FOLLOW
1. Routers should own transaction boundaries - use `async with session.begin()`
2. Services should be transaction-aware but not create their own transactions
3. Replace direct SQL with `db_service` methods where possible
4. Don't modify backup files (.bak extension)

## ⚠️ CRITICAL SUPAVISOR REQUIREMENTS ⚠️
- ONLY use Supavisor connection strings with proper format:
  `postgresql+asyncpg://postgres.your-project:password@aws-0-us-west-1.pooler.supabase.com:6543/postgres`
- NEVER use direct database connections or PgBouncer configurations
- ALWAYS configure proper pool parameters:
  ```python
  pool_pre_ping=True
  pool_size=5 (minimum)
  max_overflow=10 (recommended)
  ```
- ALL database-intensive endpoints MUST support connection pooling parameters:
  `raw_sql=true`, `no_prepare=true`, `statement_cache_size=0`

## Progress Tracking

### Completed Files
| File | Status | Notes |
|------|--------|-------|
| google_maps_api.py | ✅ DONE | Reference implementation for transaction pattern |
| profile.py | ✅ DONE | Uses proper transaction boundaries |
| batch_page_scraper.py | ✅ DONE | Background task session handling fixed |
| modernized_sitemap.py | ✅ DONE | Updated to follow transaction pattern |
| sitemap_analyzer.py | ✅ DONE | Fixed direct SQL queries with parameterized queries |

### In Progress
| File | Status | Notes |
|------|--------|-------|
| dev_tools.py | 🔄 IN PROGRESS | Direct session creation needs fixing |
| db_portal.py | 🔄 IN PROGRESS | Service-managed transactions need refactoring |

### Not Started
| File | Status | Notes |
|------|--------|-------|
| modernized_page_scraper.py | ⏱ PENDING | Low-priority but needs transaction boundary updates |

## Common Issues Found

1. **Direct Session Creation**:
   - Problem: Some endpoints create sessions directly instead of using dependency injection
   - Solution: Convert to use `session: AsyncSession = Depends(get_db_session)`

2. **Service-Managed Transactions**:
   - Problem: Services creating/committing their own transactions
   - Solution: Move transaction boundaries to router level

3. **Raw SQL with String Concatenation**:
   - Problem: Security risk with direct string concatenation in SQL queries
   - Solution: Use parameterized queries via db_service

4. **Inconsistent Session Handling**:
   - Problem: Mixed patterns for session management
   - Solution: Standardize on dependency injection pattern

## Implementation Verification

For each updated file, verify:
1. Router uses `async with session.begin()` for transaction boundaries
2. Services accept session parameter but never manage transactions
3. Background tasks create their own sessions
4. All direct SQL replaced with db_service methods
5. No string concatenation in SQL queries
6. Proper error handling with transaction rollback

## Next Steps

1. Complete dev_tools.py refactoring
2. Update db_portal.py transaction patterns
3. Finalize modernized_page_scraper.py updates
4. Document completion in follow-up report