# WF4 Database Timeout Investigation - HANDOFF DOCUMENT

**Date:** 2025-07-31  
**Issue:** WF4 Domain Curation UI hangs when clicking "Update Selected" button  
**Status:** UNRESOLVED - Database transaction timeout identified but not fixed  
**Next Engineer:** Continue database connection investigation  

---

## PROBLEM SUMMARY

**User Issue:** When selecting domains in Domain Curation UI and clicking "Update 1 Selected", the interface hangs indefinitely. No feedback, no errors, just complete UI freeze.

**Expected Behavior:** 
1. User selects domain (e.g., pacificbattleship.com)
2. Sets status to "Selected" 
3. Clicks "Update 1 Selected"
4. Domain gets dual-status update:
   - `sitemap_curation_status` → 'Selected'
   - `sitemap_analysis_status` → 'queued'
5. UI shows success message
6. Domain appears in sitemap analysis queue

**Actual Behavior:** UI hangs, no database updates occur, complete silent failure.

---

## INVESTIGATION FINDINGS

### ✅ Code Architecture Analysis
- **3-phase session management fix IS properly implemented** in `domain_scheduler.py`
- **No connection timeout errors** in logs (the original emergency fix worked)
- **WF4→WF5 handoff logic is correct** in `/src/routers/domains.py` lines 229-236
- **Frontend JavaScript is properly implemented** in `/static/js/domain-curation-tab.js`

### ✅ Database State Verification
- **Domain exists:** `pacificbattleship.com` (ID: 6aa68436-110c-4fe4-83a1-6bcc81653149)
- **Current status:** `sitemap_curation_status = 'New'`, `sitemap_analysis_status = NULL`
- **16 pending domains** exist for domain_scheduler processing
- **0 queued domains** for sitemap analysis (expected - no one has clicked "Selected")

### ❌ Critical Issue Identified: DATABASE TRANSACTION TIMEOUT

**Root Cause:** The PUT endpoint `/api/v3/domains/sitemap-curation/status` is timing out at the database transaction level.

**Evidence:**
1. **Direct API test with curl:** Times out after 2+ minutes
2. **Manual database updates:** Timeout after 2 minutes  
3. **Container restart:** Doesn't fix the issue
4. **No router logging:** Endpoint function never executes (hangs before reaching code)

---

## ATTEMPTED SOLUTIONS

### 1. Verified 3-Phase Session Management ✅
- Code in `domain_scheduler.py` correctly implements:
  - Phase 1: Quick DB fetch and mark as processing
  - Phase 2: Slow metadata extraction WITHOUT DB connection
  - Phase 3: Quick DB update with results
- **Result:** This was already working, not the issue

### 2. Authentication Testing ✅
- Development token bypass confirmed working: `scraper_sky_2024`
- Environment set to `development` mode
- **Result:** Auth is not the issue

### 3. Database Connection Testing ❌
- All database operations hang/timeout
- Simple SELECT queries work fine via schedulers
- UPDATE operations on domains table appear to be problematic
- **Result:** Database transaction/locking issue identified

---

## CURRENT SYSTEM STATE

### Working Components:
- ✅ All schedulers running successfully (domain_scheduler, sitemap_scheduler, etc.)
- ✅ Domain discovery and metadata extraction (16 pending domains being processed)
- ✅ WF4→WF5 pipeline architecture (domain_sitemap_submission_scheduler correctly looks for queued domains)
- ✅ UI loads and displays domains correctly

### Broken Components:
- ❌ Domain curation status updates (the core WF4 user interaction)
- ❌ Any database UPDATE operations on domains table appear to hang
- ❌ Manual database transactions timeout

---

## FILES INVESTIGATED

### Router Code (Working - Code Logic Correct)
- `/src/routers/domains.py` - Lines 161-253 contain the dual-status update logic
- Endpoint: `PUT /api/v3/domains/sitemap-curation/status`
- Function: `update_domain_sitemap_curation_status_batch()`

### Frontend Code (Working - Sends Correct Requests)  
- `/static/js/domain-curation-tab.js` - Lines 393-413 contain the API call
- Properly constructs payload with domain_ids and target status
- Includes proper authentication headers

### Scheduler Code (Working - Recently Fixed)
- `/src/services/domain_scheduler.py` - 3-phase session management implemented
- `/src/services/domain_sitemap_submission_scheduler.py` - Correctly looks for queued domains

---

## DIAGNOSTIC COMMANDS USED

```bash
# Check domain status
docker compose exec scrapersky python -c "..."

# Test endpoint directly
curl -X PUT "http://localhost:8000/api/v3/domains/sitemap-curation/status" \
  -H "Authorization: Bearer scraper_sky_2024" \
  -d '{"domain_ids": ["6aa68436-110c-4fe4-83a1-6bcc81653149"], "sitemap_curation_status": "Selected"}'

# Check logs for errors
docker compose logs scrapersky --tail 200 | grep -E "(ERROR|timeout|lock)"

# Container restart attempt
docker compose restart scrapersky
```

---

## NEXT INVESTIGATION STEPS

### 1. Database Connection Pool Investigation
- Check Supavisor connection pooling configuration
- Investigate if connection pool is exhausted
- Look for long-running transactions or locks

### 2. Database Lock Analysis
- Check for table locks on `domains` table
- Investigate if migration or maintenance operation is blocking updates
- Query PostgreSQL system tables for lock information

### 3. Transaction Isolation Issues
- Check if there are deadlocks between different schedulers and the router
- Investigate transaction isolation levels
- Look for race conditions between background jobs and user updates

### 4. Supabase-Specific Issues
- Check Supabase dashboard for performance metrics
- Investigate if rate limits or quotas are being hit
- Check connection limits and pooling settings

---

## IMMEDIATE WORKAROUND OPTIONS

### Option 1: Direct Database Update
Create a temporary admin endpoint that bypasses the problematic transaction to manually queue domains for testing.

### Option 2: Scheduler-Based Update
Modify domain_scheduler to also handle curation status changes, removing the need for real-time user updates.

### Option 3: Queue-Based Architecture
Implement a job queue system where UI updates create jobs instead of direct database updates.

---

## ENVIRONMENT INFO

- **Docker Container:** `scraper-sky-backend-scrapersky-1`
- **Database:** Supabase PostgreSQL via Supavisor (port 6543)
- **Environment:** Development mode
- **Auth:** Development token bypass enabled
- **Container Status:** Healthy, all schedulers running

---

## CRITICAL DATA POINTS

- **Target Domain:** pacificbattleship.com (ID: 6aa68436-110c-4fe4-83a1-6bcc81653149)
- **Expected Transition:** sitemap_curation_status 'New' → 'Selected', sitemap_analysis_status NULL → 'queued'
- **Timeout Duration:** ~2 minutes for all database UPDATE operations
- **Error Pattern:** No exceptions thrown, just hangs indefinitely

---

**HANDOFF COMPLETE**  
**Recommendation:** Focus on database connection/transaction analysis before attempting code changes.