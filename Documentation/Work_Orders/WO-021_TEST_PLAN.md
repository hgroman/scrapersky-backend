# WO-021: n8n Enrichment Return Data Pipeline - Test Plan

**Work Order:** WO-021
**Status:** ✅ Implementation Complete - Ready for Testing
**Created:** 2025-11-19
**Implementer:** Online Claude
**Tester:** Local Claude (Windsurf IDE with Supabase MCP)

---

## What Was Implemented

### Overview
WO-021 implements the **return data pipeline** for n8n contact enrichment. This completes the two-way integration started in WO-020:

- **WO-020:** Send contact data TO n8n for enrichment ✅ (Complete)
- **WO-021:** Receive enriched data FROM n8n ✅ (Implementation Complete)

### Components Added

1. **Database Migration:** `supabase/migrations/20251119010000_add_enrichment_fields.sql`
   - 15 new fields in `contacts` table
   - Enrichment status tracking (status, timestamps, error, enrichment_id)
   - Enriched data fields (phone, address, social_profiles, company, emails, confidence_score, sources)
   - Enrichment metadata (duration, api_calls, cost)
   - Indexes and constraints

2. **Contact Model:** `src/models/WF7_V2_L1_1of1_ContactModel.py`
   - Added 15 enrichment fields
   - JSONB fields for flexible schema (address, social_profiles, company, etc.)

3. **Pydantic Schemas:** `src/schemas/n8n_enrichment_schemas.py`
   - `EnrichmentCompleteRequest` - Webhook payload from n8n
   - `EnrichmentCompleteResponse` - Success response
   - `EnrichedData`, `AddressData`, `SocialProfiles`, `CompanyData` - Nested schemas
   - `EnrichmentMetadata` - Process metadata
   - Field validation (confidence_score 0-100, status enum)

4. **Service Layer:** `src/services/crm/n8n_enrichment_service.py`
   - `N8nEnrichmentService` class
   - Contact validation
   - Idempotency checking (prevents duplicate processing)
   - Enriched data field updates
   - Status tracking and metadata storage

5. **Router:** `src/routers/v3/n8n_webhook_router.py`
   - `POST /api/v3/webhooks/n8n/enrichment-complete` endpoint
   - Bearer token authentication via `N8N_WEBHOOK_SECRET`
   - Error handling (401, 404, 422, 500)
   - `GET /api/v3/webhooks/n8n/health` endpoint

6. **Configuration:**
   - `src/main.py` - Router registered
   - `.env.example` - Updated N8N_WEBHOOK_SECRET documentation
   - `src/config/settings.py` - Already has N8N_WEBHOOK_SECRET (from WO-020)

---

## Prerequisites

### 1. Database Migration

**Apply the migration using Supabase MCP:**

```sql
-- Execute via Supabase MCP execute_sql tool
-- Or apply via Supabase Dashboard SQL Editor

-- File: supabase/migrations/20251119010000_add_enrichment_fields.sql
```

**Verify migration applied:**

```sql
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'contacts'
  AND column_name LIKE 'enrichment%' OR column_name LIKE 'enriched%' OR column_name = 'last_enrichment_id'
ORDER BY ordinal_position;
```

**Expected Result:** 15 new columns visible

### 2. Environment Configuration

**Update `.env` file:**

```bash
# n8n Webhook Authentication (Required for WO-021)
N8N_WEBHOOK_SECRET=your-secure-random-token-here

# Example: Generate a secure token
# python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**⚠️ CRITICAL:** `N8N_WEBHOOK_SECRET` **MUST** be configured for the webhook endpoint to work.

### 3. Restart Application

```bash
# In Docker
docker compose down
docker compose up --build

# Watch logs
docker compose logs -f app
```

**Expected Log Output:**
```
✅ n8n webhook sync scheduler job added
INFO: Application startup complete
```

---

## Test Scenarios

### Test 1: Database Schema Verification (5 min)

**Objective:** Verify all 15 enrichment fields exist in database

**SQL Query:**
```sql
SELECT
    column_name,
    data_type,
    character_maximum_length,
    is_nullable
FROM information_schema.columns
WHERE table_name = 'contacts'
  AND (
    column_name LIKE 'enrichment%'
    OR column_name LIKE 'enriched%'
    OR column_name = 'last_enrichment_id'
  )
ORDER BY column_name;
```

**Expected Fields:**
- `enriched_additional_emails` (jsonb, nullable)
- `enriched_address` (jsonb, nullable)
- `enriched_company` (jsonb, nullable)
- `enriched_phone` (varchar 50, nullable)
- `enriched_social_profiles` (jsonb, nullable)
- `enrichment_api_calls` (integer, nullable)
- `enrichment_completed_at` (timestamp, nullable)
- `enrichment_confidence_score` (integer, nullable)
- `enrichment_cost_estimate` (double precision, nullable)
- `enrichment_duration_seconds` (double precision, nullable)
- `enrichment_error` (text, nullable)
- `enrichment_sources` (jsonb, nullable)
- `enrichment_started_at` (timestamp, nullable)
- `enrichment_status` (varchar 20, nullable)
- `last_enrichment_id` (varchar 255, nullable)

**✅ Pass Criteria:** All 15 fields exist with correct types

---

### Test 2: Health Check Endpoint (5 min)

**Objective:** Verify webhook endpoint is configured and accessible

**cURL Command:**
```bash
# Test WITHOUT authentication (should fail)
curl -X GET http://localhost:8000/api/v3/webhooks/n8n/health

# Test WITH authentication (should succeed)
curl -X GET http://localhost:8000/api/v3/webhooks/n8n/health \
  -H "Authorization: Bearer your-webhook-secret-here"
```

**Expected Response (without auth - 401):**
```json
{
  "detail": "Missing Authorization header"
}
```

**Expected Response (with auth - 200):**
```json
{
  "status": "healthy",
  "webhook_url": "/api/v3/webhooks/n8n/enrichment-complete",
  "authentication": "configured",
  "message": "n8n webhook endpoint is ready to receive enrichment data"
}
```

**✅ Pass Criteria:**
- Without auth returns 401
- With auth returns 200 and healthy status

---

### Test 3: Basic Enrichment Processing (15 min)

**Objective:** Send enrichment data to webhook and verify database updates

**Step 1: Create test contact**

```sql
-- Insert test contact
INSERT INTO contacts (
    email,
    name,
    domain_id,
    page_id,
    n8n_sync_status,
    enrichment_status
)
SELECT
    'enrichment.test@example.com',
    'Test Enrichment User',
    (SELECT id FROM domains LIMIT 1),  -- Use any existing domain
    (SELECT id FROM pages LIMIT 1),    -- Use any existing page
    'Complete',
    'pending'
RETURNING id, email, name;
```

**Copy the returned contact ID for next step.**

**Step 2: Send enrichment data via webhook**

```bash
# Replace YOUR_CONTACT_ID with the UUID from Step 1
# Replace YOUR_WEBHOOK_SECRET with your N8N_WEBHOOK_SECRET

curl -X POST http://localhost:8000/api/v3/webhooks/n8n/enrichment-complete \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_WEBHOOK_SECRET" \
  -d '{
    "contact_id": "YOUR_CONTACT_ID",
    "enrichment_id": "test-enrichment-001",
    "status": "complete",
    "timestamp": "2025-11-19T10:00:00Z",
    "enriched_data": {
      "phone": "+1-555-987-6543",
      "address": {
        "street": "123 Tech Boulevard",
        "city": "San Francisco",
        "state": "CA",
        "zip": "94102",
        "country": "USA"
      },
      "social_profiles": {
        "linkedin": "https://linkedin.com/in/testuser",
        "twitter": "https://twitter.com/testuser"
      },
      "company": {
        "name": "Tech Startup Inc",
        "website": "https://techstartup.example",
        "industry": "Software",
        "size": "11-50"
      },
      "additional_emails": [
        "test.user@techstartup.example",
        "tuser@techstartup.example"
      ],
      "confidence_score": 92,
      "sources": ["linkedin_api", "clearbit", "hunter_io"]
    },
    "metadata": {
      "enrichment_duration_seconds": 8.5,
      "api_calls_made": 3,
      "cost_estimate": 0.12
    }
  }'
```

**Expected Response (200):**
```json
{
  "success": true,
  "contact_id": "YOUR_CONTACT_ID",
  "enrichment_id": "test-enrichment-001",
  "message": "Enrichment data saved successfully",
  "updated_fields": [
    "enriched_phone",
    "enriched_address",
    "enriched_social_profiles",
    "enriched_company",
    "enriched_additional_emails",
    "enrichment_confidence_score",
    "enrichment_sources"
  ]
}
```

**Step 3: Verify database updates**

```sql
-- Check enriched data
SELECT
    email,
    enrichment_status,
    enrichment_completed_at,
    last_enrichment_id,
    enriched_phone,
    enriched_address,
    enriched_social_profiles,
    enriched_company,
    enriched_additional_emails,
    enrichment_confidence_score,
    enrichment_sources,
    enrichment_duration_seconds,
    enrichment_api_calls,
    enrichment_cost_estimate
FROM contacts
WHERE id = 'YOUR_CONTACT_ID';
```

**Expected Results:**
- `enrichment_status` = `'complete'`
- `enrichment_completed_at` = recent timestamp
- `last_enrichment_id` = `'test-enrichment-001'`
- `enriched_phone` = `'+1-555-987-6543'`
- `enriched_address` = JSON object with street, city, state, zip, country
- `enriched_social_profiles` = JSON object with linkedin, twitter
- `enriched_company` = JSON object with name, website, industry, size
- `enriched_additional_emails` = JSON array with 2 emails
- `enrichment_confidence_score` = `92`
- `enrichment_sources` = JSON array with 3 sources
- `enrichment_duration_seconds` = `8.5`
- `enrichment_api_calls` = `3`
- `enrichment_cost_estimate` = `0.12`

**✅ Pass Criteria:** All enriched data fields populated correctly

---

### Test 4: Idempotency Test (10 min)

**Objective:** Verify duplicate enrichment_id is rejected (prevents duplicate processing)

**Step 1: Send SAME enrichment_id again**

```bash
# Use SAME enrichment_id from Test 3
curl -X POST http://localhost:8000/api/v3/webhooks/n8n/enrichment-complete \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_WEBHOOK_SECRET" \
  -d '{
    "contact_id": "YOUR_CONTACT_ID",
    "enrichment_id": "test-enrichment-001",
    "status": "complete",
    "timestamp": "2025-11-19T10:05:00Z",
    "enriched_data": {
      "phone": "+1-555-DIFFERENT",
      "confidence_score": 50
    }
  }'
```

**Expected Response (200):**
```json
{
  "success": true,
  "contact_id": "YOUR_CONTACT_ID",
  "enrichment_id": "test-enrichment-001",
  "message": "Enrichment already processed (idempotent)",
  "updated_fields": []
}
```

**Step 2: Verify data NOT overwritten**

```sql
SELECT
    enriched_phone,
    enrichment_confidence_score,
    last_enrichment_id
FROM contacts
WHERE id = 'YOUR_CONTACT_ID';
```

**Expected Results:**
- `enriched_phone` = `'+1-555-987-6543'` (original, NOT changed)
- `enrichment_confidence_score` = `92` (original, NOT changed)
- `last_enrichment_id` = `'test-enrichment-001'`

**✅ Pass Criteria:** Data remains unchanged, idempotency message returned

---

### Test 5: Partial Enrichment (10 min)

**Objective:** Handle partial enrichment (some data available)

**Step 1: Create new test contact**

```sql
INSERT INTO contacts (
    email,
    name,
    domain_id,
    page_id,
    enrichment_status
)
SELECT
    'partial.test@example.com',
    'Partial Enrichment Test',
    (SELECT id FROM domains LIMIT 1),
    (SELECT id FROM pages LIMIT 1),
    'pending'
RETURNING id;
```

**Step 2: Send partial enrichment**

```bash
curl -X POST http://localhost:8000/api/v3/webhooks/n8n/enrichment-complete \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_WEBHOOK_SECRET" \
  -d '{
    "contact_id": "YOUR_NEW_CONTACT_ID",
    "enrichment_id": "test-enrichment-002",
    "status": "partial",
    "timestamp": "2025-11-19T10:10:00Z",
    "enriched_data": {
      "phone": "+1-555-111-2222",
      "confidence_score": 45
    },
    "metadata": {
      "enrichment_duration_seconds": 3.2,
      "api_calls_made": 1
    }
  }'
```

**Expected Response (200):**
```json
{
  "success": true,
  "contact_id": "YOUR_NEW_CONTACT_ID",
  "enrichment_id": "test-enrichment-002",
  "message": "Enrichment data saved successfully",
  "updated_fields": ["enriched_phone", "enrichment_confidence_score"]
}
```

**Step 3: Verify partial data saved**

```sql
SELECT
    enrichment_status,
    enriched_phone,
    enriched_address,
    enriched_company,
    enrichment_confidence_score
FROM contacts
WHERE id = 'YOUR_NEW_CONTACT_ID';
```

**Expected Results:**
- `enrichment_status` = `'partial'`
- `enriched_phone` = `'+1-555-111-2222'`
- `enriched_address` = `NULL` (not provided)
- `enriched_company` = `NULL` (not provided)
- `enrichment_confidence_score` = `45`

**✅ Pass Criteria:** Partial status set, only provided fields populated

---

### Test 6: Failed Enrichment (10 min)

**Objective:** Handle failed enrichment gracefully

**Step 1: Send failed enrichment**

```bash
curl -X POST http://localhost:8000/api/v3/webhooks/n8n/enrichment-complete \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_WEBHOOK_SECRET" \
  -d '{
    "contact_id": "YOUR_NEW_CONTACT_ID",
    "enrichment_id": "test-enrichment-003",
    "status": "failed",
    "timestamp": "2025-11-19T10:15:00Z",
    "metadata": {
      "enrichment_duration_seconds": 15.0
    }
  }'
```

**Expected Response (200):**
```json
{
  "success": true,
  "contact_id": "YOUR_NEW_CONTACT_ID",
  "enrichment_id": "test-enrichment-003",
  "message": "Enrichment data saved successfully",
  "updated_fields": []
}
```

**Step 2: Verify failed status**

```sql
SELECT
    enrichment_status,
    enrichment_completed_at,
    last_enrichment_id,
    enrichment_duration_seconds
FROM contacts
WHERE id = 'YOUR_NEW_CONTACT_ID';
```

**Expected Results:**
- `enrichment_status` = `'failed'`
- `enrichment_completed_at` = recent timestamp
- `last_enrichment_id` = `'test-enrichment-003'`
- `enrichment_duration_seconds` = `15.0`

**✅ Pass Criteria:** Failed status recorded, metadata saved

---

### Test 7: Authentication Tests (10 min)

**Objective:** Verify Bearer token authentication works correctly

**Test 7a: Missing Authorization header**

```bash
curl -X POST http://localhost:8000/api/v3/webhooks/n8n/enrichment-complete \
  -H "Content-Type: application/json" \
  -d '{"contact_id": "test", "enrichment_id": "test", "status": "complete", "timestamp": "2025-11-19T10:00:00Z"}'
```

**Expected Response (401):**
```json
{
  "detail": "Missing Authorization header"
}
```

**Test 7b: Invalid Bearer token format**

```bash
curl -X POST http://localhost:8000/api/v3/webhooks/n8n/enrichment-complete \
  -H "Content-Type: application/json" \
  -H "Authorization: InvalidFormat" \
  -d '{"contact_id": "test", "enrichment_id": "test", "status": "complete", "timestamp": "2025-11-19T10:00:00Z"}'
```

**Expected Response (401):**
```json
{
  "detail": "Authorization header must be 'Bearer {token}'"
}
```

**Test 7c: Wrong Bearer token**

```bash
curl -X POST http://localhost:8000/api/v3/webhooks/n8n/enrichment-complete \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer wrong-token-here" \
  -d '{"contact_id": "test", "enrichment_id": "test", "status": "complete", "timestamp": "2025-11-19T10:00:00Z"}'
```

**Expected Response (401):**
```json
{
  "detail": "Invalid webhook token"
}
```

**✅ Pass Criteria:** All auth failures return 401 with appropriate error messages

---

### Test 8: Validation Tests (10 min)

**Objective:** Verify payload validation works correctly

**Test 8a: Invalid contact UUID**

```bash
curl -X POST http://localhost:8000/api/v3/webhooks/n8n/enrichment-complete \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_WEBHOOK_SECRET" \
  -d '{
    "contact_id": "not-a-valid-uuid",
    "enrichment_id": "test",
    "status": "complete",
    "timestamp": "2025-11-19T10:00:00Z"
  }'
```

**Expected Response (422):**
```json
{
  "detail": "Invalid contact_id format: not-a-valid-uuid"
}
```

**Test 8b: Contact not found**

```bash
curl -X POST http://localhost:8000/api/v3/webhooks/n8n/enrichment-complete \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_WEBHOOK_SECRET" \
  -d '{
    "contact_id": "00000000-0000-0000-0000-000000000000",
    "enrichment_id": "test",
    "status": "complete",
    "timestamp": "2025-11-19T10:00:00Z"
  }'
```

**Expected Response (404):**
```json
{
  "detail": "Contact not found: 00000000-0000-0000-0000-000000000000"
}
```

**Test 8c: Invalid status value**

```bash
curl -X POST http://localhost:8000/api/v3/webhooks/n8n/enrichment-complete \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_WEBHOOK_SECRET" \
  -d '{
    "contact_id": "YOUR_CONTACT_ID",
    "enrichment_id": "test",
    "status": "invalid_status",
    "timestamp": "2025-11-19T10:00:00Z"
  }'
```

**Expected Response (422):**
```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "status"],
      "msg": "Value error, status must be one of: complete, partial, failed"
    }
  ]
}
```

**Test 8d: Invalid confidence_score (out of range)**

```bash
curl -X POST http://localhost:8000/api/v3/webhooks/n8n/enrichment-complete \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_WEBHOOK_SECRET" \
  -d '{
    "contact_id": "YOUR_CONTACT_ID",
    "enrichment_id": "test",
    "status": "complete",
    "timestamp": "2025-11-19T10:00:00Z",
    "enriched_data": {
      "confidence_score": 150
    }
  }'
```

**Expected Response (422):**
```json
{
  "detail": [
    {
      "type": "less_than_equal",
      "loc": ["body", "enriched_data", "confidence_score"],
      "msg": "Input should be less than or equal to 100"
    }
  ]
}
```

**✅ Pass Criteria:** All validation errors return 422 with descriptive messages

---

## Application Logs to Monitor

**Expected Log Output (Success):**

```
INFO: 🎣 Webhook received: contact_id=..., enrichment_id=test-enrichment-001, status=complete
INFO: 📥 Processing enrichment for contact ..., enrichment_id: test-enrichment-001, status: complete
INFO: ✅ Contact validated: enrichment.test@example.com (...)
DEBUG: 📞 Updated phone: +1-555-987-6543
DEBUG: 📍 Updated address: San Francisco, CA
DEBUG: 👥 Updated social profiles
DEBUG: 🏢 Updated company: Tech Startup Inc
DEBUG: 📧 Updated additional emails: 2 found
DEBUG: 📊 Confidence score: 92%
DEBUG: 🔍 Sources: ['linkedin_api', 'clearbit', 'hunter_io']
INFO: ✅ Updated 7 enriched data fields
DEBUG: 📈 Metadata: 8.5s, 3 API calls, $0.1200 cost
INFO: ✅ Status updated to: complete
INFO: ✅ Enrichment complete for contact ... Updated 7 fields: [...]
INFO: ✅ Webhook processed successfully: [...]
```

**Expected Log Output (Idempotency):**

```
INFO: 🎣 Webhook received: contact_id=..., enrichment_id=test-enrichment-001, status=complete
INFO: 📥 Processing enrichment for contact ..., enrichment_id: test-enrichment-001, status: complete
INFO: ✅ Contact validated: enrichment.test@example.com (...)
INFO: 🔄 Idempotency check: enrichment_id test-enrichment-001 already processed
INFO: ⏭️ Enrichment test-enrichment-001 already processed for contact ... - skipping
INFO: ✅ Webhook processed successfully: []
```

**Expected Log Output (Authentication Failure):**

```
WARNING: ⚠️ Invalid n8n webhook token received
```

---

## Troubleshooting

### Issue: 401 Unauthorized

**Symptom:** All webhook requests fail with 401

**Possible Causes:**
1. `N8N_WEBHOOK_SECRET` not set in `.env`
2. Token mismatch between `.env` and cURL request
3. Authorization header format incorrect

**Solution:**
```bash
# Check environment variable is set
docker compose exec app env | grep N8N_WEBHOOK_SECRET

# Verify it matches your cURL command
# Format must be: Authorization: Bearer {exactly-what-is-in-env}
```

### Issue: 500 Internal Server Error

**Symptom:** Webhook returns 500

**Possible Causes:**
1. Database migration not applied
2. Application not restarted after code changes
3. Model import error

**Solution:**
```bash
# Check migration applied
docker compose exec app psql $DATABASE_URL -c "\d contacts" | grep enrichment

# Restart application
docker compose restart app

# Check logs for errors
docker compose logs -f app
```

### Issue: 404 Contact Not Found

**Symptom:** Webhook returns 404 even though contact exists

**Possible Causes:**
1. Wrong contact UUID (typo)
2. Contact in different database than application

**Solution:**
```sql
-- Verify contact exists
SELECT id, email FROM contacts WHERE id = 'YOUR_CONTACT_ID';

-- Verify application database connection
-- Check DATABASE_URL in .env matches where contact was created
```

### Issue: Fields Not Updating

**Symptom:** Webhook returns success but database unchanged

**Possible Causes:**
1. Database transaction not committed
2. Wrong contact ID checked in database
3. Caching issue

**Solution:**
```sql
-- Force refresh query
SELECT * FROM contacts WHERE id = 'YOUR_CONTACT_ID' LIMIT 1;

-- Check application logs for commit messages
docker compose logs -f app | grep -i commit
```

---

## Success Criteria

### All Tests Pass ✅

- [ ] Test 1: Database schema verified (15 fields exist)
- [ ] Test 2: Health check endpoint works with auth
- [ ] Test 3: Basic enrichment processing successful
- [ ] Test 4: Idempotency prevents duplicate processing
- [ ] Test 5: Partial enrichment handled correctly
- [ ] Test 6: Failed enrichment recorded properly
- [ ] Test 7: Authentication enforced (all 3 sub-tests)
- [ ] Test 8: Validation errors caught (all 4 sub-tests)

### Application Logs Clean ✅

- [ ] No Python exceptions in logs
- [ ] Expected log messages present (emoji log format)
- [ ] No database connection errors
- [ ] Authentication working (warnings for bad tokens, success for good tokens)

### Database State Correct ✅

- [ ] Enriched data fields populated with correct values
- [ ] JSONB fields contain valid JSON objects
- [ ] Status transitions correct (pending → complete/partial/failed)
- [ ] Idempotency tracked (last_enrichment_id)
- [ ] Metadata stored (duration, api_calls, cost)

---

## Next Steps After Testing

1. **Update WO-021 Status Document**
   - Mark all test scenarios as passed/failed
   - Document any issues found
   - Create `WO-021_TEST_RESULTS.md`

2. **Production Deployment Checklist**
   - [ ] Generate secure `N8N_WEBHOOK_SECRET` token (32+ chars)
   - [ ] Add to production `.env`
   - [ ] Apply database migration to production
   - [ ] Deploy updated code
   - [ ] Configure n8n workflow to POST to webhook
   - [ ] Test with real enrichment workflow

3. **n8n Workflow Configuration**
   - Add "HTTP Request" node to end of enrichment workflow
   - Method: POST
   - URL: `https://your-scrapersky.com/api/v3/webhooks/n8n/enrichment-complete`
   - Headers: `Authorization: Bearer {N8N_WEBHOOK_SECRET}`
   - Body: JSON payload matching `EnrichmentCompleteRequest` schema

4. **Frontend Integration (WO-022)**
   - Display enriched data in contact detail view
   - Show enrichment status badge
   - Link to social profiles
   - Display confidence score

---

**End of Test Plan**

**Created:** 2025-11-19
**Author:** Online Claude
**For:** Local Claude Testing
**Work Order:** WO-021
