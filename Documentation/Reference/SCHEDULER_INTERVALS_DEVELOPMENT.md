# Scheduler Intervals - Development vs Production

**Date:** 2025-11-19  
**Status:** ✅ **CONFIGURED FOR DEVELOPMENT**

---

## Current Configuration (Development Mode)

All scheduler intervals have been set to **1 minute** for faster development and testing.

### Scheduler Settings in `.env`

```bash
# Brevo Sync Scheduler (Line 52)
BREVO_SYNC_SCHEDULER_INTERVAL_MINUTES=1  # Development: 1 min, Production: 5 min

# HubSpot Sync Scheduler (Line 67)
HUBSPOT_SYNC_SCHEDULER_INTERVAL_MINUTES=1  # Development: 1 min, Production: 5 min

# DeBounce Validation Scheduler (Line 90)
DEBOUNCE_VALIDATION_SCHEDULER_INTERVAL_MINUTES=1  # Development: 1 min, Production: 5 min
```

---

## Verification

**Check Docker logs to confirm:**
```bash
docker logs scraper-sky-backend-scrapersky-1 2>&1 | grep -A 3 "Configuring.*scheduler"
```

**Expected output:**
```
📋 Configuring Brevo sync scheduler...
   Interval: 1 minutes ✅
   Batch size: 10 contacts
   Max instances: 1

📋 Configuring HubSpot sync scheduler...
   Interval: 1 minutes ✅
   Batch size: 10 contacts
   Max instances: 1

📋 Configuring DeBounce email validation scheduler...
   Interval: 1 minutes ✅
   Batch size: 50 emails
   Max instances: 1
```

---

## Why 1 Minute for Development?

### Benefits

1. **Faster Testing**
   - Queue a contact for validation
   - See results in 1 minute instead of 5
   - Iterate quickly during development

2. **Immediate Feedback**
   - Test scheduler functionality
   - Verify error handling
   - Debug issues faster

3. **Better Development Experience**
   - Don't wait 5 minutes between tests
   - Rapid iteration on scheduler logic
   - Easier to reproduce issues

### Trade-offs

1. **Higher API Usage**
   - More frequent API calls to DeBounce, Brevo, HubSpot
   - May hit rate limits faster
   - Higher costs during development

2. **More Database Load**
   - More frequent queries
   - More write operations
   - Higher CPU usage

3. **More Log Noise**
   - Scheduler runs more frequently
   - More log entries
   - Harder to spot specific issues

---

## Production Configuration

**For production deployment, change back to 5 minutes:**

```bash
# Brevo Sync Scheduler
BREVO_SYNC_SCHEDULER_INTERVAL_MINUTES=5

# HubSpot Sync Scheduler
HUBSPOT_SYNC_SCHEDULER_INTERVAL_MINUTES=5

# DeBounce Validation Scheduler
DEBOUNCE_VALIDATION_SCHEDULER_INTERVAL_MINUTES=5
```

### Why 5 Minutes for Production?

1. **API Rate Limits**
   - Respects third-party API rate limits
   - Avoids hitting quotas
   - Reduces costs

2. **Server Resources**
   - Lower CPU usage
   - Fewer database queries
   - More efficient operation

3. **Reasonable Latency**
   - 5 minutes is acceptable for background processing
   - Balances responsiveness with efficiency
   - Industry standard for batch operations

---

## How to Change

### Step 1: Update `.env` File

```bash
# Edit the .env file
nano /path/to/.env

# Change the interval values
BREVO_SYNC_SCHEDULER_INTERVAL_MINUTES=5
HUBSPOT_SYNC_SCHEDULER_INTERVAL_MINUTES=5
DEBOUNCE_VALIDATION_SCHEDULER_INTERVAL_MINUTES=5
```

### Step 2: Rebuild Docker Container

```bash
# Rebuild and restart
docker compose up --build -d

# Verify new settings
docker logs scraper-sky-backend-scrapersky-1 2>&1 | grep "Interval:"
```

### Step 3: Verify

Check logs to confirm the new interval is active:
```
Interval: 5 minutes ✅
```

---

## Other Scheduler Settings

### Batch Sizes

**Current values (same for dev and prod):**
```bash
BREVO_SYNC_SCHEDULER_BATCH_SIZE=10
HUBSPOT_SYNC_SCHEDULER_BATCH_SIZE=10
DEBOUNCE_VALIDATION_SCHEDULER_BATCH_SIZE=50
```

**Why these values?**
- **Brevo/HubSpot:** 10 contacts per batch
  - Balances throughput with API limits
  - Reduces risk of timeout
  - Easier to debug issues

- **DeBounce:** 50 emails per batch
  - DeBounce has no bulk endpoint (sequential validation)
  - Higher batch size acceptable since it's just queueing
  - Actual validation happens sequentially

### Max Instances

**Current values (same for dev and prod):**
```bash
BREVO_SYNC_SCHEDULER_MAX_INSTANCES=1
HUBSPOT_SYNC_SCHEDULER_MAX_INSTANCES=1
DEBOUNCE_VALIDATION_SCHEDULER_MAX_INSTANCES=1
```

**Why 1 instance?**
- Prevents concurrent processing of same contacts
- Avoids race conditions
- Simpler error handling
- Sufficient for current load

---

## Scheduler Behavior

### How Schedulers Work

1. **Startup**
   - Scheduler registers with APScheduler
   - First run scheduled immediately
   - Subsequent runs every N minutes

2. **Execution**
   - Query for contacts with status "Queued"
   - Process batch (10 or 50 contacts)
   - Update statuses
   - Commit to database

3. **Next Run**
   - Schedule next run N minutes from start time
   - Not from completion time
   - Ensures consistent intervals

### Example Timeline (1 Minute Interval)

```
00:00 - Scheduler starts, first run scheduled
00:00 - First run executes (processes 10 contacts, takes 5 seconds)
00:01 - Second run executes (processes 10 contacts, takes 5 seconds)
00:02 - Third run executes (processes 10 contacts, takes 5 seconds)
...
```

### Example Timeline (5 Minute Interval)

```
00:00 - Scheduler starts, first run scheduled
00:00 - First run executes (processes 10 contacts, takes 5 seconds)
00:05 - Second run executes (processes 10 contacts, takes 5 seconds)
00:10 - Third run executes (processes 10 contacts, takes 5 seconds)
...
```

---

## Monitoring

### Check Scheduler Status

```bash
# View scheduler logs
docker logs scraper-sky-backend-scrapersky-1 -f | grep scheduler

# Check next run time
docker logs scraper-sky-backend-scrapersky-1 | grep "Next wakeup"

# View specific scheduler
docker logs scraper-sky-backend-scrapersky-1 | grep "DeBounce"
```

### Check Processing Stats

```bash
# View Brevo sync stats
docker logs scraper-sky-backend-scrapersky-1 | grep "Brevo.*complete"

# View HubSpot sync stats
docker logs scraper-sky-backend-scrapersky-1 | grep "HubSpot.*complete"

# View DeBounce validation stats
docker logs scraper-sky-backend-scrapersky-1 | grep "DeBounce.*complete"
```

---

## Troubleshooting

### Scheduler Not Running

**Symptom:** No scheduler logs appearing

**Check:**
1. Is Docker container running?
   ```bash
   docker ps | grep scrapersky
   ```

2. Are environment variables loaded?
   ```bash
   docker exec scraper-sky-backend-scrapersky-1 env | grep SCHEDULER
   ```

3. Is APScheduler starting?
   ```bash
   docker logs scraper-sky-backend-scrapersky-1 | grep "APScheduler"
   ```

### Scheduler Running Too Frequently

**Symptom:** Scheduler runs more often than expected

**Cause:** Interval set too low or multiple instances running

**Fix:**
1. Check interval setting in `.env`
2. Verify `MAX_INSTANCES=1`
3. Restart Docker container

### Scheduler Not Picking Up Changes

**Symptom:** Changed interval in `.env` but scheduler still uses old value

**Cause:** Docker container not rebuilt

**Fix:**
```bash
docker compose up --build -d
```

---

## Summary

### Current State ✅

- **Development Mode:** All intervals set to 1 minute
- **Brevo Scheduler:** 1 minute, 10 contacts per batch
- **HubSpot Scheduler:** 1 minute, 10 contacts per batch
- **DeBounce Scheduler:** 1 minute, 50 emails per batch

### Production Recommendation

- **Production Mode:** Change all intervals to 5 minutes
- **Reason:** Balance between responsiveness and resource usage
- **When:** Before deploying to production environment

### How to Change

1. Edit `.env` file
2. Update `*_INTERVAL_MINUTES` values
3. Rebuild Docker: `docker compose up --build -d`
4. Verify in logs: `docker logs ... | grep "Interval:"`

---

**Created:** 2025-11-19  
**Author:** Local Claude (Windsurf)  
**Status:** ✅ Development mode active (1 minute intervals)  
**Next Action:** Change to 5 minutes before production deployment
