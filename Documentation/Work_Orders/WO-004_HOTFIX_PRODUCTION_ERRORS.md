# WO-004 Production Hotfix - Critical Errors

**Date:** 2025-11-17  
**Status:** 🚨 IN PROGRESS  
**Priority:** CRITICAL

---

## Summary

Three critical issues discovered in production after WO-004 deployment:

1. ✅ **FIXED:** AttributeError in domain_extraction_scheduler
2. ⚠️ **INVESTIGATING:** Database enum mismatch for "Not_a_Fit"
3. ⚠️ **TO FIX:** N+1 query performance issue

---

## Error 1: AttributeError - LocalBusiness.website ✅ FIXED

### The Error
```
AttributeError: 'LocalBusiness' object has no attribute 'website'
Source: src.services.domain_extraction_scheduler line 65
```

### Root Cause
The NEW domain_extraction_scheduler (deployed in WO-004) was logging `business.website`, but the LocalBusiness model uses `website_url` as the column name.

### The Fix
**File:** `src/services/domain_extraction_scheduler.py`  
**Line:** 65  
**Change:** `business.website` → `business.website_url`

**Commit:** `697279d`  
**Status:** ✅ DEPLOYED

### Impact
- WF3 (Domain Extraction) scheduler was failing on ALL items
- No domains were being extracted
- Queue was backing up

### Verification
```bash
# Check Render.com logs for:
"Processing domain extraction for LocalBusiness <uuid> (website=https://...)"
# Should now work without AttributeError
```

---

## Error 2: Database Enum Mismatch - "Not_a_Fit" ⚠️ INVESTIGATING

### The Error
```
invalid input value for enum sitemap_import_curation_status: "Not_a_Fit"
Source: src.routers.local_businesses
Endpoint: PUT /api/v3/local-businesses/status
```

### Root Cause Analysis

**Python Enum Definition** (place.py line 36):
```python
class PlaceStatusEnum(enum.Enum):
    Not_a_Fit = "Not a Fit"  # VALUE has space
```

**Database Enum:**
```sql
-- Check actual database values
SELECT enumlabel 
FROM pg_enum 
WHERE enumtypid = 'sitemap_import_curation_status'::regtype;
```

**Expected values:**
- New
- Selected
- Maybe
- Not a Fit  ← (with space)
- Archived

### The Problem

SQLAlchemy is trying to write `"Not_a_Fit"` (the enum MEMBER NAME) instead of `"Not a Fit"` (the enum VALUE) to the database.

This suggests one of two issues:
1. The database enum actually has `"Not_a_Fit"` (with underscore) and our Python code is wrong
2. SQLAlchemy is misconfigured and sending the name instead of the value

### Investigation Steps

**Step 1: Check Database Enum Values**
```sql
-- Connect to Supabase and run:
SELECT enumlabel 
FROM pg_enum 
WHERE enumtypid = 'sitemap_import_curation_status'::regtype
ORDER BY enumsortorder;
```

**Step 2: Check Existing Data**
```sql
-- See what values are actually in the database
SELECT DISTINCT status 
FROM local_businesses 
ORDER BY status;
```

**Step 3: Test Enum Assignment**
```python
# In Python console:
from src.models.place import PlaceStatusEnum
member = PlaceStatusEnum.Not_a_Fit
print(f"Name: {member.name}")    # Should be: Not_a_Fit
print(f"Value: {member.value}")  # Should be: Not a Fit
```

### Possible Fixes

**Option A: Database has underscore (Python code is wrong)**
```python
# Change place.py line 36:
Not_a_Fit = "Not_a_Fit"  # Match database exactly
```

**Option B: Database has space (SQLAlchemy misconfigured)**
```python
# Check local_business.py lines 107-117
# Ensure native_enum=True and create_type=False
# This should make SQLAlchemy use the VALUE, not the NAME
```

**Option C: Database needs migration**
```sql
-- If database has wrong value, fix it:
ALTER TYPE sitemap_import_curation_status RENAME VALUE 'Not_a_Fit' TO 'Not a Fit';
```

### Temporary Workaround

Until fixed, users cannot set status to "Not a Fit" via the API. They can use:
- New
- Selected
- Maybe
- Archived

### Status
⚠️ **NEEDS DATABASE VERIFICATION**

**Action Required:**
1. Check database enum values
2. Determine which is correct (space vs underscore)
3. Apply appropriate fix
4. Test thoroughly
5. Deploy hotfix

---

## Error 3: N+1 Query Performance Issue ⚠️ TO FIX

### The Symptom
```
Logs spammed with many identical:
DEBUG - Executing LocalBusiness query: SELECT local_businesses.id, ...
```

### Root Cause
N+1 query problem - code is looping through items and fetching one LocalBusiness at a time from the database.

### Where It's Happening

**Likely locations:**
1. `src.routers.local_businesses` - GET endpoint with filters
2. `src.common.curation_sdk.scheduler_loop` - Processing loop

### Investigation

**Check scheduler_loop.py:**
The main loop (lines 67-115) looks good - it fetches IDs in bulk:
```python
stmt = select(model.id).where(...).limit(batch_size)
# Then bulk updates
update_stmt = update(model).where(model.id.in_(items_to_process_ids))
```

**But individual processing might have N+1:**
Each item is processed separately, which might trigger additional queries.

### The Fix

**For GET endpoint:**
```python
# BEFORE (N+1):
for business_id in business_ids:
    business = await session.get(LocalBusiness, business_id)
    # Process business

# AFTER (Batch):
stmt = select(LocalBusiness).where(LocalBusiness.id.in_(business_ids))
result = await session.execute(stmt)
businesses = result.scalars().all()
for business in businesses:
    # Process business
```

**For Related Data:**
```python
# Use eager loading
from sqlalchemy.orm import selectinload, joinedload

stmt = select(LocalBusiness).options(
    selectinload(LocalBusiness.related_field)
).where(...)
```

### Performance Impact

**Current:**
- 1 query to get IDs
- N queries to get each business (N = batch size, typically 10-20)
- Total: 11-21 queries per cycle

**After Fix:**
- 1 query to get IDs
- 1 query to get all businesses
- Total: 2 queries per cycle

**Improvement:** 5-10x faster

### Status
⚠️ **NEEDS CODE REVIEW**

**Action Required:**
1. Identify exact location of N+1 queries
2. Refactor to use batch queries
3. Add eager loading for related data
4. Test performance improvement
5. Deploy hotfix

---

## Deployment Plan

### Hotfix #1: AttributeError ✅ COMPLETE
- **Commit:** `697279d`
- **Deployed:** 2025-11-17
- **Status:** Live in production

### Hotfix #2: Enum Mismatch ⏳ PENDING
- **Status:** Investigating
- **Blocker:** Need database verification
- **ETA:** TBD

### Hotfix #3: N+1 Queries ⏳ PENDING
- **Status:** Needs code review
- **Blocker:** Need to identify exact location
- **ETA:** TBD

---

## Monitoring

### What to Watch

**After Hotfix #1:**
- ✅ Domain extraction scheduler should process successfully
- ✅ No more AttributeError in logs
- ✅ Domains being created

**After Hotfix #2:**
- ✅ Users can set status to "Not a Fit"
- ✅ No more enum errors
- ✅ Status updates work correctly

**After Hotfix #3:**
- ✅ Fewer database queries in logs
- ✅ Faster response times
- ✅ Lower database load

### Verification Queries

**Check WF3 is working:**
```sql
SELECT 
    domain_extraction_status,
    COUNT(*) as count
FROM local_businesses
WHERE updated_at > NOW() - INTERVAL '1 hour'
GROUP BY domain_extraction_status;
```

**Check status updates:**
```sql
SELECT 
    status,
    COUNT(*) as count
FROM local_businesses
GROUP BY status;
```

**Check for "Not a Fit" records:**
```sql
SELECT COUNT(*) 
FROM local_businesses 
WHERE status = 'Not a Fit';
-- OR
WHERE status = 'Not_a_Fit';
-- (depending on which is correct)
```

---

## Lessons Learned

### What Went Wrong

1. **Insufficient Test Data**
   - Local testing didn't catch the `.website` typo because we had no real data
   - Need better test fixtures with realistic data

2. **Enum Mismatch Not Caught**
   - Database enum values vs Python enum values weren't verified
   - Need automated tests that verify enum consistency

3. **Performance Not Tested**
   - N+1 queries not caught in local testing
   - Need performance benchmarks and query logging in tests

### Improvements Needed

1. **Better Test Data**
   - Create fixtures with realistic LocalBusiness records
   - Include all enum values in test data
   - Test with batch sizes similar to production

2. **Enum Validation**
   - Add test that queries database enums and compares to Python enums
   - Fail if mismatch detected
   - Run in CI/CD pipeline

3. **Performance Testing**
   - Add query counting in tests
   - Fail if N+1 detected
   - Benchmark critical endpoints

4. **Staging Environment**
   - Deploy to staging first
   - Run with production-like data
   - Monitor for 24 hours before production

---

## Next Steps

### Immediate (Now)

1. ✅ Deploy Hotfix #1 (AttributeError) - DONE
2. ⏳ Investigate Hotfix #2 (Enum mismatch)
   - Query database for actual enum values
   - Determine correct fix
   - Test thoroughly
   - Deploy

3. ⏳ Investigate Hotfix #3 (N+1 queries)
   - Profile query patterns
   - Identify exact locations
   - Implement batch queries
   - Test performance
   - Deploy

### Short-term (This Week)

1. Add comprehensive test fixtures
2. Add enum validation tests
3. Add performance tests
4. Update deployment process to include staging

### Long-term (Next Sprint)

1. Implement automated performance monitoring
2. Add query logging and analysis
3. Create staging environment with production data
4. Improve test coverage for schedulers

---

**Document Status:** ACTIVE  
**Last Updated:** 2025-11-17  
**Next Review:** After each hotfix deployment

**END OF HOTFIX DOCUMENTATION**
