# n8n Webhook Integration - Trigger Fields

**Date:** 2025-11-19  
**Status:** ✅ Verified and Documented

---

## Frontend Button Action

When the frontend "Sync to n8n" button is clicked, it should set:

```typescript
// What the frontend button should do:
contact.n8n_sync_status = 'Selected'
contact.n8n_processing_status = 'Queued'
```

---

## Database Fields

### Primary Trigger Fields

| Field | Type | Purpose | Frontend Sets |
|-------|------|---------|---------------|
| `n8n_sync_status` | ENUM | User selection status | ✅ `'Selected'` |
| `n8n_processing_status` | ENUM | Scheduler processing status | ✅ `'Queued'` |

### Supporting Fields

| Field | Type | Purpose | Set By |
|-------|------|---------|--------|
| `n8n_processing_error` | TEXT | Error messages | Backend (scheduler) |
| `n8n_workflow_id` | VARCHAR | n8n workflow identifier | Backend (future) |
| `retry_count` | INTEGER | Number of retry attempts | Backend (scheduler) |
| `next_retry_at` | TIMESTAMP | When to retry failed sends | Backend (scheduler) |

---

## Field Values

### n8n_sync_status (CRMSyncStatus)

**Valid values:**
- `'New'` - Default, not yet selected
- `'Selected'` - ✅ **Frontend sets this** (user clicked button)
- `'Queued'` - Ready for processing
- `'Processing'` - Currently being processed
- `'Complete'` - Successfully sent to n8n
- `'Error'` - Failed after max retries
- `'Skipped'` - User chose to skip

**Frontend Action:**
```sql
UPDATE contacts 
SET n8n_sync_status = 'Selected'
WHERE id = :contact_id
```

### n8n_processing_status (CRMProcessingStatus)

**Valid values:**
- `NULL` - Not yet queued
- `'Queued'` - ✅ **Frontend sets this** (ready for scheduler)
- `'Processing'` - Scheduler is sending to webhook
- `'Complete'` - Successfully sent to n8n
- `'Error'` - Failed (will retry if retry_count < max)

**Frontend Action:**
```sql
UPDATE contacts 
SET n8n_processing_status = 'Queued'
WHERE id = :contact_id
```

---

## How It Works

### 1. Frontend Button Click

**User Action:** Clicks "Sync to n8n" button in Contact Launchpad

**Frontend Updates:**
```typescript
// API call to update contact
PATCH /api/v3/contacts/{contact_id}
{
  "n8n_sync_status": "Selected",
  "n8n_processing_status": "Queued"
}
```

### 2. Scheduler Picks Up Contact

**Scheduler Query:**
```sql
SELECT * FROM contacts
WHERE n8n_processing_status = 'Queued'
AND (next_retry_at IS NULL OR next_retry_at <= NOW())
ORDER BY updated_at ASC
LIMIT 10
```

**Scheduler runs every:** 1 minute (development) / 5 minutes (production)

### 3. Webhook Send

**Scheduler updates status:**
```sql
-- Before sending
UPDATE contacts 
SET n8n_processing_status = 'Processing'
WHERE id = :contact_id

-- After successful send
UPDATE contacts 
SET n8n_sync_status = 'Complete',
    n8n_processing_status = 'Complete'
WHERE id = :contact_id

-- After failed send (will retry)
UPDATE contacts 
SET n8n_processing_status = 'Error',
    n8n_processing_error = :error_message,
    retry_count = retry_count + 1,
    next_retry_at = :next_retry_time
WHERE id = :contact_id
```

---

## Current Database State

**As of 2025-11-19:**

```
sync_status=New             processing_status=NULL            count=71
sync_status=Queued          processing_status=Error           count=2
```

**Interpretation:**
- 71 contacts have never been queued for n8n (default state)
- 2 contacts were queued but failed (our test contacts with expired webhook)

---

## Verification Query

**Check if frontend is setting fields correctly:**

```sql
SELECT 
    id,
    email,
    n8n_sync_status,
    n8n_processing_status,
    n8n_processing_error,
    retry_count,
    next_retry_at,
    updated_at
FROM contacts
WHERE n8n_sync_status != 'New'
OR n8n_processing_status IS NOT NULL
ORDER BY updated_at DESC;
```

**Expected after frontend button click:**
```
n8n_sync_status: Selected ✅
n8n_processing_status: Queued ✅
n8n_processing_error: NULL
retry_count: 0
next_retry_at: NULL
```

---

## Frontend Implementation Checklist

### Required Frontend Changes

- [ ] "Sync to n8n" button exists in Contact Launchpad
- [ ] Button calls API to update contact
- [ ] API sets `n8n_sync_status = 'Selected'`
- [ ] API sets `n8n_processing_status = 'Queued'`
- [ ] UI shows updated status immediately
- [ ] UI polls for status updates (optional)

### API Endpoint

**Existing endpoint:** `PATCH /api/v3/contacts/{contact_id}`

**Request body:**
```json
{
  "n8n_sync_status": "Selected",
  "n8n_processing_status": "Queued"
}
```

**Response:**
```json
{
  "id": "uuid",
  "email": "contact@example.com",
  "n8n_sync_status": "Selected",
  "n8n_processing_status": "Queued",
  ...
}
```

---

## Status Transitions

### Happy Path

```
New → Selected → Queued → Processing → Complete
  ↑      ↑         ↑          ↑           ↑
  |      |         |          |           |
Default  Frontend  Frontend   Scheduler   Scheduler
         Button    Button     (before)    (after success)
```

### Error Path (with retries)

```
Queued → Processing → Error → Queued → Processing → Error → ...
  ↑         ↑          ↑        ↑          ↑          ↑
  |         |          |        |          |          |
Frontend  Scheduler  Scheduler Scheduler  Scheduler  Scheduler
Button    (before)   (failed)  (retry 1)  (before)   (failed)

After max retries (3):
Error (final) - no more retries
```

---

## Testing Frontend Integration

### Manual Test

1. **Open Contact Launchpad**
2. **Select a contact**
3. **Click "Sync to n8n" button**
4. **Verify in database:**
   ```sql
   SELECT n8n_sync_status, n8n_processing_status 
   FROM contacts 
   WHERE id = :contact_id
   ```
5. **Expected:**
   - `n8n_sync_status = 'Selected'`
   - `n8n_processing_status = 'Queued'`
6. **Wait 1 minute** (development mode)
7. **Check logs:**
   ```bash
   docker logs scraper-sky-backend-scrapersky-1 -f | grep "n8n"
   ```
8. **Expected:**
   - `🚀 Starting n8n webhook sync scheduler cycle`
   - `📧 Sending contact {email} to n8n webhook`
   - `✅ Successfully sent {email} to n8n webhook`

### Automated Test

```typescript
// Frontend test
test('Sync to n8n button sets correct fields', async () => {
  const contact = await createTestContact()
  
  // Click button
  await clickSyncToN8nButton(contact.id)
  
  // Verify API call
  expect(apiMock).toHaveBeenCalledWith(
    `PATCH /api/v3/contacts/${contact.id}`,
    {
      n8n_sync_status: 'Selected',
      n8n_processing_status: 'Queued'
    }
  )
  
  // Verify UI update
  expect(contact.n8n_sync_status).toBe('Selected')
  expect(contact.n8n_processing_status).toBe('Queued')
})
```

---

## Common Issues

### Issue: Contact not picked up by scheduler

**Symptoms:**
- Frontend sets status correctly
- Scheduler runs but doesn't process contact

**Possible causes:**
1. `n8n_processing_status` not set to `'Queued'`
2. `next_retry_at` is in the future (from previous failure)
3. Scheduler disabled (N8N_WEBHOOK_URL not set)

**Fix:**
```sql
-- Reset contact for immediate processing
UPDATE contacts
SET n8n_processing_status = 'Queued',
    next_retry_at = NULL
WHERE id = :contact_id
```

### Issue: Contact stuck in "Processing"

**Symptoms:**
- Status shows "Processing" for extended time
- Scheduler crashed mid-processing

**Fix:**
```sql
-- Reset to Queued
UPDATE contacts
SET n8n_processing_status = 'Queued'
WHERE n8n_processing_status = 'Processing'
```

### Issue: Frontend button doesn't update status

**Symptoms:**
- Button clicked but status remains "New"
- No API call made

**Check:**
1. Is API endpoint correct?
2. Is authentication working?
3. Are field names correct in request?
4. Check browser console for errors

---

## Summary

### Trigger Fields (Frontend Sets)

```typescript
{
  n8n_sync_status: 'Selected',      // User selected for n8n sync
  n8n_processing_status: 'Queued'   // Ready for scheduler to process
}
```

### Scheduler Query (Backend Checks)

```sql
WHERE n8n_processing_status = 'Queued'
AND (next_retry_at IS NULL OR next_retry_at <= NOW())
```

### Success Criteria

✅ Frontend sets both fields when button clicked  
✅ Scheduler picks up contact within 1-5 minutes  
✅ Webhook POST sent to n8n  
✅ Status updates to "Complete" on success  
✅ Status updates to "Error" on failure (with retry)  

---

**Created:** 2025-11-19  
**Author:** Local Claude (Windsurf)  
**Status:** ✅ Verified in database and code  
**Related:** WO-020 (n8n webhook integration)
