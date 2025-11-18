# WO-004 Production Deployment Monitoring Guide
# Real-Time Deployment Tracking

**Deployment Date:** 2025-11-17  
**Commit:** `09dadc4` (Merge WO-004)  
**Status:** 🚀 DEPLOYED TO PRODUCTION

---

## Deployment Timeline

### ✅ Phase 1: Code Push (COMPLETE)
- **Time:** 2025-11-17 07:29 UTC
- **Action:** Pushed to main branch
- **Commit:** `09dadc4`
- **Trigger:** Render.com auto-deploy initiated

### 🔄 Phase 2: Render.com Build (IN PROGRESS)
**Expected Duration:** 2-5 minutes

**What to Watch:**
1. Go to: https://dashboard.render.com
2. Find service: `scrapersky-backend`
3. Watch for new deployment starting

**Expected Logs:**
```
==> Cloning from https://github.com/hgroman/scrapersky-backend...
==> Checking out commit 09dadc4...
==> Building Docker image...
==> Running docker build...
```

### ⏳ Phase 3: Application Startup (NEXT)
**Expected Duration:** 10-30 seconds

**Critical Logs to Watch:**
```
INFO: Started server process
INFO: Waiting for application startup
INFO: Starting up the ScraperSky API - Lifespan Start
INFO: Scheduler started
INFO: Shared APScheduler started
INFO: Adding jobs to the shared scheduler...
```

### 🎯 Phase 4: Scheduler Registration (CRITICAL)
**What to Verify:**

**Look for these 6 scheduler registrations:**

1. **Domain Scheduler (WF4):**
   ```
   Setting up Domain scheduler job (Interval: 1m, Batch: 50, Max Instances: 3)
   Added job "Process Pending Domains" to job store "default"
   ```

2. **Deep Scan Scheduler (WF2) - NEW:**
   ```
   Setting up deep scan scheduler (interval=5m, batch=10, max_instances=1)
   Added job "WF2 - Deep Scan Queue Processor" to job store "default"
   Deep scan scheduler job 'process_deep_scan_queue' added to shared scheduler
   ```

3. **Domain Extraction Scheduler (WF3) - NEW:**
   ```
   Setting up domain extraction scheduler (interval=2m, batch=20, max_instances=1)
   Added job "WF3 - Domain Extraction Queue Processor" to job store "default"
   Domain extraction scheduler job 'process_domain_extraction_queue' added
   ```

4. **Domain Sitemap Submission Scheduler:**
   ```
   Setting up domain sitemap submission scheduler (runs every 1 minute)
   Added job "Domain Sitemap Submission Scheduler" to job store "default"
   ```

5. **Sitemap Import Scheduler (WF6):**
   ```
   Setting up scheduler job: process_sitemap_imports
   Added job "Process Pending Sitemap Imports" to job store "default"
   ```

6. **Page Curation Scheduler (WF7):**
   ```
   Added job "process_page_curation_queue" to job store "default"
   Page curation scheduler job added
   ```

### ✅ Phase 5: Health Check (VERIFICATION)
**Expected:** `Application startup complete`

**Test Command:**
```bash
curl https://your-render-url.onrender.com/health
```

**Expected Response:**
```json
{"status":"ok"}
```

---

## Critical Success Indicators

### Immediate (First 5 Minutes)

**✅ MUST SEE:**
- [ ] Build completes successfully
- [ ] Application starts without errors
- [ ] All 6 schedulers register
- [ ] Health endpoint returns 200 OK
- [ ] No error logs

**🚨 RED FLAGS:**
- ❌ Build fails
- ❌ Import errors
- ❌ Configuration errors
- ❌ Missing scheduler registrations
- ❌ Database connection errors

### First Hour

**✅ MONITOR:**
- [ ] WF2 scheduler runs (every 5 minutes)
- [ ] WF3 scheduler runs (every 2 minutes)
- [ ] No duplicate processing
- [ ] Error rates normal
- [ ] No crashes or restarts

**Check Logs For:**
```
Starting deep scan queue processing cycle
SCHEDULER_LOOP: Found X Place items with status Queued
Processing deep scan for Place <uuid>
Finished deep scan queue processing cycle

Starting domain extraction queue processing cycle
SCHEDULER_LOOP: Found X LocalBusiness items with status Queued
Processing domain extraction for LocalBusiness <uuid>
Finished domain extraction queue processing cycle
```

### First 24 Hours

**✅ VALIDATE:**
- [ ] Queue depths stable or decreasing
- [ ] Success rate >= 90%
- [ ] No race conditions observed
- [ ] Throughput >= baseline
- [ ] System metrics normal

---

## Database Monitoring

### Check WF2 (Deep Scans)

```sql
-- Check processing status
SELECT 
    deep_scan_status,
    COUNT(*) as count
FROM place
GROUP BY deep_scan_status
ORDER BY count DESC;

-- Check recent activity
SELECT 
    id,
    place_id,
    deep_scan_status,
    updated_at
FROM place
WHERE updated_at > NOW() - INTERVAL '1 hour'
ORDER BY updated_at DESC
LIMIT 20;

-- Check for duplicates (should be 0)
SELECT 
    place_id,
    COUNT(*) as duplicate_count
FROM local_business
GROUP BY place_id
HAVING COUNT(*) > 1;
```

### Check WF3 (Domain Extraction)

```sql
-- Check processing status
SELECT 
    domain_extraction_status,
    COUNT(*) as count
FROM local_business
GROUP BY domain_extraction_status
ORDER BY count DESC;

-- Check recent activity
SELECT 
    id,
    name,
    website,
    domain_extraction_status,
    updated_at
FROM local_business
WHERE updated_at > NOW() - INTERVAL '1 hour'
ORDER BY updated_at DESC
LIMIT 20;

-- Check domains created
SELECT 
    COUNT(*) as domains_created_last_hour
FROM domain
WHERE created_at > NOW() - INTERVAL '1 hour';
```

---

## Troubleshooting Guide

### Issue: Scheduler Not Registering

**Symptoms:**
- Missing "Added job" log
- Scheduler not in job store

**Check:**
1. Environment variables set correctly
2. No import errors
3. Configuration loaded

**Fix:**
```bash
# Check Render.com environment variables
DEEP_SCAN_SCHEDULER_INTERVAL_MINUTES=5
DEEP_SCAN_SCHEDULER_BATCH_SIZE=10
DEEP_SCAN_SCHEDULER_MAX_INSTANCES=1

DOMAIN_EXTRACTION_SCHEDULER_INTERVAL_MINUTES=2
DOMAIN_EXTRACTION_SCHEDULER_BATCH_SIZE=20
DOMAIN_EXTRACTION_SCHEDULER_MAX_INSTANCES=1
```

### Issue: Race Conditions Detected

**Symptoms:**
- Duplicate LocalBusiness records
- Same Place processed multiple times
- Duplicate API calls

**Verify:**
```sql
-- Check for duplicate processing
SELECT 
    place_id,
    COUNT(*) as process_count
FROM local_business
GROUP BY place_id
HAVING COUNT(*) > 1;
```

**Fix:**
- Verify `.with_for_update(skip_locked=True)` is in scheduler_loop.py line 72
- Check only one instance of each scheduler is running

### Issue: High Error Rate

**Symptoms:**
- Many records in Error/Failed status
- Error logs increasing

**Check:**
1. Database connectivity
2. Google Maps API key valid
3. API rate limits
4. Network issues

**Query:**
```sql
-- Check error details
SELECT 
    deep_scan_error,
    COUNT(*) as error_count
FROM place
WHERE deep_scan_status = 'Error'
GROUP BY deep_scan_error
ORDER BY error_count DESC;
```

### Issue: Application Crash

**Symptoms:**
- Container restarts
- 503 errors
- Health check fails

**Immediate Action:**
1. Check Render.com logs for stack trace
2. Verify database connection
3. Check memory/CPU usage
4. Consider rollback if critical

**Rollback Command:**
```bash
# On Render.com dashboard:
# 1. Go to service
# 2. Click "Rollback"
# 3. Select previous deployment (e9ac60d)
```

---

## Success Metrics

### Performance Targets

**Throughput:**
- WF2: 10-20 deep scans per 5-minute cycle
- WF3: 20-40 domain extractions per 2-minute cycle
- Combined: ~30 items/minute

**Success Rate:**
- Target: >= 90% success rate
- Acceptable: >= 80% success rate
- Critical: < 80% requires investigation

**Response Time:**
- Deep scan: 2-5 seconds per item
- Domain extraction: 1-2 seconds per item

**Queue Depth:**
- Should decrease over time
- If increasing: Check for bottlenecks

### System Health

**CPU Usage:**
- Normal: 20-40%
- High: 60-80%
- Critical: > 80%

**Memory Usage:**
- Normal: < 1GB
- High: 1-2GB
- Critical: > 2GB

**Database Connections:**
- Normal: 5-15 active
- High: 20-30 active
- Critical: > 30 active

---

## Rollback Plan

### When to Rollback

**IMMEDIATE ROLLBACK if:**
- ❌ Application won't start
- ❌ Critical errors in logs
- ❌ Data corruption detected
- ❌ Race conditions causing duplicates
- ❌ System instability

### How to Rollback

**Option 1: Render.com Dashboard (FASTEST)**
1. Go to https://dashboard.render.com
2. Select `scrapersky-backend` service
3. Click "Rollback" button
4. Select previous deployment: `e9ac60d`
5. Confirm rollback

**Option 2: Git Revert**
```bash
git revert 09dadc4
git push origin main
# Render.com auto-deploys previous version
```

**Option 3: Re-enable Old Scheduler**
```bash
# Edit src/main.py
# Uncomment lines 111-114:
try:
    setup_sitemap_scheduler()
except Exception as e:
    logger.error(f"Failed to setup Sitemap scheduler job: {e}", exc_info=True)

# Comment out lines 100-108:
# setup_deep_scan_scheduler()
# setup_domain_extraction_scheduler()

git commit -am "rollback: re-enable old sitemap_scheduler"
git push origin main
```

---

## Communication Plan

### Stakeholders to Notify

**Immediate (if issues):**
- Development team
- Operations team
- Product owner

**Daily (first week):**
- Status update email
- Metrics summary
- Any issues encountered

### Status Update Template

```
WO-004 Deployment Status - Day X

Deployment: STABLE / ISSUES / CRITICAL
Uptime: XX hours
Schedulers: 6/6 active

Metrics:
- WF2 processed: XXX items
- WF3 processed: XXX items
- Success rate: XX%
- Error rate: XX%

Issues:
- [None / List issues]

Actions:
- [None / List actions taken]

Next check: [Time]
```

---

## Next Steps

### Immediate (Now)

1. ✅ Watch Render.com deployment logs
2. ✅ Verify all 6 schedulers register
3. ✅ Test health endpoint
4. ✅ Monitor first scheduler cycles

### First Hour

1. ⏳ Watch for WF2 first run (5 minutes)
2. ⏳ Watch for WF3 first run (2 minutes)
3. ⏳ Check database for processed records
4. ⏳ Verify no errors in logs

### First Day

1. ⏳ Monitor queue depths
2. ⏳ Check success rates
3. ⏳ Verify no race conditions
4. ⏳ Review system metrics

### First Week

1. ⏳ Daily metrics review
2. ⏳ Performance comparison to baseline
3. ⏳ Identify optimization opportunities
4. ⏳ Plan cleanup phase (remove old scheduler)

---

## Cleanup Phase (After 1 Week Success)

**If deployment successful for 1 week:**

1. Remove old scheduler file:
   ```bash
   git rm src/services/sitemap_scheduler.py
   ```

2. Remove commented code from main.py:
   ```python
   # Delete lines 110-114 (commented sitemap_scheduler setup)
   ```

3. Remove deprecated settings:
   ```python
   # From settings.py, remove:
   # SITEMAP_SCHEDULER_INTERVAL_MINUTES
   # SITEMAP_SCHEDULER_BATCH_SIZE
   # SITEMAP_SCHEDULER_MAX_INSTANCES
   ```

4. Update documentation:
   - Mark WO-004 as COMPLETE
   - Update architecture diagrams
   - Archive old scheduler docs

5. Commit cleanup:
   ```bash
   git commit -am "cleanup: remove deprecated sitemap_scheduler after successful WO-004 deployment"
   git push origin main
   ```

---

## Contact Information

**For Issues:**
- Check Render.com logs first
- Review this monitoring guide
- Check database queries
- Contact development team if needed

**For Rollback:**
- Follow rollback plan above
- Document reason for rollback
- Plan fix and re-deployment

---

**Document Status:** ACTIVE  
**Last Updated:** 2025-11-17 07:29 UTC  
**Deployment Status:** 🚀 IN PROGRESS  
**Next Review:** 1 hour after deployment

**END OF DEPLOYMENT MONITORING GUIDE**
