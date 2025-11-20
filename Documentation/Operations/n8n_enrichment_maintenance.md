# n8n Contact Enrichment - Maintenance Guide

**Feature:** Contact Enrichment via n8n  
**Status:** ✅ Production  
**Audience:** DevOps, System Administrators  
**Last Updated:** 2025-11-19

---

## System Overview

### Architecture

```
┌─────────────────┐         ┌──────────────┐         ┌─────────────────┐
│  Contact Model  │         │ n8n Workflow │         │ Webhook Router  │
│  (15 fields)    │ ──────> │ (enrichment) │ ──────> │ (inbound data)  │
└─────────────────┘         └──────────────┘         └─────────────────┘
        ↑                                                      │
        │                                                      │
        └──────────────────────────────────────────────────────┘
                    Updates contact with enriched data
```

### Components

1. **Outbound Service** (`n8n_sync_service.py`) - WO-020
   - Sends contacts TO n8n for enrichment
   - Scheduler runs every 1-5 minutes
   - Handles retry logic

2. **Inbound Router** (`n8n_webhook_router.py`) - WO-021
   - Receives enriched data FROM n8n
   - Webhook endpoint with Bearer auth
   - Updates 15 database fields

3. **Enrichment Service** (`n8n_enrichment_service.py`)
   - Processes incoming enrichment data
   - Validates and stores in database
   - Handles idempotency

---

## Configuration

### Environment Variables

```bash
# Required
N8N_WEBHOOK_URL=https://your-n8n-instance.com/webhook/contact-enrichment
N8N_WEBHOOK_SECRET=your-secure-bearer-token

# Optional (scheduler intervals)
N8N_SYNC_SCHEDULER_INTERVAL_MINUTES=5  # Production: 5, Dev: 1
```

### Verification

```bash
# Check configuration
docker exec scraper-sky-backend-scrapersky-1 env | grep N8N

# Expected output:
# N8N_WEBHOOK_URL=https://...
# N8N_WEBHOOK_SECRET=***
# N8N_SYNC_SCHEDULER_INTERVAL_MINUTES=5
```

---

## Database Schema

### The 15 Enrichment Fields

```sql
-- Status Tracking (5 fields)
enrichment_status VARCHAR(20)           -- pending/complete/partial/failed
enrichment_started_at TIMESTAMP         -- When enrichment began
enrichment_completed_at TIMESTAMP       -- When enrichment finished
enrichment_error TEXT                   -- Error message if failed
last_enrichment_id VARCHAR(255)         -- For idempotency

-- Enriched Data (7 fields - JSONB)
enriched_phone VARCHAR(50)              -- Additional phone
enriched_address JSONB                  -- {street, city, state, zip, country}
enriched_social_profiles JSONB          -- {linkedin, twitter, facebook}
enriched_company JSONB                  -- {name, website, industry, size}
enriched_additional_emails JSONB        -- Array of emails
enrichment_confidence_score INTEGER     -- 0-100 quality score
enrichment_sources JSONB                -- Array of data sources

-- Metadata (3 fields)
enrichment_duration_seconds FLOAT       -- Processing time
enrichment_api_calls INTEGER            -- Number of API calls
enrichment_cost_estimate FLOAT          -- Estimated cost
```

### Indexes

```sql
-- Check indexes exist
SELECT indexname, indexdef 
FROM pg_indexes 
WHERE tablename = 'contacts' 
AND indexname LIKE '%enrichment%';

-- Expected:
-- idx_contacts_enrichment_status
-- idx_contacts_last_enrichment_id
```

---

## Monitoring

### Health Checks

**1. Check Scheduler is Running**
```bash
docker logs scraper-sky-backend-scrapersky-1 -f | grep "n8n.*scheduler"

# Expected every 1-5 minutes:
# 🚀 Starting n8n webhook sync scheduler cycle
# ✅ n8n webhook sync scheduler cycle complete
```

**2. Check Webhook Endpoint**
```bash
curl -X GET https://your-api.com/api/v3/webhooks/n8n/health \
  -H "Authorization: Bearer ${N8N_WEBHOOK_SECRET}"

# Expected:
# {"status": "healthy", "service": "n8n-webhook"}
```

**3. Check Recent Enrichments**
```sql
SELECT 
    COUNT(*) as total_enriched,
    COUNT(*) FILTER (WHERE enrichment_status = 'complete') as complete,
    COUNT(*) FILTER (WHERE enrichment_status = 'partial') as partial,
    COUNT(*) FILTER (WHERE enrichment_status = 'failed') as failed,
    AVG(enrichment_confidence_score) as avg_confidence,
    AVG(enrichment_duration_seconds) as avg_duration
FROM contacts
WHERE enrichment_completed_at > NOW() - INTERVAL '24 hours';
```

### Key Metrics

**Performance Metrics:**
- Enrichment success rate (target: >90%)
- Average confidence score (target: >70)
- Average duration (target: <30 seconds)
- API calls per enrichment (target: <5)

**Cost Metrics:**
- Average cost per contact (track trends)
- Total daily enrichment cost
- Cost by data source

**Query for Daily Stats:**
```sql
SELECT 
    DATE(enrichment_completed_at) as date,
    COUNT(*) as contacts_enriched,
    AVG(enrichment_confidence_score) as avg_confidence,
    SUM(enrichment_cost_estimate) as total_cost,
    SUM(enrichment_api_calls) as total_api_calls
FROM contacts
WHERE enrichment_completed_at > NOW() - INTERVAL '7 days'
GROUP BY DATE(enrichment_completed_at)
ORDER BY date DESC;
```

---

## Troubleshooting

### Issue: Contacts Not Being Enriched

**Symptoms:**
- Contacts stuck in "Queued" status
- No enrichment activity in logs

**Diagnosis:**
```bash
# 1. Check scheduler is running
docker logs scraper-sky-backend-scrapersky-1 | grep "n8n.*scheduler" | tail -20

# 2. Check webhook URL is configured
docker exec scraper-sky-backend-scrapersky-1 env | grep N8N_WEBHOOK_URL

# 3. Check contacts in queue
docker exec scraper-sky-backend-scrapersky-1 psql $DATABASE_URL -c \
  "SELECT COUNT(*) FROM contacts WHERE n8n_processing_status = 'Queued'"
```

**Solutions:**
1. **Scheduler not running:** Restart container
2. **URL not configured:** Set N8N_WEBHOOK_URL environment variable
3. **No contacts queued:** Frontend not setting status correctly

---

### Issue: Webhook Authentication Failures

**Symptoms:**
- 401 errors in n8n logs
- Enrichment status shows "failed"
- Log message: "Invalid n8n webhook token"

**Diagnosis:**
```bash
# Check webhook secret is set
docker exec scraper-sky-backend-scrapersky-1 env | grep N8N_WEBHOOK_SECRET

# Test webhook manually
curl -X POST https://your-api.com/api/v3/webhooks/n8n/enrichment-complete \
  -H "Authorization: Bearer ${N8N_WEBHOOK_SECRET}" \
  -H "Content-Type: application/json" \
  -d @test_payload.json
```

**Solutions:**
1. **Secret mismatch:** Update N8N_WEBHOOK_SECRET in both systems
2. **Secret not set:** Configure environment variable
3. **Wrong header format:** Ensure "Bearer " prefix

---

### Issue: Low Confidence Scores

**Symptoms:**
- Average confidence score below 60
- Many "partial" enrichment results

**Diagnosis:**
```sql
-- Check confidence score distribution
SELECT 
    CASE 
        WHEN enrichment_confidence_score >= 80 THEN 'High (80-100)'
        WHEN enrichment_confidence_score >= 60 THEN 'Medium (60-79)'
        WHEN enrichment_confidence_score >= 40 THEN 'Low (40-59)'
        ELSE 'Very Low (<40)'
    END as confidence_range,
    COUNT(*) as count,
    AVG(enrichment_confidence_score) as avg_score
FROM contacts
WHERE enrichment_status IS NOT NULL
GROUP BY confidence_range
ORDER BY avg_score DESC;

-- Check which data sources are being used
SELECT 
    jsonb_array_elements_text(enrichment_sources) as source,
    COUNT(*) as usage_count
FROM contacts
WHERE enrichment_sources IS NOT NULL
GROUP BY source
ORDER BY usage_count DESC;
```

**Solutions:**
1. **Poor data quality:** Review n8n workflow data sources
2. **Limited sources:** Add more data sources to n8n workflow
3. **Outdated data:** Re-enrich contacts periodically

---

### Issue: High Costs

**Symptoms:**
- Enrichment costs exceeding budget
- High API call counts

**Diagnosis:**
```sql
-- Cost analysis
SELECT 
    DATE(enrichment_completed_at) as date,
    COUNT(*) as contacts,
    SUM(enrichment_cost_estimate) as total_cost,
    AVG(enrichment_cost_estimate) as avg_cost,
    SUM(enrichment_api_calls) as total_api_calls
FROM contacts
WHERE enrichment_completed_at > NOW() - INTERVAL '30 days'
GROUP BY date
ORDER BY total_cost DESC;

-- Most expensive enrichments
SELECT 
    id,
    email,
    enrichment_cost_estimate,
    enrichment_api_calls,
    enrichment_sources
FROM contacts
WHERE enrichment_cost_estimate > 0.50
ORDER BY enrichment_cost_estimate DESC
LIMIT 20;
```

**Solutions:**
1. **Optimize data sources:** Remove expensive sources with low value
2. **Batch processing:** Enrich in larger batches less frequently
3. **Selective enrichment:** Only enrich high-value contacts
4. **Cache results:** Don't re-enrich recently enriched contacts

---

### Issue: Duplicate Enrichments

**Symptoms:**
- Same contact enriched multiple times
- Idempotency not working

**Diagnosis:**
```sql
-- Check for duplicate enrichment IDs
SELECT 
    last_enrichment_id,
    COUNT(*) as count
FROM contacts
WHERE last_enrichment_id IS NOT NULL
GROUP BY last_enrichment_id
HAVING COUNT(*) > 1;

-- Check enrichment history
SELECT 
    id,
    email,
    last_enrichment_id,
    enrichment_completed_at
FROM contacts
WHERE enrichment_status IS NOT NULL
ORDER BY enrichment_completed_at DESC
LIMIT 50;
```

**Solutions:**
1. **n8n not sending enrichment_id:** Update n8n workflow
2. **Database constraint missing:** Check last_enrichment_id index
3. **Race condition:** Review service idempotency logic

---

## Maintenance Tasks

### Daily

**1. Monitor Success Rate**
```sql
SELECT 
    COUNT(*) FILTER (WHERE enrichment_status = 'complete') * 100.0 / COUNT(*) as success_rate
FROM contacts
WHERE enrichment_completed_at > NOW() - INTERVAL '24 hours';
```

**2. Check for Errors**
```bash
docker logs scraper-sky-backend-scrapersky-1 --since 24h | grep -i "enrichment.*error"
```

**3. Review Costs**
```sql
SELECT SUM(enrichment_cost_estimate) as daily_cost
FROM contacts
WHERE enrichment_completed_at > NOW() - INTERVAL '24 hours';
```

### Weekly

**1. Analyze Confidence Trends**
```sql
SELECT 
    DATE_TRUNC('week', enrichment_completed_at) as week,
    AVG(enrichment_confidence_score) as avg_confidence,
    COUNT(*) as contacts_enriched
FROM contacts
WHERE enrichment_completed_at > NOW() - INTERVAL '8 weeks'
GROUP BY week
ORDER BY week DESC;
```

**2. Review Failed Enrichments**
```sql
SELECT 
    enrichment_error,
    COUNT(*) as count
FROM contacts
WHERE enrichment_status = 'failed'
AND enrichment_completed_at > NOW() - INTERVAL '7 days'
GROUP BY enrichment_error
ORDER BY count DESC;
```

**3. Clean Up Old Errors**
```sql
-- Reset failed contacts older than 30 days for retry
UPDATE contacts
SET n8n_processing_status = 'Queued',
    retry_count = 0,
    next_retry_at = NULL
WHERE enrichment_status = 'failed'
AND enrichment_completed_at < NOW() - INTERVAL '30 days';
```

### Monthly

**1. Cost Analysis Report**
```sql
SELECT 
    DATE_TRUNC('month', enrichment_completed_at) as month,
    COUNT(*) as contacts_enriched,
    SUM(enrichment_cost_estimate) as total_cost,
    AVG(enrichment_cost_estimate) as avg_cost_per_contact,
    AVG(enrichment_confidence_score) as avg_confidence
FROM contacts
WHERE enrichment_completed_at > NOW() - INTERVAL '12 months'
GROUP BY month
ORDER BY month DESC;
```

**2. Data Source Performance**
```sql
-- Analyze which sources provide best data
WITH source_stats AS (
    SELECT 
        jsonb_array_elements_text(enrichment_sources) as source,
        enrichment_confidence_score
    FROM contacts
    WHERE enrichment_sources IS NOT NULL
    AND enrichment_completed_at > NOW() - INTERVAL '30 days'
)
SELECT 
    source,
    COUNT(*) as usage_count,
    AVG(enrichment_confidence_score) as avg_confidence
FROM source_stats
GROUP BY source
ORDER BY avg_confidence DESC;
```

**3. Archive Old Enrichment Data** (Optional)
```sql
-- Archive enrichments older than 1 year
-- (Only if storage is a concern)
CREATE TABLE IF NOT EXISTS contacts_enrichment_archive AS
SELECT 
    id,
    email,
    enrichment_status,
    enrichment_completed_at,
    enrichment_confidence_score,
    enrichment_cost_estimate
FROM contacts
WHERE enrichment_completed_at < NOW() - INTERVAL '1 year';

-- Clear old enrichment data (CAREFUL!)
-- UPDATE contacts
-- SET enrichment_status = NULL,
--     enriched_phone = NULL,
--     ... (all 15 fields)
-- WHERE enrichment_completed_at < NOW() - INTERVAL '1 year';
```

---

## Emergency Procedures

### Disable Enrichment Immediately

```bash
# Stop scheduler by removing webhook URL
docker exec scraper-sky-backend-scrapersky-1 \
  bash -c "unset N8N_WEBHOOK_URL && supervisorctl restart all"

# Or restart container without N8N_WEBHOOK_URL
```

### Reset All Queued Contacts

```sql
-- Clear all pending enrichments
UPDATE contacts
SET n8n_processing_status = NULL,
    retry_count = 0,
    next_retry_at = NULL
WHERE n8n_processing_status IN ('Queued', 'Processing');
```

### Rollback Failed Enrichments

```sql
-- Clear enrichment data for failed contacts
UPDATE contacts
SET enrichment_status = NULL,
    enrichment_error = NULL,
    enriched_phone = NULL,
    enriched_address = NULL,
    enriched_social_profiles = NULL,
    enriched_company = NULL,
    enriched_additional_emails = NULL,
    enrichment_confidence_score = NULL,
    enrichment_sources = NULL,
    enrichment_duration_seconds = NULL,
    enrichment_api_calls = NULL,
    enrichment_cost_estimate = NULL
WHERE enrichment_status = 'failed'
AND enrichment_completed_at > NOW() - INTERVAL '24 hours';
```

---

## Performance Optimization

### Database Indexes

```sql
-- Ensure indexes exist for common queries
CREATE INDEX IF NOT EXISTS idx_contacts_enrichment_status 
ON contacts(enrichment_status);

CREATE INDEX IF NOT EXISTS idx_contacts_enrichment_completed_at 
ON contacts(enrichment_completed_at);

CREATE INDEX IF NOT EXISTS idx_contacts_last_enrichment_id 
ON contacts(last_enrichment_id);

-- Analyze query performance
EXPLAIN ANALYZE
SELECT * FROM contacts
WHERE enrichment_status = 'complete'
AND enrichment_completed_at > NOW() - INTERVAL '7 days';
```

### Scheduler Tuning

**Development:** 1 minute interval
```bash
N8N_SYNC_SCHEDULER_INTERVAL_MINUTES=1
```

**Production:** 5 minute interval
```bash
N8N_SYNC_SCHEDULER_INTERVAL_MINUTES=5
```

**High Volume:** Increase batch size in `n8n_sync_scheduler.py`
```python
batch_size=50  # Default: 10
```

---

## Security

### Webhook Authentication

**Best Practices:**
- Use strong, random Bearer tokens (32+ characters)
- Rotate tokens quarterly
- Never commit tokens to git
- Use environment variables only

**Token Rotation:**
```bash
# 1. Generate new token
NEW_TOKEN=$(openssl rand -base64 32)

# 2. Update n8n workflow with new token
# 3. Update backend environment variable
docker exec scraper-sky-backend-scrapersky-1 \
  bash -c "export N8N_WEBHOOK_SECRET=$NEW_TOKEN && supervisorctl restart all"
```

### Data Privacy

- All enrichment data is from public sources
- Document data sources in `enrichment_sources` field
- Support data deletion requests (GDPR)
- Log all enrichment activities

---

## Related Documentation

- **User Guide:** `Documentation/Guides/n8n_enrichment_user_guide.md`
- **Technical Details:** Router header in `src/routers/v3/n8n_webhook_router.py`
- **Integration Guide:** `Documentation/N8N_TRIGGER_FIELDS.md`
- **Work Orders:** `Documentation/Work_Orders/WO-020_COMPLETE.md`, `WO-021_COMPLETE.md`

---

## Support Contacts

**For Issues:**
- Check logs first: `docker logs scraper-sky-backend-scrapersky-1 -f | grep enrichment`
- Review this guide's troubleshooting section
- Contact DevOps team

**For Feature Requests:**
- Submit via work order system
- Reference WO-020/WO-021 for context

---

**Last Updated:** 2025-11-19  
**Version:** 1.0  
**Maintained By:** DevOps Team
