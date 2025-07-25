# Technical Debt: SQLAlchemy Enum Value Conversion Issue

**Priority**: P1 (Medium)
**Impact**: Background scheduler error logs (non-blocking)
**Created**: 2025-07-02
**Status**: Identified - Requires Systematic Audit Approach

## Issue Summary

SQLAlchemy is converting Python enum **values** ("Queued") to enum **names** ("QUEUED") in database queries, causing enum validation errors in background schedulers.

## Evidence

**Database Reality** (✅ Correct):

```sql
domain_extraction_status: ['Queued', 'Processing', 'Completed', 'Error']
gcp_api_deep_scan_status: ['Queued', 'Processing', 'Completed', 'Error']
```

**Python Enum Definitions** (✅ Correct):

```python
DomainExtractionStatus.QUEUED.value = 'Queued'  # ✅
DomainExtractionStatus.QUEUED.name = 'QUEUED'   # ❌ This is being used
```

**SQLAlchemy Query Parameters** (❌ Incorrect):

```sql
[parameters: ('QUEUED', 5)]  -- Should be ('Queued', 5)
```

## Current Impact

- Background schedulers log enum validation errors
- Application continues running normally
- All core functionality operational
- Health checks pass (200 OK)

## Root Cause Analysis

**Configuration Attempts Made**:

1. `create_type=False` → `create_type=True`
2. `create_type=True` → `native_enum=False`
3. Direct `.value` usage in queries: `DomainExtractionStatus.QUEUED.value`

**Result**: All approaches still result in SQLAlchemy using enum **names** instead of **values**.

## Affected Components

**Enums**:

- `domain_extraction_status`
- `gcp_api_deep_scan_status`

**Services**:

- `local_business_curation_scheduler.py`
- `staging_editor_scheduler.py`
- `sitemap_scheduler.py`

## Temporary Mitigations Applied

Applied `.value` explicit usage in query comparisons as temporary fix:

```python
# Temporary workaround
.where(LocalBusiness.domain_extraction_status == DomainExtractionStatus.QUEUED.value)
```

**Status**: Still not working - SQLAlchemy continues using enum names.

## Recommended Resolution Approach

**DO NOT**: Continue ad-hoc fixes to this systematic issue.

**DO**: Address through proper DC-2-Model-2-Schema-Audit workflow:

1. **Add to WF7**: SQLAlchemy Enum Configuration Audit
2. **Research**: Systematic SQLAlchemy enum handling patterns
3. **Options to Evaluate**:
   - Database migration to align enum values with Python enum names
   - Complete SQLAlchemy enum configuration refactor
   - String-based status columns instead of native enums

## Integration with Existing Audit

This issue aligns with documented pattern in DC-2-Model-2-Schema-Audit:

- **Root Cause**: Previous rogue agent changes to data layer without schema validation
- **Pattern**: Enum/schema mismatches requiring systematic remediation
- **Priority Framework**: P1 (non-blocking but affects operational logs)

## Success Criteria

1. Background schedulers run without enum validation errors
2. SQLAlchemy queries use correct enum values matching database
3. No impact to application functionality during remediation

## Files for Future Audit

- `src/models/enums.py` - Enum definitions
- `src/models/place.py` - Column configurations
- `src/models/local_business.py` - Column configurations
- All services using enum comparisons in SQLAlchemy queries

---

**Note**: Application is fully operational. This is documentation for systematic future remediation, not an urgent blocking issue.
