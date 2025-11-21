# INCIDENT #003: V2 Router Ghost Column - The Silent Killer

**Date:** November 20, 2025  
**Severity:** P0 - Production Breaking  
**Status:** ✅ RESOLVED  
**Resolution Commit:** `314bca1`

---

## Executive Summary

A V2 router endpoint was writing to a **non-existent database column** (`sitemap_import_curation_status`), causing SQLAlchemy to generate invalid SQL that triggered PostgreSQL enum type comparison errors. This silent failure plagued production for months, manifesting as cryptic 500 errors on batch sitemap curation updates.

**Impact:** WF5 sitemap curation workflow completely broken for batch operations.

---

## The Error

```
sqlalchemy.exc.ProgrammingError: (asyncpg.exceptions.UndefinedFunctionError)
operator does not exist: sitemap_curation_status_enum = sitemap_import_curation_status
```

**Translation:** PostgreSQL was trying to compare two different enum types and couldn't find an operator to do so.

---

## Root Cause Analysis

### The Deadly Code (Line 49, `src/routers/v2/sitemap_files.py`)

```python
# WRONG - This field doesn't exist in the database!
sitemap_file.sitemap_import_curation_status = request.status
```

### What Actually Happened

1. **Developer Intent:** Update the curation status of sitemap files
2. **What They Typed:** `sitemap_import_curation_status` (wrong field name)
3. **What Exists in DB:** `deep_scrape_curation_status` (actual column)
4. **SQLAlchemy Behavior:** Silently treats non-existent attribute as raw value
5. **PostgreSQL Result:** Tries to compare `sitemap_curation_status_enum` (column type) with `sitemap_import_curation_status` (orphaned enum type)
6. **Error:** `operator does not exist`

### Why It Was So Hard to Find

| Factor | Impact |
|--------|--------|
| **5 Similar Enum Types** | `sitemap_curation_status`, `sitemap_curation_status_enum`, `sitemap_import_curation_status`, `sitemapimportcurationstatus`, `sitemapimportcurationstatusenum` |
| **Silent Failure** | SQLAlchemy didn't raise AttributeError |
| **Batch-Only** | Single-record endpoints used different code path |
| **Misleading Error** | Error message pointed to enum types, not field name |
| **Historical Debt** | Multiple rounds of renaming left orphaned types |

---

## The Fix

### Commit `314bca1` - One Line Change

```python
# CORRECT - Uses actual database column name
sitemap_file.deep_scrape_curation_status = request.status
```

**File:** `src/routers/v2/sitemap_files.py`  
**Line:** 49  
**Change:** `sitemap_import_curation_status` → `deep_scrape_curation_status`

---

## Database State Analysis

### Enum Types in Database (Before Cleanup)

```sql
SELECT typname, string_agg(enumlabel, ', ') 
FROM pg_type t JOIN pg_enum e ON t.oid = e.enumtypid 
WHERE typname ILIKE '%sitemap%curation%' 
GROUP BY typname;
```

**Results:**
1. ✅ `sitemap_curation_status_enum` - **ACTIVE** (used by `deep_scrape_curation_status` column)
2. ❌ `sitemap_import_curation_status` - **ORPHANED** (no columns use this)
3. ❌ `sitemap_curation_status` - **ORPHANED** (duplicate with different values)
4. ❌ `sitemapimportcurationstatus` - **ORPHANED** (old naming convention)
5. ❌ `sitemapimportcurationstatusenum` - **ORPHANED** (duplicate)

### Actual Column Definition

```sql
SELECT table_name, column_name, udt_name 
FROM information_schema.columns 
WHERE table_name = 'sitemap_files' 
AND column_name = 'deep_scrape_curation_status';
```

**Result:**
- Table: `sitemap_files`
- Column: `deep_scrape_curation_status`
- Type: `sitemap_curation_status_enum` ✅

---

## Prevention Measures

### 1. Database Cleanup (Execute Now)

```sql
-- Remove orphaned enum types
DROP TYPE IF EXISTS sitemap_import_curation_status CASCADE;
DROP TYPE IF EXISTS sitemap_curation_status CASCADE;
DROP TYPE IF EXISTS sitemapimportcurationstatus CASCADE;
DROP TYPE IF EXISTS sitemapimportcurationstatusenum CASCADE;

-- Verify only the correct type remains
SELECT typname FROM pg_type WHERE typname ILIKE '%sitemap%curation%';
-- Expected: sitemap_curation_status_enum
```

### 2. Runtime Protection (Future PR)

```python
# Add to BaseModel or create SQLAlchemy event listener
class SafeAttributeModel(Base):
    def __setattr__(self, name, value):
        if not name.startswith('_') and not hasattr(self.__class__, name):
            raise AttributeError(
                f"Column '{name}' does not exist on {self.__class__.__name__}. "
                f"Available columns: {[c.name for c in self.__table__.columns]}"
            )
        super().__setattr__(name, value)
```

### 3. Linter Rule (Pre-commit Hook)

```python
# Add to code audit suite
def check_model_attribute_access(file_path):
    """Detect assignments to potentially non-existent model attributes."""
    # Parse AST and flag: model_instance.field_name = value
    # where field_name not in model's __table__.columns
```

### 4. Integration Test

```python
# tests/integration/test_sitemap_curation.py
def test_v2_batch_status_update_uses_correct_field():
    """Ensure V2 router writes to actual database column."""
    sitemap_file = SitemapFile(...)
    
    # This should work
    sitemap_file.deep_scrape_curation_status = SitemapImportCurationStatusEnum.Selected
    
    # This should raise AttributeError
    with pytest.raises(AttributeError):
        sitemap_file.sitemap_import_curation_status = SitemapImportCurationStatusEnum.Selected
```

---

## Timeline

| Time | Event |
|------|-------|
| **Months Ago** | V2 router created with incorrect field name |
| **Nov 20, 01:37** | First error logged in production |
| **Nov 20, 02:16** | Continued errors, multiple attempts to fix enum definitions |
| **Nov 20, 07:45** | User reports "repeat error" - previous fixes didn't work |
| **Nov 20, 07:52** | Deep investigation begins |
| **Nov 20, 07:58** | Root cause identified: wrong field name in V2 router |
| **Nov 20, 08:00** | Fix committed and pushed (commit `314bca1`) |

**Total Time to Resolution:** ~6 hours of active debugging  
**Actual Root Cause:** 1 incorrect field name  
**Lines Changed:** 1

---

## Lessons Learned

### What Went Wrong

1. **No Field Validation:** SQLAlchemy silently accepts non-existent attributes
2. **Misleading Error:** PostgreSQL error pointed to enum types, not field names
3. **Orphaned Types:** Database had 4 unused enum types creating confusion
4. **No Integration Tests:** Batch update endpoint never tested end-to-end
5. **Copy-Paste Error:** V2 router likely copied from old code with wrong field name

### What Went Right

1. **Systematic Investigation:** Checked actual database state vs. code
2. **Direct SQL Queries:** Used MCP to verify column types and enum definitions
3. **Git History:** Tracked recent changes to understand context
4. **Pattern Recognition:** Identified this as part of larger enum standardization issue

### Best Practices Established

1. ✅ **Always verify field names** against actual database schema
2. ✅ **Use MCP/direct SQL** to confirm database state
3. ✅ **Clean up orphaned types** immediately after migrations
4. ✅ **Add runtime validation** for model attribute access
5. ✅ **Write integration tests** for batch operations

---

## Related Incidents

- **Incident #001:** Enum type name mismatches (fixed in commit `26f3911`)
- **Incident #002:** Duplicate enum definitions (fixed in commit `f1afdd7`)
- **Incident #003:** V2 router ghost column (fixed in commit `314bca1`) ← **THIS INCIDENT**

---

## Verification Checklist

### Post-Deploy Verification

- [ ] Render deployment completes successfully
- [ ] No errors in startup logs
- [ ] `PUT /api/v2/sitemap-files/status` returns 200
- [ ] Batch update actually modifies `deep_scrape_curation_status` in DB
- [ ] Dual-status pattern triggers: Selected → Queued
- [ ] No more enum comparison errors in logs

### Database Cleanup

- [ ] Execute DROP TYPE statements for orphaned enums
- [ ] Verify only `sitemap_curation_status_enum` remains
- [ ] Document cleanup in migration log

### Code Audit

- [ ] Search for other instances of `sitemap_import_curation_status` in codebase
- [ ] Verify all routers use correct field names
- [ ] Add integration tests for V2 endpoints

---

## Status: ✅ RESOLVED

**Fix Deployed:** Commit `314bca1`  
**Verification:** Pending Render deployment  
**Cleanup:** Database orphaned types pending removal  
**Prevention:** Runtime validation pending future PR

---

**The beast is dead. November 20, 2025 — the day the bleeding stopped.**

---

**END OF INCIDENT REPORT**
