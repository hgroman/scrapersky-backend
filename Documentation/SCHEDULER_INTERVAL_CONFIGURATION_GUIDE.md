# SCHEDULER INTERVAL CONFIGURATION GUIDE
**Last Updated:** November 20, 2025  
**Commit:** f10ec73

---

## OVERVIEW

ScraperSky uses APScheduler to run 10 background services that process queued items. Each scheduler has a configurable interval that determines how frequently it checks for new work.

**All scheduler intervals are configured in:** `src/config/settings.py`

---

## CURRENT CONFIGURATION (All at 1 Minute)

### Workflow Schedulers

| Scheduler | Setting | Current | Purpose |
|-----------|---------|---------|---------|
| **WF2: Deep Scan** | `DEEP_SCAN_SCHEDULER_INTERVAL_MINUTES` | 1 | Google Maps API deep scan |
| **WF3: Domain Extraction** | `DOMAIN_EXTRACTION_SCHEDULER_INTERVAL_MINUTES` | 2 | Extract domains from businesses |
| **WF4: Domain Processing** | `DOMAIN_SCHEDULER_INTERVAL_MINUTES` | 1 | Domain metadata extraction |
| **WF5: Sitemap Submission** | `DOMAIN_SITEMAP_SCHEDULER_INTERVAL_MINUTES` | 1 | Sitemap discovery & analysis |
| **WF6: Sitemap Import** | `SITEMAP_IMPORT_SCHEDULER_INTERVAL_MINUTES` | 1 | Import URLs from sitemaps |
| **WF7: Page Curation** | `PAGE_CURATION_SCHEDULER_INTERVAL_MINUTES` | 1 | Extract contacts from pages |

### CRM Sync Schedulers

| Scheduler | Setting | Current | Purpose |
|-----------|---------|---------|---------|
| **Brevo Sync** | `BREVO_SYNC_SCHEDULER_INTERVAL_MINUTES` | 1 | Sync contacts to Brevo |
| **HubSpot Sync** | `HUBSPOT_SYNC_SCHEDULER_INTERVAL_MINUTES` | 1 | Sync contacts to HubSpot |
| **n8n Sync** | `N8N_SYNC_SCHEDULER_INTERVAL_MINUTES` | 1 | Send contacts to n8n webhook |
| **DeBounce Validation** | `DEBOUNCE_VALIDATION_SCHEDULER_INTERVAL_MINUTES` | 1 | Validate email addresses |

---

## DEVELOPMENT vs PRODUCTION

### Development (Current: All at 1 minute)
**Purpose:** Fast iteration and immediate feedback  
**Benefits:**
- See results within 1 minute of queueing items
- Rapid testing of workflow changes
- Quick debugging of processing issues

**Considerations:**
- Higher database load
- More frequent API calls
- Faster credit consumption for external APIs

### Production (Recommended: 5 minutes for external APIs)
**Purpose:** Balance responsiveness with resource efficiency  
**Benefits:**
- Reduced API rate limit pressure
- Lower database query frequency
- More efficient batch processing

**Recommended Production Values:**
```python
# External API schedulers (rate limit sensitive)
DEEP_SCAN_SCHEDULER_INTERVAL_MINUTES: int = 5
BREVO_SYNC_SCHEDULER_INTERVAL_MINUTES: int = 5
HUBSPOT_SYNC_SCHEDULER_INTERVAL_MINUTES: int = 5
DEBOUNCE_VALIDATION_SCHEDULER_INTERVAL_MINUTES: int = 5
N8N_SYNC_SCHEDULER_INTERVAL_MINUTES: int = 5

# Internal processing schedulers (can stay fast)
DOMAIN_SCHEDULER_INTERVAL_MINUTES: int = 1
DOMAIN_EXTRACTION_SCHEDULER_INTERVAL_MINUTES: int = 2
DOMAIN_SITEMAP_SCHEDULER_INTERVAL_MINUTES: int = 1
SITEMAP_IMPORT_SCHEDULER_INTERVAL_MINUTES: int = 1
PAGE_CURATION_SCHEDULER_INTERVAL_MINUTES: int = 1
```

---

## HOW TO CHANGE INTERVALS

### Step 1: Edit settings.py

**File:** `src/config/settings.py`

**Find the scheduler setting and change the value:**
```python
# Example: Change Brevo sync from 1 to 5 minutes
BREVO_SYNC_SCHEDULER_INTERVAL_MINUTES: int = 5
```

### Step 2: Commit and Push

```bash
git add src/config/settings.py
git commit -m "config: adjust scheduler intervals for [environment]"
git push origin main
```

### Step 3: Verify Deployment

**For Render.com:**
1. Push triggers automatic rebuild
2. Check Render dashboard for deployment status
3. Wait for "Live" status
4. Verify in logs: Look for scheduler setup messages

**For Local Development:**
1. Restart FastAPI server
2. Check startup logs for scheduler configuration
3. Verify intervals in log output

---

## SCHEDULER CONFIGURATION LOCATIONS

### Settings Definition
**File:** `src/config/settings.py`  
**Lines:** 47-183  
**Purpose:** Define interval values

### Scheduler Setup Files
Each scheduler reads from settings and configures APScheduler:

| Scheduler | Setup File | Setup Function |
|-----------|------------|----------------|
| Deep Scan | `src/services/deep_scan_scheduler.py` | `setup_deep_scan_scheduler()` |
| Domain Extraction | `src/services/domain_extraction_scheduler.py` | `setup_domain_extraction_scheduler()` |
| Domain Processing | `src/services/domain_scheduler.py` | `setup_domain_scheduler()` |
| Sitemap Submission | `src/services/domain_sitemap_submission_scheduler.py` | `setup_domain_sitemap_submission_scheduler()` |
| Sitemap Import | `src/services/sitemap_import_scheduler.py` | `setup_sitemap_import_scheduler()` |
| Page Curation | `src/services/WF7_V2_L4_2of2_PageCurationScheduler.py` | `setup_page_curation_scheduler()` |
| Brevo Sync | `src/services/crm/brevo_sync_scheduler.py` | `setup_brevo_sync_scheduler()` |
| HubSpot Sync | `src/services/crm/hubspot_sync_scheduler.py` | `setup_hubspot_sync_scheduler()` |
| n8n Sync | `src/services/crm/n8n_sync_scheduler.py` | `setup_n8n_sync_scheduler()` |
| DeBounce | `src/services/email_validation/debounce_scheduler.py` | `setup_debounce_validation_scheduler()` |

---

## VERIFYING SCHEDULER CONFIGURATION

### Check Startup Logs

When the server starts, each scheduler logs its configuration:

```
INFO: Setting up deep scan scheduler (interval=1m, batch=10, max_instances=1)
INFO: Setting up domain extraction scheduler (interval=2m, batch=20, max_instances=1)
INFO: Configuring Brevo sync scheduler...
INFO:    Interval: 1 minutes
INFO:    Batch size: 10 contacts
```

### Check APScheduler Jobs

```python
# In Python console or debug endpoint
from src.scheduler_instance import scheduler

# List all jobs
for job in scheduler.get_jobs():
    print(f"{job.name}: {job.trigger}")
```

### Monitor Execution Frequency

Check logs for job execution timestamps:
```
INFO: Starting domain extraction queue processing cycle
INFO: Finished domain extraction queue processing cycle
```

Calculate time between cycles to verify interval.

---

## TROUBLESHOOTING

### Scheduler Not Running at Expected Interval

**Check:**
1. Server was restarted after settings change
2. Settings file was committed and pushed
3. Deployment completed successfully
4. No errors in scheduler setup logs

### Scheduler Running Too Frequently

**Possible Causes:**
- Multiple server instances running
- `MAX_INSTANCES` set too high
- Interval set to 0 (runs continuously)

**Solution:**
- Check `MAX_INSTANCES` setting
- Verify only one server instance running
- Confirm interval is > 0

### Scheduler Not Processing Items

**Check:**
1. Items are actually queued (check database)
2. Status field matches queued status enum
3. No errors in processing function
4. Batch size not too small

---

## BATCH SIZE CONFIGURATION

**Also configurable in settings.py:**

| Setting | Current | Purpose |
|---------|---------|---------|
| `DEEP_SCAN_SCHEDULER_BATCH_SIZE` | 10 | Items per cycle |
| `DOMAIN_EXTRACTION_SCHEDULER_BATCH_SIZE` | 20 | Items per cycle |
| `DOMAIN_SCHEDULER_BATCH_SIZE` | 50 | Items per cycle |
| `SITEMAP_IMPORT_SCHEDULER_BATCH_SIZE` | 20 | Items per cycle |
| `PAGE_CURATION_SCHEDULER_BATCH_SIZE` | 10 | Items per cycle |
| `BREVO_SYNC_SCHEDULER_BATCH_SIZE` | 10 | Items per cycle |
| `HUBSPOT_SYNC_SCHEDULER_BATCH_SIZE` | 10 | Items per cycle |
| `DEBOUNCE_VALIDATION_SCHEDULER_BATCH_SIZE` | 50 | Items per cycle |
| `N8N_SYNC_SCHEDULER_BATCH_SIZE` | 10 | Items per cycle |

**Formula:** `Total items/hour = (60 / interval_minutes) * batch_size`

**Example:** 1-minute interval, 10 batch size = 600 items/hour

---

## ENVIRONMENT-SPECIFIC CONFIGURATION

### Using Environment Variables

Override settings via environment variables:

```bash
# .env file or Render environment variables
DEEP_SCAN_SCHEDULER_INTERVAL_MINUTES=5
BREVO_SYNC_SCHEDULER_INTERVAL_MINUTES=5
```

### Conditional Configuration

```python
# In settings.py
DEEP_SCAN_SCHEDULER_INTERVAL_MINUTES: int = (
    1 if environment == "development" else 5
)
```

---

## MAINTENANCE CHECKLIST

### When Adding New Scheduler

1. ✅ Add `*_INTERVAL_MINUTES` setting to `settings.py`
2. ✅ Add `*_BATCH_SIZE` setting to `settings.py`
3. ✅ Add `*_MAX_INSTANCES` setting to `settings.py`
4. ✅ Document in this guide
5. ✅ Add to monitoring/logging
6. ✅ Test with 1-minute interval first
7. ✅ Adjust for production if external API

### When Changing Intervals

1. ✅ Update `settings.py`
2. ✅ Update this guide if changing defaults
3. ✅ Commit with descriptive message
4. ✅ Push to trigger deployment
5. ✅ Verify in logs after deployment
6. ✅ Monitor for 10-15 minutes

### Regular Review

**Monthly:**
- Review scheduler execution logs
- Check for bottlenecks or delays
- Adjust intervals based on load
- Verify API rate limit compliance

---

## RELATED DOCUMENTATION

- **Enum Standardization:** `Documentation/ENUM_STANDARDIZATION_AUDIT_2025-11-20.md`
- **Database Schema:** `Documentation/DATABASE_ENUM_LIVE_REPORT_2025-11-20.md`
- **Workflow Chain:** See enum audit report Part 6

---

## COMMIT HISTORY

**Recent Changes:**
- `f10ec73` (2025-11-20) - Set all scheduler intervals to 1 minute for development
- Previous: Various intervals (1-5 minutes)

---

**END OF GUIDE**
