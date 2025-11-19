# WO-020: n8n Webhook Integration Test Plan

**Date:** 2025-11-19
**Tester:** Local Claude (Windsurf IDE)
**Status:** 📋 Ready for Testing

---

## Overview

This test plan validates the n8n webhook integration service and scheduler.

**What to Test:**
1. n8n webhook receives contact data
2. Scheduler processes queued contacts automatically
3. Database status updates correctly
4. Error handling works (webhook failures)
5. Retry logic functions properly

---

## Prerequisites

### 1. n8n Webhook Setup

**Option A: Use Your Existing n8n Instance**
- Ensure n8n is running and accessible
- Note your webhook URL
- Optionally configure webhook authentication

**Option B: Quick n8n Test Webhook (Recommended for Testing)**
1. Visit https://webhook.site/ or use your n8n instance
2. Copy the unique webhook URL
3. Use this URL for testing (it will show all received requests)

### 2. Environment Configuration

**Update `.env` file:**
```bash
# n8n Webhook Integration (WO-020)
N8N_WEBHOOK_URL=https://your-webhook-url-here/webhook/contact-enrichment
N8N_WEBHOOK_SECRET=  # Optional - leave empty for testing
N8N_SYNC_SCHEDULER_INTERVAL_MINUTES=5
N8N_SYNC_SCHEDULER_BATCH_SIZE=10
N8N_SYNC_MAX_RETRIES=3
```

**Important:** Replace `N8N_WEBHOOK_URL` with your actual webhook URL!

---

## Test 1: Service Direct Test (Quickest Validation)

### Step 1: Create Test Contact in Database

```sql
-- Via Supabase MCP or direct SQL:
INSERT INTO contacts (
    email,
    name,
    n8n_sync_status,
    n8n_processing_status
)
VALUES (
    'test.n8n.webhook@example.com',
    'n8n Test User',
    'Selected',
    'Queued'
)
RETURNING id;
```

**Save the returned UUID** - you'll need it!

### Step 2: Start Docker Stack

```bash
docker compose up --build
```

### Step 3: Watch Server Logs

```bash
docker compose logs -f app | grep "n8n"
```

**Expected Log Output (within 5 minutes):**
```
✅ n8n webhook sync scheduler job registered successfully
🚀 Starting n8n webhook sync scheduler cycle
📧 Sending contact test.n8n.webhook@example.com to n8n webhook
📤 POSTing to n8n webhook: https://...
✅ Webhook accepted contact test.n8n.webhook@example.com (HTTP 200)
✅ Successfully sent test.n8n.webhook@example.com to n8n webhook
✅ Finished n8n webhook sync scheduler cycle
```

### Step 4: Verify in n8n/Webhook Site

**If using webhook.site:**
- Refresh the page
- You should see a POST request with JSON payload:
```json
{
  "contact_id": "uuid-here",
  "email": "test.n8n.webhook@example.com",
  "name": "n8n Test User",
  "scrapersky_domain_id": null,
  "scrapersky_page_id": null,
  "timestamp": "2025-11-19T10:00:00Z"
}
```

**If using n8n:**
- Check n8n execution history
- Verify workflow received the contact data

### Step 5: Verify Database Updated

```sql
SELECT
    email,
    n8n_sync_status,
    n8n_processing_status,
    n8n_processing_error,
    retry_count
FROM contacts
WHERE email = 'test.n8n.webhook@example.com';
```

**Expected Results:**
```
email: test.n8n.webhook@example.com
n8n_sync_status: Complete
n8n_processing_status: Complete
n8n_processing_error: NULL
retry_count: 0
```

---

## Test 2: Scheduler Configuration Test

### Verify Scheduler Registered

**Check Docker logs on startup:**
```bash
docker compose logs app | grep "n8n webhook sync scheduler"
```

**Expected Output:**
```
📋 Configuring n8n webhook sync scheduler...
   Interval: 5 minutes
   Batch size: 10 contacts
   Max instances: 1
   Webhook URL: https://your-webhook-url...
✅ n8n webhook sync scheduler job registered successfully
```

**If scheduler is disabled:**
```
⚠️ N8N_WEBHOOK_URL not configured - n8n sync scheduler DISABLED
   Set N8N_WEBHOOK_URL in .env to enable automatic n8n webhook sync
```

→ This means you forgot to set `N8N_WEBHOOK_URL` in `.env`

---

## Test 3: Batch Processing Test

### Step 1: Create Multiple Test Contacts

```sql
INSERT INTO contacts (email, name, n8n_sync_status, n8n_processing_status)
VALUES
    ('n8n.batch.test.1@example.com', 'Batch Test 1', 'Selected', 'Queued'),
    ('n8n.batch.test.2@example.com', 'Batch Test 2', 'Selected', 'Queued'),
    ('n8n.batch.test.3@example.com', 'Batch Test 3', 'Selected', 'Queued'),
    ('n8n.batch.test.4@example.com', 'Batch Test 4', 'Selected', 'Queued'),
    ('n8n.batch.test.5@example.com', 'Batch Test 5', 'Selected', 'Queued');
```

### Step 2: Monitor Logs

```bash
docker compose logs -f app | grep "n8n"
```

**Expected:** Within 5 minutes, you should see all 5 contacts processed.

### Step 3: Verify All Completed

```sql
SELECT
    email,
    n8n_processing_status,
    n8n_processing_error
FROM contacts
WHERE email LIKE 'n8n.batch.test.%'
ORDER BY email;
```

**Expected:** All 5 contacts should have `n8n_processing_status = 'Complete'`

---

## Test 4: Error Handling Test

### Step 1: Temporarily Break Webhook URL

**Update `.env`:**
```bash
N8N_WEBHOOK_URL=https://invalid-webhook-url-that-does-not-exist.com/webhook
```

**Restart Docker:**
```bash
docker compose down
docker compose up --build
```

### Step 2: Create Test Contact

```sql
INSERT INTO contacts (email, name, n8n_sync_status, n8n_processing_status)
VALUES (
    'n8n.error.test@example.com',
    'Error Test',
    'Selected',
    'Queued'
);
```

### Step 3: Watch for Error Handling

```bash
docker compose logs -f app | grep "n8n"
```

**Expected Log Output:**
```
❌ n8n webhook send failed for n8n.error.test@example.com: ...
🔄 Scheduled retry 1/3 for n8n.error.test@example.com at ... (in 5 minutes)
```

### Step 4: Verify Error in Database

```sql
SELECT
    email,
    n8n_sync_status,
    n8n_processing_status,
    n8n_processing_error,
    retry_count,
    next_retry_at
FROM contacts
WHERE email = 'n8n.error.test@example.com';
```

**Expected:**
```
n8n_sync_status: Queued  (will retry)
n8n_processing_status: Error
n8n_processing_error: "Webhook HTTP error: ..." or "Webhook returned non-success status..."
retry_count: 1
next_retry_at: <timestamp in ~5 minutes>
```

### Step 5: Fix Webhook URL and Verify Retry

**Update `.env` back to valid URL:**
```bash
N8N_WEBHOOK_URL=https://your-valid-webhook-url-here
```

**Restart Docker:**
```bash
docker compose restart app
```

**Wait 5-10 minutes** for retry to execute.

**Expected:** Contact should eventually reach `Complete` status after retry succeeds.

---

## Test 5: Frontend Integration Test

### Step 1: Use Frontend to Queue Contacts

**Via Contact Launchpad UI:**
1. Select one or more contacts
2. Click dropdown to set status to "Selected"
3. Click "Sync to n8n" button
4. Observe status changes to "Queued"

### Step 2: Verify Automatic Processing

**Watch logs:**
```bash
docker compose logs -f app | grep "n8n"
```

**Within 5 minutes:** Contacts should be processed by scheduler.

### Step 3: Verify in Database

```sql
SELECT
    email,
    n8n_sync_status,
    n8n_processing_status
FROM contacts
WHERE n8n_processing_status IN ('Processing', 'Complete', 'Error')
ORDER BY updated_at DESC
LIMIT 10;
```

---

## Test 6: Max Retries Test

### Goal: Verify that failed contacts eventually stop retrying after max attempts

**This test requires patience** (up to 30 minutes with default settings).

### Step 1: Keep Webhook URL Invalid

```bash
N8N_WEBHOOK_URL=https://intentionally-invalid-url.com/webhook
```

### Step 2: Create Test Contact

```sql
INSERT INTO contacts (email, name, n8n_sync_status, n8n_processing_status)
VALUES (
    'n8n.max.retries.test@example.com',
    'Max Retries Test',
    'Selected',
    'Queued'
);
```

### Step 3: Monitor Retries Over Time

**Every 5-10 minutes, check:**
```sql
SELECT
    email,
    retry_count,
    n8n_processing_status,
    next_retry_at
FROM contacts
WHERE email = 'n8n.max.retries.test@example.com';
```

**Expected Progression:**
```
Retry 0 → retry_count: 1, next_retry_at: +5 minutes
Retry 1 → retry_count: 2, next_retry_at: +10 minutes
Retry 2 → retry_count: 3, next_retry_at: +20 minutes
Retry 3 → retry_count: 3, n8n_processing_status: Error (FINAL)
```

**After max retries (3):**
```
n8n_sync_status: Error
n8n_processing_status: Error
n8n_processing_error: "Webhook HTTP error: ..."
retry_count: 3
next_retry_at: NULL (no more retries)
```

---

## Success Criteria Checklist

### Core Functionality ✅
- [ ] n8n scheduler registers on startup
- [ ] Scheduler processes contacts where `n8n_processing_status = 'Queued'`
- [ ] Webhook receives correct JSON payload
- [ ] Database updates to `Complete` after successful send
- [ ] Contacts are processed within 5 minutes of queueing

### Error Handling ✅
- [ ] Invalid webhook URL triggers error status
- [ ] Error message stored in `n8n_processing_error`
- [ ] Retry count increments on failure
- [ ] `next_retry_at` calculated with exponential backoff
- [ ] After max retries, status becomes `Error` (final)

### Scheduler Behavior ✅
- [ ] Scheduler runs every 5 minutes (default)
- [ ] Batch size respected (processes up to 10 contacts per cycle)
- [ ] No duplicate sends (same contact not processed twice)
- [ ] Scheduler skips contacts with `next_retry_at` in the future

### Integration ✅
- [ ] Frontend "Sync to n8n" button queues contacts
- [ ] Dual-status adapter works (`Selected` → `Queued`)
- [ ] n8n receives data and can process enrichment workflow
- [ ] Logs provide clear visibility into processing

---

## Common Issues & Troubleshooting

### Issue: "n8n sync scheduler DISABLED"

**Cause:** `N8N_WEBHOOK_URL` not set in `.env`

**Fix:**
1. Add `N8N_WEBHOOK_URL=https://...` to `.env`
2. Restart Docker: `docker compose restart app`

### Issue: "Webhook request timed out after 30 seconds"

**Cause:** n8n webhook is slow to respond or down

**Fix:**
- Check n8n instance is running
- Check network connectivity
- Verify webhook URL is correct

### Issue: Contacts stuck in "Processing" status

**Cause:** Scheduler crashed mid-processing

**Fix:**
1. Manually reset status:
```sql
UPDATE contacts
SET n8n_processing_status = 'Queued'
WHERE n8n_processing_status = 'Processing';
```
2. Restart Docker

### Issue: "Webhook returned non-success status: 401"

**Cause:** Webhook requires authentication

**Fix:**
1. Set `N8N_WEBHOOK_SECRET=your-token` in `.env`
2. Restart Docker

---

## Verification Report Template

```markdown
# WO-020 Test Results

**Date:** YYYY-MM-DD
**Tester:** Local Claude
**Environment:** Docker + Supabase

## Test Results

| Test | Status | Notes |
|------|--------|-------|
| Service Direct Test | ✅/❌ | |
| Scheduler Configuration | ✅/❌ | |
| Batch Processing | ✅/❌ | |
| Error Handling | ✅/❌ | |
| Frontend Integration | ✅/❌ | |
| Max Retries Test | ✅/❌ | |

## Issues Found
[List any bugs or unexpected behavior]

## Recommendations
[Any improvements or configuration changes]

## Conclusion
WO-020 is READY / NOT READY for production.
```

---

## Next Steps After Testing

### If All Tests Pass ✅

1. **Document webhook URL** in production `.env`
2. **Configure n8n enrichment workflow**
3. **Plan WO-021:** Return data pipeline (enriched data coming back)
4. **Update frontend** to show enrichment status

### If Tests Fail ❌

1. **Document failures** in test report
2. **Check logs** for specific error messages
3. **Report to Online Claude** for bug fixes
4. **Re-test** after fixes applied

---

**Status:** 📋 **READY FOR LOCAL CLAUDE TESTING**
**Estimated Test Time:** 30-45 minutes
**Prerequisites:** n8n instance or webhook.site for testing

---

**Created:** 2025-11-19
**Author:** Online Claude
**For:** Local Claude (Windsurf IDE with Supabase MCP)
