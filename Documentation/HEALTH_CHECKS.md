# Health Check Playbook
**Purpose:** Verify system health end-to-end  
**Last Updated:** November 17, 2025

---

## Quick Health Check (5 minutes)

### 1. Check Queue Depths
```sql
-- Domains waiting for sitemap discovery
SELECT COUNT(*) FROM domains WHERE sitemap_analysis_status = 'queued';
-- Expected: 0-50 (if higher, scheduler may be stuck)

-- Sitemaps waiting for URL extraction
SELECT COUNT(*) FROM sitemap_files WHERE sitemap_import_status = 'Queued';
-- Expected: 0-100

-- Pages waiting for scraping
SELECT COUNT(*) FROM pages WHERE page_processing_status = 'Queued';
-- Expected: 0-500
```

### 2. Check for Stuck Jobs
```sql
-- Jobs stuck in pending > 5 minutes
SELECT COUNT(*) FROM jobs 
WHERE status = 'pending' 
AND created_at < NOW() - INTERVAL '5 minutes';
-- Expected: 0 (any > 0 indicates problem)
```

### 3. Check Recent Processing
```sql
-- Pages processed in last hour
SELECT COUNT(*) FROM pages 
WHERE page_processing_status = 'Complete' 
AND updated_at > NOW() - INTERVAL '1 hour';
-- Expected: > 0 if system is active
```

### 4. Check Scheduler Logs (Render.com)
- Visit Render.com dashboard
- Check logs for "Setting up scheduler job"
- Should see 3+ schedulers initialized
- No recent errors

---

## WF4→WF5→WF7 End-to-End Test (30 minutes)

### Step 1: Create Test Domain
```sql
INSERT INTO domains (domain, sitemap_curation_status, sitemap_analysis_status)
VALUES ('example.com', 'New', NULL)
RETURNING id;
-- Note the ID
```

### Step 2: Trigger Processing
```sql
UPDATE domains 
SET sitemap_curation_status = 'Selected'
WHERE domain = 'example.com';
-- This should auto-set sitemap_analysis_status = 'queued'
```

### Step 3: Wait & Verify Job Created (2 minutes)
```sql
SELECT * FROM jobs 
WHERE result_data->>'domain' = 'example.com'
ORDER BY created_at DESC LIMIT 1;
-- Expected: status = 'complete' or 'running' within 2 minutes
```

### Step 4: Verify Sitemaps Found (5 minutes)
```sql
SELECT * FROM sitemap_files sf
JOIN domains d ON sf.domain_id = d.id
WHERE d.domain = 'example.com';
-- Expected: 1-10 sitemap records within 5 minutes
```

### Step 5: Verify Pages Imported (10 minutes)
```sql
SELECT COUNT(*) FROM pages p
JOIN sitemap_files sf ON p.sitemap_file_id = sf.id
JOIN domains d ON sf.domain_id = d.id
WHERE d.domain = 'example.com';
-- Expected: 10-1000 page records within 10 minutes
```

### Step 6: Verify Contact Extraction (15 minutes)
```sql
SELECT COUNT(*) FROM pages p
JOIN sitemap_files sf ON p.sitemap_file_id = sf.id
JOIN domains d ON sf.domain_id = d.id
WHERE d.domain = 'example.com'
AND p.page_processing_status = 'Complete';
-- Expected: Some pages complete within 15 minutes
```

---

## Common Failures & Solutions

### No Job Created
**Symptom:** Domain status = 'queued' but no job in jobs table

**Check:**
- Scheduler running? (Render logs)
- Scheduler errors? (Render logs)
- Domain actually queued? `SELECT sitemap_analysis_status FROM domains WHERE domain='...'`

**Solution:**
- Check scheduler logs
- Manually trigger: Set domain back to 'queued'

---

### Job Stuck in Pending
**Symptom:** Job created but status stays 'pending'

**Check:**
- Background task triggered? (This was INCIDENT-2025-11-17)
- Logs show processing started?

**Solution:**
- Check [INCIDENT-2025-11-17-sitemap-jobs-not-processing](./INCIDENTS/2025-11-17-sitemap-jobs-not-processing.md)
- Verify Commit 9f091f6 is deployed

---

### No Sitemaps Found
**Symptom:** Job complete but no sitemap_files records

**Check:**
- Domain actually has sitemaps? (try manually: `curl https://domain.com/sitemap.xml`)
- Job status = 'complete'?
- Job error message?

**Solution:**
- Check job result_data for errors
- Verify domain is accessible
- Check sitemap paths tried

---

### Sitemaps Not Processing
**Symptom:** sitemap_files created but sitemap_import_status = NULL

**Check:**
- Known gap! See [WF4_WF5_WF7_GAPS_IMPROVEMENTS.md #1](./Architecture/WF4_WF5_WF7_GAPS_IMPROVEMENTS.md#1-sitemap-files-not-auto-queued)

**Solution:**
```sql
UPDATE sitemap_files 
SET sitemap_import_status = 'Queued'
WHERE sitemap_import_status IS NULL;
```

---

### Pages Not Processing
**Symptom:** Pages created but page_processing_status = NULL

**Check:**
- page_curation_status = 'Selected'?
- page_processing_status = 'Queued'?
- Page curation scheduler running?

**Solution:**
```sql
-- Manually queue pages
UPDATE pages 
SET page_curation_status = 'Selected',
    page_processing_status = 'Queued'
WHERE page_curation_status = 'New';
```

---

## Monitoring Queries

### Queue Depth Trends
```sql
SELECT 
    DATE_TRUNC('hour', created_at) as hour,
    COUNT(*) as domains_created,
    COUNT(*) FILTER (WHERE sitemap_analysis_status = 'queued') as queued,
    COUNT(*) FILTER (WHERE sitemap_analysis_status = 'submitted') as submitted
FROM domains
WHERE created_at > NOW() - INTERVAL '24 hours'
GROUP BY hour
ORDER BY hour;
```

### Processing Rates
```sql
-- Pages per hour
SELECT 
    DATE_TRUNC('hour', updated_at) as hour,
    COUNT(*) as pages_processed
FROM pages
WHERE page_processing_status = 'Complete'
AND updated_at > NOW() - INTERVAL '24 hours'
GROUP BY hour
ORDER BY hour;
```

### Error Rates
```sql
-- Failures by workflow
SELECT 
    'Domains' as workflow,
    COUNT(*) FILTER (WHERE sitemap_analysis_status = 'failed') as failures,
    COUNT(*) as total,
    ROUND(100.0 * COUNT(*) FILTER (WHERE sitemap_analysis_status = 'failed') / COUNT(*), 2) as failure_rate
FROM domains
WHERE created_at > NOW() - INTERVAL '24 hours'

UNION ALL

SELECT 
    'Sitemaps' as workflow,
    COUNT(*) FILTER (WHERE sitemap_import_status = 'Error') as failures,
    COUNT(*) as total,
    ROUND(100.0 * COUNT(*) FILTER (WHERE sitemap_import_status = 'Error') / COUNT(*), 2) as failure_rate
FROM sitemap_files
WHERE created_at > NOW() - INTERVAL '24 hours'

UNION ALL

SELECT 
    'Pages' as workflow,
    COUNT(*) FILTER (WHERE page_processing_status = 'Error') as failures,
    COUNT(*) as total,
    ROUND(100.0 * COUNT(*) FILTER (WHERE page_processing_status = 'Error') / COUNT(*), 2) as failure_rate
FROM pages
WHERE created_at > NOW() - INTERVAL '24 hours';
```

---

## Expected Timings

- **Job creation:** < 2 minutes (scheduler runs every 1 min)
- **Sitemap discovery:** 2-5 minutes
- **URL import:** 5-10 minutes (depends on sitemap size)
- **Page processing:** 10-30 minutes (depends on batch size and ScraperAPI)

---

## Health Check Automation

**Recommended:** Run these queries on a schedule (e.g., every 15 minutes)

**Alert on:**
- Stuck jobs > 5 minutes
- Queue depth > threshold
- Error rate > 10%
- No processing in last hour (during active hours)

**Reference:** [WF4_WF5_WF7_GAPS_IMPROVEMENTS.md #4](./Architecture/WF4_WF5_WF7_GAPS_IMPROVEMENTS.md#4-no-monitoring-for-stuck-jobs)

---

**For more troubleshooting:**
- [INCIDENTS/](./INCIDENTS/) - Past incidents and solutions
- [PATTERNS.md](./PATTERNS.md) - Common anti-patterns
- [SYSTEM_MAP.md](./SYSTEM_MAP.md) - Architecture overview
