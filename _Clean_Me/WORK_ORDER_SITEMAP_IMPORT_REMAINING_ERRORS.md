# Work Order: Fix Remaining Sitemap Import Errors

**ID:** WO-2025-09-14-001
**Priority:** Medium
**Type:** Bug Fix

## Problem

19 sitemap import failures remain after timezone fix deployment:
- 15 timezone errors (cached processes using old code)
- 4 PostgreSQL parameter limit errors (32,767 limit exceeded)

**Evidence**: MCP SQL query shows specific error counts from sitemap_files table.

## Required Fixes

### Fix 1: Clear Cached Timezone Errors
**Target**: 15 remaining timezone errors
**Root Cause**: Background processes still running pre-fix code
**Solution**: Restart sitemap import scheduler service

**Error Pattern**:
```
invalid input for query argument $18: datetime.datetime(2025, 9, 14, 12, 28, 3...
(can't subtract offset-naive and offset-aware datetimes)
```

**Implementation**:
1. Restart background scheduler process
2. Verify no cached instances using manual datetime injection

### Fix 2: PostgreSQL Bulk Insert Limit
**Target**: 4 parameter limit errors
**Root Cause**: Bulk inserts exceeding PostgreSQL 32,767 parameter limit
**Solution**: Implement batch size limiting

**Error Pattern**:
```
the number of query arguments cannot exceed 32767
[SQL: INSERT INTO pages (...) VALUES ($1::UUID, $2::UUID, ...
```

**File**: `src/services/sitemap_import_service.py:274-298`

**Code Change**:
```python
# BEFORE: Single bulk insert of all pages
insert_stmt = pg_insert(Page).values(page_dicts)

# AFTER: Batched inserts with safe limits
MAX_BATCH_SIZE = 1000  # 18 columns * 1000 = 18,000 params (safe)
for i in range(0, len(page_dicts), MAX_BATCH_SIZE):
    batch = page_dicts[i:i + MAX_BATCH_SIZE]
    insert_stmt = pg_insert(Page).values(batch).on_conflict_do_nothing(...)
    await session.execute(insert_stmt)
```

## Expected Results

- **19 additional sitemaps** converted to pages successfully
- **Zero remaining timezone errors**
- **Large sitemaps processed** without parameter limit failures
- **Success rate improvement**: 77% → 78.4% (19/1397 additional)

## Files to Modify

1. `src/services/sitemap_import_service.py` - Add batch size limiting
2. Background process restart - Clear cached timezone errors

## Verification

```sql
-- Check error reduction
SELECT sitemap_import_status, COUNT(*)
FROM sitemap_files
WHERE deep_scrape_curation_status = 'Selected'
GROUP BY sitemap_import_status;
```

Expected: Error count drops from 269 to 250.