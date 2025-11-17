# WF4→WF5→WF7 Identified Gaps & Improvements
**Part of:** Complete Pipeline Documentation  
**Last Updated:** November 17, 2025  
**Priority:** HIGH - Address before scaling

---

## Critical Issues (P0 - Fix Immediately)

### 1. Sitemap Files Not Auto-Queued
**Status:** 🔴 BROKEN  
**Impact:** HIGH - Sitemaps discovered but not processed

**Problem:**
- `sitemap_files` created with `sitemap_import_status = NULL`
- No automatic transition to 'Queued'
- Requires manual intervention in GUI

**Evidence:**
```sql
-- Query from Nov 17, 2025 testing
SELECT url, sitemap_import_status
FROM sitemap_files
WHERE domain_id = (SELECT id FROM domains WHERE domain = 'jenkinseyecare.com');

-- Results: 8 sitemaps, only 1 has status='Complete', rest are NULL
```

**Root Cause:**
- SitemapProcessingService creates records without setting status
- No trigger or default value on table
- No post-creation hook to queue

**Solution Options:**

**Option A: Auto-queue on creation (Recommended)**
```python
# In SitemapProcessingService.process_domain_with_own_session()
sitemap_file = SitemapFile(
    url=sitemap_url,
    domain_id=domain_id,
    sitemap_import_status=SitemapImportProcessStatusEnum.Queued  # ADD THIS
)
```

**Option B: Database trigger**
```sql
CREATE OR REPLACE FUNCTION auto_queue_sitemap()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.sitemap_import_status IS NULL THEN
        NEW.sitemap_import_status := 'Queued';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER sitemap_auto_queue
BEFORE INSERT ON sitemap_files
FOR EACH ROW
EXECUTE FUNCTION auto_queue_sitemap();
```

**Option C: Background job**
```python
# New scheduler job
async def queue_unprocessed_sitemaps():
    """Find sitemap_files with NULL status and queue them"""
    await session.execute(
        update(SitemapFile)
        .where(SitemapFile.sitemap_import_status == None)
        .values(sitemap_import_status='Queued')
    )
```

**Recommendation:** Option A (code fix) + Option C (safety net)

**Estimated Effort:** 2 hours  
**Assigned To:** TBD  
**Target Date:** Next sprint

---

### 2. Missing sitemap_curation_status Field
**Status:** 🟡 MISSING FEATURE  
**Impact:** MEDIUM - Inconsistent curation pattern

**Problem:**
- `domains` table has `sitemap_curation_status`
- `pages` table has `page_curation_status`
- `sitemap_files` table has NO curation status field
- Cannot track user decisions on sitemaps

**Evidence:**
```sql
-- This query fails
SELECT sitemap_curation_status FROM sitemap_files;
-- ERROR: column "sitemap_curation_status" does not exist
```

**Impact:**
- Cannot filter sitemaps by curation status in GUI
- Cannot implement "Select All" for sitemaps
- Inconsistent with WF4 and WF7 patterns

**Solution:**

**Step 1: Add column**
```sql
ALTER TABLE sitemap_files
ADD COLUMN sitemap_curation_status VARCHAR(50) DEFAULT 'New';

CREATE INDEX idx_sitemap_files_curation_status 
ON sitemap_files(sitemap_curation_status);
```

**Step 2: Update existing records**
```sql
UPDATE sitemap_files
SET sitemap_curation_status = 'New'
WHERE sitemap_curation_status IS NULL;
```

**Step 3: Add to router**
```python
# In WF5_V3_L3_1of1_SitemapRouter.py
@router.put("/status")
async def update_sitemap_curation_status_batch(...):
    # Similar to domains and pages routers
    # When status='Selected', set sitemap_import_status='Queued'
```

**Step 4: Update GUI**
- Add curation status filter
- Add batch update dropdown
- Add "Select All" button

**Estimated Effort:** 4 hours  
**Assigned To:** TBD  
**Target Date:** Next sprint

---

### 3. Job Table Cleanup
**Status:** 🟡 TECHNICAL DEBT  
**Impact:** LOW - Will accumulate over time

**Problem:**
- Jobs created for every domain processed
- No cleanup mechanism
- Will grow indefinitely

**Evidence:**
```sql
SELECT COUNT(*) FROM jobs WHERE job_type = 'sitemap';
-- Likely thousands of old completed jobs
```

**Solution Options:**

**Option A: TTL Policy**
```sql
-- Delete jobs older than 30 days
DELETE FROM jobs
WHERE created_at < NOW() - INTERVAL '30 days'
  AND status IN ('complete', 'failed');
```

**Option B: Scheduled Cleanup Job**
```python
async def cleanup_old_jobs():
    """Delete completed/failed jobs older than 30 days"""
    cutoff = datetime.utcnow() - timedelta(days=30)
    await session.execute(
        delete(Job)
        .where(Job.created_at < cutoff)
        .where(Job.status.in_(['complete', 'failed']))
    )
```

**Option C: Partition Table**
```sql
-- Partition by month for easier cleanup
CREATE TABLE jobs_2025_11 PARTITION OF jobs
FOR VALUES FROM ('2025-11-01') TO ('2025-12-01');
```

**Recommendation:** Option B (scheduled cleanup)

**Estimated Effort:** 2 hours  
**Assigned To:** TBD  
**Target Date:** Q1 2026

---

## High Priority Issues (P1 - Fix This Sprint)

### 4. No Monitoring for Stuck Jobs
**Status:** 🟡 MISSING FEATURE  
**Impact:** MEDIUM - Silent failures

**Problem:**
- Jobs can get stuck in 'pending' or 'running' state
- No alerts or monitoring
- Discovered issues only through manual inspection

**Solution:**

**Monitoring Query:**
```sql
-- Jobs stuck in pending > 5 minutes
SELECT job_id, job_type, created_at, status
FROM jobs
WHERE status = 'pending'
  AND created_at < NOW() - INTERVAL '5 minutes';

-- Jobs stuck in running > 30 minutes
SELECT job_id, job_type, created_at, status
FROM jobs
WHERE status = 'running'
  AND updated_at < NOW() - INTERVAL '30 minutes';
```

**Alert System:**
```python
async def check_stuck_jobs():
    """Alert on jobs stuck in pending/running"""
    stuck_pending = await session.execute(
        select(Job)
        .where(Job.status == 'pending')
        .where(Job.created_at < datetime.utcnow() - timedelta(minutes=5))
    )
    
    if stuck_pending.scalars().all():
        # Send alert (Slack, email, etc.)
        logger.error(f"Found {len(stuck_pending)} stuck pending jobs")
```

**Dashboard Metrics:**
- Jobs created (last hour)
- Jobs completed (last hour)
- Jobs failed (last hour)
- Jobs stuck (current)
- Average processing time

**Estimated Effort:** 4 hours  
**Assigned To:** TBD  
**Target Date:** This sprint

---

### 5. Incomplete Error Handling in Schedulers
**Status:** 🟡 INCONSISTENT  
**Impact:** MEDIUM - Some errors not logged properly

**Problem:**
- Some schedulers catch and log errors
- Others let exceptions propagate
- Inconsistent error reporting

**Solution:**

**Standard Error Handling Pattern:**
```python
async def process_queue():
    """Standard scheduler pattern with error handling"""
    try:
        await run_job_loop(
            model=Model,
            status_enum=StatusEnum,
            queued_status=StatusEnum.Queued,
            processing_status=StatusEnum.Processing,
            completed_status=StatusEnum.Complete,
            failed_status=StatusEnum.Error,
            processing_function=service.process_single_item,
            batch_size=settings.BATCH_SIZE,
            order_by_column=asc(Model.updated_at),
            status_field_name="status_field",
            error_field_name="error_field",
        )
    except Exception as e:
        logger.exception(f"Critical error in scheduler: {e}")
        # Send alert
        # Don't re-raise - let scheduler continue
```

**Apply to all schedulers:**
- domain_sitemap_submission_scheduler.py
- sitemap_import_scheduler.py
- WF7_V2_L4_2of2_PageCurationScheduler.py

**Estimated Effort:** 2 hours  
**Assigned To:** TBD  
**Target Date:** This sprint

---

## Medium Priority Issues (P2 - Fix Next Sprint)

### 6. Missing Indexes for Common Queries
**Status:** 🟡 PERFORMANCE  
**Impact:** MEDIUM - Slow queries on large datasets

**Problem:**
- Some common filter combinations lack composite indexes
- GUI queries may be slow with large datasets

**Solution:**

**Add composite indexes:**
```sql
-- Domains: Common filter combination
CREATE INDEX idx_domains_curation_analysis 
ON domains(sitemap_curation_status, sitemap_analysis_status);

-- Pages: Common filter combination
CREATE INDEX idx_pages_curation_processing 
ON pages(page_curation_status, page_processing_status);

-- Pages: URL search (trigram for LIKE queries)
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE INDEX idx_pages_url_trgm 
ON pages USING gin(url gin_trgm_ops);

-- SitemapFiles: Domain + status
CREATE INDEX idx_sitemap_files_domain_status 
ON sitemap_files(domain_id, sitemap_import_status);
```

**Estimated Effort:** 1 hour  
**Assigned To:** TBD  
**Target Date:** Next sprint

---

### 7. No Bulk Operations for Large Datasets
**Status:** 🟡 MISSING FEATURE  
**Impact:** MEDIUM - Manual work for large selections

**Problem:**
- "Select All" works but processes one-by-one
- No true bulk operations for 1000+ records
- GUI may timeout on large updates

**Solution:**

**Batch Update Endpoint:**
```python
@router.put("/bulk-update")
async def bulk_update_pages(
    request: BulkUpdateRequest,
    session: AsyncSession = Depends(get_db_session)
):
    """Update pages in batches to avoid timeout"""
    batch_size = 100
    total_updated = 0
    
    # Process in batches
    for i in range(0, len(request.page_ids), batch_size):
        batch = request.page_ids[i:i+batch_size]
        result = await session.execute(
            update(Page)
            .where(Page.id.in_(batch))
            .values(page_curation_status=request.status)
        )
        total_updated += result.rowcount
        await session.commit()
    
    return {"updated_count": total_updated}
```

**Estimated Effort:** 3 hours  
**Assigned To:** TBD  
**Target Date:** Next sprint

---

### 8. No Retry Logic for Failed Jobs
**Status:** 🟡 MISSING FEATURE  
**Impact:** MEDIUM - Transient failures not recovered

**Problem:**
- Jobs fail due to transient errors (network, API limits)
- No automatic retry
- Requires manual requeue

**Solution:**

**Add retry fields to jobs table:**
```sql
ALTER TABLE jobs
ADD COLUMN retry_count INTEGER DEFAULT 0,
ADD COLUMN max_retries INTEGER DEFAULT 3,
ADD COLUMN next_retry_at TIMESTAMP WITH TIME ZONE;
```

**Retry Logic:**
```python
async def process_with_retry(job: Job):
    """Process job with exponential backoff retry"""
    try:
        await process_job(job)
        job.status = 'complete'
    except Exception as e:
        job.retry_count += 1
        
        if job.retry_count < job.max_retries:
            # Exponential backoff: 1min, 2min, 4min
            delay = 2 ** job.retry_count
            job.next_retry_at = datetime.utcnow() + timedelta(minutes=delay)
            job.status = 'pending'
        else:
            job.status = 'failed'
            job.error = str(e)
```

**Estimated Effort:** 4 hours  
**Assigned To:** TBD  
**Target Date:** Next sprint

---

## Low Priority Issues (P3 - Nice to Have)

### 9. No Progress Tracking for Long Jobs
**Status:** 🟡 MISSING FEATURE  
**Impact:** LOW - User experience

**Problem:**
- Long-running jobs show no progress
- User doesn't know if job is stuck or processing

**Solution:**

**Add progress field:**
```sql
ALTER TABLE jobs
ADD COLUMN progress_percent INTEGER DEFAULT 0,
ADD COLUMN progress_message TEXT;
```

**Update during processing:**
```python
async def process_sitemap(job_id, domain):
    total_paths = len(SITEMAP_PATHS)
    
    for i, path in enumerate(SITEMAP_PATHS):
        # Process path...
        
        # Update progress
        progress = int((i + 1) / total_paths * 100)
        await update_job_progress(job_id, progress, f"Checking {path}")
```

**Estimated Effort:** 3 hours  
**Assigned To:** TBD  
**Target Date:** Q1 2026

---

### 10. No Deduplication of Pages
**Status:** 🟡 MISSING FEATURE  
**Impact:** LOW - Duplicate processing

**Problem:**
- Same URL can appear in multiple sitemaps
- Creates duplicate Page records
- Wastes ScraperAPI credits

**Solution:**

**Add unique constraint:**
```sql
-- Option A: Strict uniqueness
CREATE UNIQUE INDEX idx_pages_url_unique ON pages(url);

-- Option B: Unique per sitemap_file (allows same URL in different sitemaps)
CREATE UNIQUE INDEX idx_pages_url_sitemap ON pages(url, sitemap_file_id);
```

**Deduplication logic:**
```python
async def create_page_if_not_exists(url, sitemap_file_id):
    """Only create if URL doesn't exist"""
    existing = await session.execute(
        select(Page).where(Page.url == url)
    )
    
    if existing.scalar_one_or_none():
        logger.info(f"Page already exists: {url}")
        return None
    
    return await create_page(url, sitemap_file_id)
```

**Estimated Effort:** 2 hours  
**Assigned To:** TBD  
**Target Date:** Q1 2026

---

## GUI Improvements Needed

### 11. Add Sitemap Curation Status Filter
**Status:** 🔴 MISSING (depends on #2)  
**Impact:** HIGH - Cannot filter sitemaps

**Current State:**
- Sitemap Curation (WF5) GUI exists
- No curation status filter
- No batch update capability

**Needed:**
1. Add `sitemap_curation_status` dropdown filter
2. Add batch update dropdown (New/Selected/Rejected)
3. Add "Select All Filtered" button
4. Display curation status in table

**Mockup:**
```
[Sitemap Curation (WF5)]

Filters:
  Domain: [_____________]
  Import Status: [All Statuses ▼]
  Curation Status: [All Statuses ▼]  ← ADD THIS
  
Batch Update:
  Status: [Selected ▼]  [Update Selected]  [Update ALL Filtered (X items)]
  
Table:
  ☐ URL                              | Domain      | Import Status | Curation Status | Created
  ☐ example.com/sitemap.xml          | example.com | Complete      | New            | 11/17/25
```

**Estimated Effort:** 2 hours (after #2 complete)  
**Assigned To:** TBD  
**Target Date:** Next sprint

---

### 12. Add Priority Level Filter to Pages
**Status:** 🟡 MISSING FEATURE  
**Impact:** MEDIUM - Cannot filter by priority

**Current State:**
- Pages have `priority_level` field (1, 2, 3)
- Not exposed in GUI filters

**Needed:**
1. Add priority level dropdown filter
2. Sort by priority by default
3. Color-code rows by priority

**Mockup:**
```
[Page Curation (WF7)]

Filters:
  URL: [_____________]
  Processing Status: [All Statuses ▼]
  Curation Status: [All Statuses ▼]
  Page Type: [All Types ▼]
  Priority: [All Priorities ▼]  ← ADD THIS
  
Table (color-coded):
  ☐ URL                    | Type         | Priority | Status   | Curation
  ☐ example.com/contact    | CONTACT_ROOT | 1 🔴     | Complete | Selected
  ☐ example.com/about      | unknown      | 3 🟢     | Complete | New
```

**Estimated Effort:** 2 hours  
**Assigned To:** TBD  
**Target Date:** Next sprint

---

### 13. Add "View Extracted Contacts" Modal
**Status:** 🟡 MISSING FEATURE  
**Impact:** MEDIUM - Cannot view results easily

**Current State:**
- Contacts stored in `scraped_content` JSONB
- No way to view in GUI
- Must query database directly

**Needed:**
1. Add "View Contacts" button for completed pages
2. Modal showing extracted data:
   - Emails
   - Phone numbers
   - Addresses
   - Extraction timestamp
3. Copy-to-clipboard buttons

**Mockup:**
```
[View Extracted Contacts - example.com/contact]

Emails (2):
  ☐ contact@example.com     [Copy]
  ☐ info@example.com        [Copy]
  
Phone Numbers (1):
  ☐ +1-555-0100            [Copy]
  
Addresses (0):
  (No addresses found)
  
Extracted: 11/17/2025 1:52 AM
ScraperAPI Credits Used: 1

[Close]
```

**Estimated Effort:** 3 hours  
**Assigned To:** TBD  
**Target Date:** Next sprint

---

## Architecture Improvements

### 14. Standardize Service Communication Pattern
**Status:** 🟡 INCONSISTENT  
**Impact:** MEDIUM - Maintenance burden

**Problem:**
- Some services use direct calls
- Some use HTTP (legacy)
- Inconsistent patterns

**Solution:**

**Document standard pattern:**
```python
# ✅ CORRECT: Direct service call
service = SomeService()
result = await service.process(item_id, session)

# ❌ WRONG: HTTP call
async with httpx.AsyncClient() as client:
    response = await client.post("http://localhost:8000/api/...")
```

**Audit all services:**
- Find remaining HTTP calls between services
- Refactor to direct calls
- Document in architecture guide

**Estimated Effort:** 4 hours  
**Assigned To:** TBD  
**Target Date:** Next sprint

---

### 15. Add Service Health Checks
**Status:** 🟡 MISSING FEATURE  
**Impact:** MEDIUM - Cannot verify system health

**Problem:**
- No health check endpoint
- Cannot verify schedulers running
- Cannot verify external dependencies

**Solution:**

**Health Check Endpoint:**
```python
@router.get("/health")
async def health_check():
    """Check system health"""
    return {
        "status": "healthy",
        "schedulers": {
            "domain_sitemap_submission": check_scheduler_running("process_pending_domain_sitemap_submissions"),
            "sitemap_import": check_scheduler_running("process_sitemap_imports"),
            "page_curation": check_scheduler_running("v2_page_curation_processor"),
        },
        "external_services": {
            "scraper_api": await check_scraper_api(),
            "database": await check_database(),
        },
        "queue_depths": {
            "domains_queued": await count_queued_domains(),
            "sitemaps_queued": await count_queued_sitemaps(),
            "pages_queued": await count_queued_pages(),
        }
    }
```

**Estimated Effort:** 3 hours  
**Assigned To:** TBD  
**Target Date:** This sprint

---

## Summary

### By Priority

**P0 (Critical - Fix Immediately):**
1. Sitemap files not auto-queued
2. Missing sitemap_curation_status field
3. Job table cleanup

**P1 (High - Fix This Sprint):**
4. No monitoring for stuck jobs
5. Incomplete error handling in schedulers

**P2 (Medium - Fix Next Sprint):**
6. Missing indexes for common queries
7. No bulk operations for large datasets
8. No retry logic for failed jobs

**P3 (Low - Nice to Have):**
9. No progress tracking for long jobs
10. No deduplication of pages

### By Category

**Database (5 issues):**
- #1 Auto-queue sitemaps
- #2 Add curation status field
- #3 Job cleanup
- #6 Add indexes
- #10 Deduplication

**Monitoring (2 issues):**
- #4 Stuck job alerts
- #15 Health checks

**Error Handling (2 issues):**
- #5 Standardize error handling
- #8 Retry logic

**GUI (3 issues):**
- #11 Sitemap curation filter
- #12 Priority level filter
- #13 View contacts modal

**Performance (2 issues):**
- #6 Indexes
- #7 Bulk operations

**Architecture (2 issues):**
- #14 Service communication pattern
- #15 Health checks

### Estimated Total Effort
- P0: 8 hours
- P1: 6 hours
- P2: 9 hours
- P3: 5 hours
- **Total: 28 hours (~3.5 days)**

### Recommended Sprint Plan

**Sprint 1 (This Week):**
- #1 Auto-queue sitemaps (2h)
- #2 Add curation status field (4h)
- #4 Stuck job monitoring (4h)
- #5 Error handling (2h)
- #15 Health checks (3h)
- **Total: 15 hours**

**Sprint 2 (Next Week):**
- #6 Add indexes (1h)
- #7 Bulk operations (3h)
- #8 Retry logic (4h)
- #11 Sitemap GUI (2h)
- #12 Priority filter (2h)
- #13 View contacts modal (3h)
- **Total: 15 hours**

**Sprint 3 (Future):**
- #3 Job cleanup (2h)
- #9 Progress tracking (3h)
- #10 Deduplication (2h)
- #14 Service pattern audit (4h)
- **Total: 11 hours**
