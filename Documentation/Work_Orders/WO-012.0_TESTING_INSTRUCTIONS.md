# Testing Instructions for WO-009, WO-010, WO-011

**Date:** November 17, 2025
**Branch:** `claude/read-context-docs-01E8GWdNj2rJUHkN231xBFus`
**Commits to Test:**
- 1ad0a1d: WO-010 (Direct Domain Submission)
- 4819c66: WO-009 (Direct Page Submission)
- 45fe838: WO-011 (Direct Sitemap Submission)

---

## Overview

This document provides step-by-step testing instructions for the three new direct submission endpoints. These endpoints allow users to bypass early workflow stages and submit data directly.

**New Endpoints:**
1. `/api/v3/domains/direct-submit` - Submit domains directly (WO-010)
2. `/api/v3/pages/direct-submit` - Submit page URLs directly (WO-009)
3. `/api/v3/sitemaps/direct-submit` - Submit sitemap URLs directly (WO-011)

---

## Phase 0: Environment Setup

### Step 1: Build and Start Docker Environment

```bash
# Navigate to project root
cd /home/user/scrapersky-backend

# Stop any running containers
docker compose down

# Build fresh containers with new code
docker compose build --no-cache

# Start the application stack
docker compose up -d

# Wait 10 seconds for services to initialize
sleep 10

# Verify app is running
docker compose ps

# Check app logs for startup errors
docker compose logs app | tail -50
```

**Expected Output:**
- Container status: `Up` for all services (app, db)
- No ERROR messages in logs
- Look for: "Uvicorn running on http://0.0.0.0:8000"
- Look for: "API routers included."

### Step 2: Verify Router Registration

```bash
# Check that new routers are loaded
docker compose logs app | grep -i "router"
```

**Expected Output:**
Should see log entries indicating routers were included (check main.py logging).

### Step 3: Verify OpenAPI Schema

```bash
# Fetch the OpenAPI schema to verify endpoints are registered
curl -s http://localhost:8000/api/schema.json | python -m json.tool > /tmp/openapi_schema.json

# Check for our new endpoints
grep -A 5 "/api/v3/domains/direct-submit" /tmp/openapi_schema.json
grep -A 5 "/api/v3/pages/direct-submit" /tmp/openapi_schema.json
grep -A 5 "/api/v3/sitemaps/direct-submit" /tmp/openapi_schema.json
```

**Expected Output:**
- All three endpoint paths should appear in the schema
- Each should have POST method defined

---

## Phase 1: Authentication Setup

### Step 1: Obtain JWT Token

```bash
# Method 1: Use existing user credentials
# Replace with actual credentials from .env or database
curl -X POST http://localhost:8000/api/v3/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpassword"
  }'

# Method 2: Check if there's a dev/test token endpoint
# (Adjust based on your auth implementation)
```

**Expected Output:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Action:** Save the `access_token` value to an environment variable:
```bash
export JWT_TOKEN="<your_token_here>"
```

### Step 2: Test Authentication

```bash
# Verify token works with a protected endpoint
curl -X GET http://localhost:8000/api/v3/profile \
  -H "Authorization: Bearer $JWT_TOKEN"
```

**Expected Output:**
- HTTP 200 OK
- User profile data returned

**If authentication fails:**
- Check if the app is in debug mode (might bypass auth)
- Check `src/auth/dependencies.py` for auth requirements
- Verify JWT_SECRET_KEY in .env matches what app is using

---

## Phase 2: Test WO-010 (Direct Domain Submission)

### Test Case 1: Basic Domain Submission (auto_queue=false)

```bash
curl -X POST http://localhost:8000/api/v3/domains/direct-submit \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -d '{
    "domains": [
      "example.com",
      "testsite.org"
    ],
    "auto_queue": false
  }'
```

**Expected Response:**
```json
{
  "submitted_count": 2,
  "domain_ids": [
    "<uuid1>",
    "<uuid2>"
  ],
  "auto_queued": false
}
```

**Verification SQL:**
```sql
-- Connect to database
docker compose exec db psql -U postgres -d scrapersky

-- Check domains were created
SELECT id, domain, tenant_id, local_business_id,
       sitemap_curation_status, sitemap_analysis_status
FROM domains
WHERE domain IN ('example.com', 'testsite.org')
ORDER BY created_at DESC;
```

**Expected Database State:**
- `domain`: "example.com", "testsite.org"
- `tenant_id`: "550e8400-e29b-41d4-a716-446655440000" (DEFAULT_TENANT_ID)
- `local_business_id`: NULL
- `sitemap_curation_status`: "New"
- `sitemap_analysis_status`: NULL

### Test Case 2: Domain Submission with Auto-Queue

```bash
curl -X POST http://localhost:8000/api/v3/domains/direct-submit \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -d '{
    "domains": [
      "autoqueue-test.com"
    ],
    "auto_queue": true
  }'
```

**Expected Response:**
```json
{
  "submitted_count": 1,
  "domain_ids": ["<uuid>"],
  "auto_queued": true
}
```

**Verification SQL:**
```sql
SELECT domain, sitemap_curation_status, sitemap_analysis_status
FROM domains
WHERE domain = 'autoqueue-test.com';
```

**Expected Database State:**
- `sitemap_curation_status`: "Selected"
- `sitemap_analysis_status`: "Queued"

### Test Case 3: Duplicate Domain Detection

```bash
# Submit same domain again
curl -X POST http://localhost:8000/api/v3/domains/direct-submit \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -d '{
    "domains": [
      "example.com"
    ],
    "auto_queue": false
  }'
```

**Expected Response:**
- HTTP 409 Conflict
```json
{
  "detail": "Domain already exists: example.com"
}
```

### Test Case 4: Domain Normalization

```bash
# Test various domain formats
curl -X POST http://localhost:8000/api/v3/domains/direct-submit \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -d '{
    "domains": [
      "https://www.normalized-test.com",
      "HTTP://UPPERCASE.COM",
      "  whitespace-test.com  "
    ],
    "auto_queue": false
  }'
```

**Expected Response:**
- All domains normalized (lowercase, trimmed, protocol removed)

**Verification SQL:**
```sql
SELECT domain FROM domains
WHERE domain IN ('normalized-test.com', 'uppercase.com', 'whitespace-test.com');
```

### Test Case 5: Validation Errors

```bash
# Test empty domain list
curl -X POST http://localhost:8000/api/v3/domains/direct-submit \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -d '{
    "domains": [],
    "auto_queue": false
  }'

# Test exceeding max limit (100)
curl -X POST http://localhost:8000/api/v3/domains/direct-submit \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -d "{
    \"domains\": [$(python3 -c 'print(",".join([f"\"domain{i}.com\"" for i in range(101)]))')],
    \"auto_queue\": false
  }"

# Test invalid domain format
curl -X POST http://localhost:8000/api/v3/domains/direct-submit \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -d '{
    "domains": ["not a valid domain!@#"],
    "auto_queue": false
  }'
```

**Expected Response:**
- HTTP 422 Unprocessable Entity for all three
- Validation error messages in response

---

## Phase 3: Test WO-009 (Direct Page Submission)

### Test Case 1: Basic Page Submission (auto_queue=false)

```bash
curl -X POST http://localhost:8000/api/v3/pages/direct-submit \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -d '{
    "urls": [
      "https://example.com/contact",
      "https://example.com/about"
    ],
    "auto_queue": false,
    "priority_level": 5
  }'
```

**Expected Response:**
```json
{
  "submitted_count": 2,
  "page_ids": ["<uuid1>", "<uuid2>"],
  "auto_queued": false
}
```

**Verification SQL:**
```sql
SELECT
  p.id, p.url, p.domain_id, p.sitemap_file_id,
  p.page_curation_status, p.page_processing_status,
  p.priority_level, p.user_id,
  d.domain
FROM pages p
JOIN domains d ON p.domain_id = d.id
WHERE p.url IN (
  'https://example.com/contact',
  'https://example.com/about'
)
ORDER BY p.created_at DESC;
```

**Expected Database State:**
- `url`: Full URL as submitted
- `domain_id`: NOT NULL (should reference existing or new 'example.com' domain)
- `sitemap_file_id`: NULL
- `page_curation_status`: "New"
- `page_processing_status`: NULL
- `priority_level`: 5
- `user_id`: Should match JWT token's user_id
- `page_category`: NULL
- `category_confidence`: NULL
- `depth`: NULL

### Test Case 2: Page Submission with Auto-Queue

```bash
curl -X POST http://localhost:8000/api/v3/pages/direct-submit \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -d '{
    "urls": [
      "https://testsite.org/services"
    ],
    "auto_queue": true,
    "priority_level": 1
  }'
```

**Expected Response:**
```json
{
  "submitted_count": 1,
  "page_ids": ["<uuid>"],
  "auto_queued": true
}
```

**Verification SQL:**
```sql
SELECT url, page_curation_status, page_processing_status, priority_level
FROM pages
WHERE url = 'https://testsite.org/services';
```

**Expected Database State:**
- `page_curation_status`: "Selected"
- `page_processing_status`: "Queued"
- `priority_level`: 1

### Test Case 3: Domain Auto-Creation

```bash
# Submit page for a new domain that doesn't exist yet
curl -X POST http://localhost:8000/api/v3/pages/direct-submit \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -d '{
    "urls": [
      "https://www.brand-new-domain-12345.com/page"
    ],
    "auto_queue": false,
    "priority_level": 5
  }'
```

**Verification SQL:**
```sql
-- Verify domain was auto-created
SELECT id, domain, tenant_id, local_business_id,
       sitemap_curation_status, sitemap_analysis_status
FROM domains
WHERE domain = 'brand-new-domain-12345.com';

-- Verify page references the auto-created domain
SELECT p.url, p.domain_id, d.domain
FROM pages p
JOIN domains d ON p.domain_id = d.id
WHERE p.url = 'https://www.brand-new-domain-12345.com/page';
```

**Expected Database State:**
- Domain "brand-new-domain-12345.com" exists
- Domain has `tenant_id` = DEFAULT_TENANT_ID
- Domain has `local_business_id` = NULL
- Page's `domain_id` matches the auto-created domain's ID

### Test Case 4: Duplicate Page Detection

```bash
curl -X POST http://localhost:8000/api/v3/pages/direct-submit \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -d '{
    "urls": [
      "https://example.com/contact"
    ],
    "auto_queue": false,
    "priority_level": 5
  }'
```

**Expected Response:**
- HTTP 409 Conflict
```json
{
  "detail": "Page already exists: https://example.com/contact (ID: <uuid>)"
}
```

### Test Case 5: Domain Extraction from Various URLs

```bash
curl -X POST http://localhost:8000/api/v3/pages/direct-submit \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -d '{
    "urls": [
      "https://www.subdomain.example.com/page1",
      "https://subdomain.example.com/page2",
      "http://another-domain.co.uk/contact?param=value#anchor"
    ],
    "auto_queue": false,
    "priority_level": 5
  }'
```

**Verification SQL:**
```sql
-- Check that domains were extracted correctly
SELECT DISTINCT d.domain, COUNT(p.id) as page_count
FROM pages p
JOIN domains d ON p.domain_id = d.id
WHERE p.url LIKE '%subdomain.example.com%'
   OR p.url LIKE '%another-domain.co.uk%'
GROUP BY d.domain;
```

**Expected:**
- Domain "subdomain.example.com" with 2 pages
- Domain "another-domain.co.uk" with 1 page
- No "www." prefix in domain names

---

## Phase 4: Test WO-011 (Direct Sitemap Submission)

### Test Case 1: Basic Sitemap Submission (auto_import=false)

```bash
curl -X POST http://localhost:8000/api/v3/sitemaps/direct-submit \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -d '{
    "sitemap_urls": [
      "https://example.com/sitemap.xml",
      "https://testsite.org/sitemap_index.xml"
    ],
    "auto_import": false
  }'
```

**Expected Response:**
```json
{
  "submitted_count": 2,
  "sitemap_ids": ["<uuid1>", "<uuid2>"],
  "auto_queued": false
}
```

**Verification SQL:**
```sql
SELECT
  sf.id, sf.url, sf.domain_id, sf.sitemap_type,
  sf.deep_scrape_curation_status, sf.sitemap_import_status,
  sf.url_count, sf.last_modified, sf.file_size,
  d.domain
FROM sitemap_files sf
JOIN domains d ON sf.domain_id = d.id
WHERE sf.url IN (
  'https://example.com/sitemap.xml',
  'https://testsite.org/sitemap_index.xml'
)
ORDER BY sf.created_at DESC;
```

**Expected Database State:**
- `url`: Full sitemap URL as submitted
- `domain_id`: NOT NULL (should reference existing or new domain)
- `sitemap_type`: "STANDARD"
- `deep_scrape_curation_status`: "New"
- `sitemap_import_status`: NULL
- `url_count`: NULL (populated after import)
- `last_modified`: NULL (populated after import)
- `file_size`: NULL (populated after import)
- `user_id`: Should match JWT token's user_id

### Test Case 2: Sitemap Submission with Auto-Import

```bash
curl -X POST http://localhost:8000/api/v3/sitemaps/direct-submit \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -d '{
    "sitemap_urls": [
      "https://auto-import-test.com/sitemap.xml"
    ],
    "auto_import": true
  }'
```

**Expected Response:**
```json
{
  "submitted_count": 1,
  "sitemap_ids": ["<uuid>"],
  "auto_queued": true
}
```

**Verification SQL:**
```sql
SELECT url, deep_scrape_curation_status, sitemap_import_status, sitemap_type
FROM sitemap_files
WHERE url = 'https://auto-import-test.com/sitemap.xml';
```

**Expected Database State:**
- `deep_scrape_curation_status`: "Selected"
- `sitemap_import_status`: "Queued"
- `sitemap_type`: "STANDARD"

### Test Case 3: Domain Auto-Creation for Sitemaps

```bash
curl -X POST http://localhost:8000/api/v3/sitemaps/direct-submit \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -d '{
    "sitemap_urls": [
      "https://www.new-sitemap-domain-99999.com/sitemap.xml"
    ],
    "auto_import": false
  }'
```

**Verification SQL:**
```sql
-- Verify domain was auto-created
SELECT id, domain, tenant_id, local_business_id
FROM domains
WHERE domain = 'new-sitemap-domain-99999.com';

-- Verify sitemap references the domain
SELECT sf.url, sf.domain_id, d.domain, sf.sitemap_type
FROM sitemap_files sf
JOIN domains d ON sf.domain_id = d.id
WHERE sf.url = 'https://www.new-sitemap-domain-99999.com/sitemap.xml';
```

**Expected Database State:**
- Domain "new-sitemap-domain-99999.com" exists (www. removed)
- Domain has `tenant_id` = DEFAULT_TENANT_ID
- Domain has `local_business_id` = NULL
- Sitemap's `domain_id` matches the auto-created domain's ID
- Sitemap's `sitemap_type` = "STANDARD"

### Test Case 4: Duplicate Sitemap Detection

```bash
curl -X POST http://localhost:8000/api/v3/sitemaps/direct-submit \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -d '{
    "sitemap_urls": [
      "https://example.com/sitemap.xml"
    ],
    "auto_import": false
  }'
```

**Expected Response:**
- HTTP 409 Conflict
```json
{
  "detail": "Sitemap already exists: https://example.com/sitemap.xml (ID: <uuid>)"
}
```

### Test Case 5: Sitemap URL Validation

```bash
# Test valid sitemap formats
curl -X POST http://localhost:8000/api/v3/sitemaps/direct-submit \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -d '{
    "sitemap_urls": [
      "https://example.com/sitemap.xml",
      "https://example.com/sitemaps/products.xml",
      "https://example.com/sitemap_index.xml",
      "https://example.com/custom-sitemap.xml"
    ],
    "auto_import": false
  }'

# Test invalid sitemap URL (should fail validation)
curl -X POST http://localhost:8000/api/v3/sitemaps/direct-submit \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -d '{
    "sitemap_urls": [
      "https://example.com/not-a-sitemap.html"
    ],
    "auto_import": false
  }'
```

**Expected:**
- First request: Success (all valid sitemap URLs)
- Second request: HTTP 422 Unprocessable Entity (invalid sitemap format)

---

## Phase 5: Integration Tests

### Test Case 1: End-to-End Workflow (Domain → Sitemap → Pages)

```bash
# Step 1: Submit a domain
curl -X POST http://localhost:8000/api/v3/domains/direct-submit \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -d '{
    "domains": ["integration-test.com"],
    "auto_queue": false
  }'

# Step 2: Submit sitemaps for that domain
curl -X POST http://localhost:8000/api/v3/sitemaps/direct-submit \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -d '{
    "sitemap_urls": [
      "https://integration-test.com/sitemap.xml"
    ],
    "auto_import": false
  }'

# Step 3: Submit pages for that domain
curl -X POST http://localhost:8000/api/v3/pages/direct-submit \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -d '{
    "urls": [
      "https://integration-test.com/contact",
      "https://integration-test.com/about"
    ],
    "auto_queue": false,
    "priority_level": 5
  }'
```

**Verification SQL:**
```sql
-- Check complete data hierarchy
SELECT
  d.domain,
  d.sitemap_curation_status as domain_curation,
  COUNT(DISTINCT sf.id) as sitemap_count,
  COUNT(DISTINCT p.id) as page_count
FROM domains d
LEFT JOIN sitemap_files sf ON d.id = sf.domain_id
LEFT JOIN pages p ON d.id = p.domain_id
WHERE d.domain = 'integration-test.com'
GROUP BY d.id, d.domain, d.sitemap_curation_status;
```

**Expected:**
- 1 domain: "integration-test.com"
- 1 sitemap linked to domain
- 2 pages linked to domain
- All records have correct tenant_id

### Test Case 2: Mixed Auto-Queue Scenarios

```bash
# Submit pages with mixed auto_queue settings
curl -X POST http://localhost:8000/api/v3/pages/direct-submit \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -d '{
    "urls": [
      "https://mixed-test.com/page1"
    ],
    "auto_queue": true,
    "priority_level": 1
  }'

curl -X POST http://localhost:8000/api/v3/pages/direct-submit \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -d '{
    "urls": [
      "https://mixed-test.com/page2"
    ],
    "auto_queue": false,
    "priority_level": 5
  }'
```

**Verification SQL:**
```sql
SELECT
  url,
  page_curation_status,
  page_processing_status,
  priority_level
FROM pages
WHERE url LIKE '%mixed-test.com%'
ORDER BY url;
```

**Expected:**
- page1: curation="Selected", processing="Queued", priority=1
- page2: curation="New", processing=NULL, priority=5

---

## Phase 6: Error Handling Tests

### Test Case 1: Unauthenticated Request

```bash
# Attempt request without JWT token
curl -X POST http://localhost:8000/api/v3/domains/direct-submit \
  -H "Content-Type: application/json" \
  -d '{
    "domains": ["test.com"],
    "auto_queue": false
  }'
```

**Expected Response:**
- HTTP 401 Unauthorized
```json
{
  "detail": "Not authenticated"
}
```

### Test Case 2: Invalid JSON

```bash
curl -X POST http://localhost:8000/api/v3/domains/direct-submit \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -d '{invalid json}'
```

**Expected Response:**
- HTTP 422 Unprocessable Entity
- JSON decode error message

### Test Case 3: Missing Required Fields

```bash
curl -X POST http://localhost:8000/api/v3/pages/direct-submit \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -d '{
    "auto_queue": true
  }'
```

**Expected Response:**
- HTTP 422 Unprocessable Entity
- Error indicating "urls" field is required

---

## Phase 7: Database Integrity Checks

### Constraint Verification

```sql
-- Verify ALL pages have domain_id (nullable=False check)
SELECT COUNT(*) as pages_without_domain
FROM pages
WHERE domain_id IS NULL;
-- Expected: 0

-- Verify ALL sitemaps have domain_id (nullable=False check)
SELECT COUNT(*) as sitemaps_without_domain
FROM sitemap_files
WHERE domain_id IS NULL;
-- Expected: 0

-- Verify ALL sitemaps have sitemap_type (nullable=False check)
SELECT COUNT(*) as sitemaps_without_type
FROM sitemap_files
WHERE sitemap_type IS NULL;
-- Expected: 0

-- Verify ALL auto-created domains have tenant_id
SELECT COUNT(*) as domains_without_tenant
FROM domains
WHERE tenant_id IS NULL
  AND local_business_id IS NULL;
-- Expected: 0

-- Verify tenant_id matches DEFAULT_TENANT_ID for auto-created domains
SELECT COUNT(*) as incorrect_tenant_id
FROM domains
WHERE local_business_id IS NULL
  AND tenant_id != '550e8400-e29b-41d4-a716-446655440000'::uuid;
-- Expected: 0
```

### Foreign Key Integrity

```sql
-- Verify all pages reference valid domains
SELECT COUNT(*) as orphaned_pages
FROM pages p
LEFT JOIN domains d ON p.domain_id = d.id
WHERE d.id IS NULL;
-- Expected: 0

-- Verify all sitemaps reference valid domains
SELECT COUNT(*) as orphaned_sitemaps
FROM sitemap_files sf
LEFT JOIN domains d ON sf.domain_id = d.id
WHERE d.id IS NULL;
-- Expected: 0
```

### ENUM Value Verification

```sql
-- Check page curation status values
SELECT DISTINCT page_curation_status
FROM pages
ORDER BY page_curation_status;
-- Expected: Only "New", "Selected", "Rejected", etc.

-- Check page processing status values
SELECT DISTINCT page_processing_status
FROM pages
WHERE page_processing_status IS NOT NULL
ORDER BY page_processing_status;
-- Expected: Only "Queued", "Processing", "Complete", "Error"

-- Check sitemap curation status values
SELECT DISTINCT deep_scrape_curation_status
FROM sitemap_files
ORDER BY deep_scrape_curation_status;
-- Expected: Only valid SitemapImportCurationStatusEnum values

-- Check sitemap processing status values
SELECT DISTINCT sitemap_import_status
FROM sitemap_files
WHERE sitemap_import_status IS NOT NULL
ORDER BY sitemap_import_status;
-- Expected: Only valid SitemapImportProcessStatusEnum values
```

---

## Phase 8: Cleanup

### Remove Test Data

```sql
-- Delete test pages
DELETE FROM pages
WHERE url LIKE '%example.com%'
   OR url LIKE '%testsite.org%'
   OR url LIKE '%test.com%'
   OR url LIKE '%integration-test.com%'
   OR url LIKE '%mixed-test.com%'
   OR url LIKE '%brand-new-domain%'
   OR url LIKE '%auto%test%'
   OR url LIKE '%subdomain.example.com%'
   OR url LIKE '%another-domain.co.uk%';

-- Delete test sitemaps
DELETE FROM sitemap_files
WHERE url LIKE '%example.com%'
   OR url LIKE '%testsite.org%'
   OR url LIKE '%test.com%'
   OR url LIKE '%integration-test.com%'
   OR url LIKE '%auto-import-test%'
   OR url LIKE '%new-sitemap-domain%';

-- Delete auto-created test domains (only those without local_business_id)
DELETE FROM domains
WHERE local_business_id IS NULL
  AND (
    domain LIKE '%example.com%'
    OR domain LIKE '%testsite.org%'
    OR domain LIKE '%test.com%'
    OR domain LIKE '%integration-test.com%'
    OR domain LIKE '%auto%test%'
    OR domain LIKE '%brand-new-domain%'
    OR domain LIKE '%normalized-test%'
    OR domain LIKE '%uppercase%'
    OR domain LIKE '%whitespace-test%'
    OR domain LIKE '%subdomain.example.com%'
    OR domain LIKE '%another-domain.co.uk%'
    OR domain LIKE '%new-sitemap-domain%'
    OR domain LIKE '%mixed-test%'
  );
```

---

## Test Results Checklist

Use this checklist to track test completion:

### WO-010 (Direct Domain Submission)
- [ ] Basic submission works (auto_queue=false)
- [ ] Auto-queue submission works (auto_queue=true)
- [ ] Duplicate detection works (409 Conflict)
- [ ] Domain normalization works (lowercase, trim, no protocol)
- [ ] Validation errors work (empty list, max limit, invalid format)
- [ ] Tenant ID correctly set to DEFAULT_TENANT_ID
- [ ] Database constraints satisfied (no NULL violations)

### WO-009 (Direct Page Submission)
- [ ] Basic submission works (auto_queue=false)
- [ ] Auto-queue submission works (auto_queue=true)
- [ ] Domain auto-creation works
- [ ] Duplicate detection works (409 Conflict)
- [ ] Domain extraction from URLs works (www. removal)
- [ ] Priority level setting works
- [ ] Dual-status pattern correct (curation + processing)
- [ ] domain_id is NEVER NULL
- [ ] sitemap_file_id is NULL for direct submissions
- [ ] Tenant ID correctly set on auto-created domains

### WO-011 (Direct Sitemap Submission)
- [ ] Basic submission works (auto_import=false)
- [ ] Auto-import submission works (auto_import=true)
- [ ] Domain auto-creation works
- [ ] Duplicate detection works (409 Conflict)
- [ ] Sitemap URL validation works (.xml requirement)
- [ ] sitemap_type correctly set to "STANDARD"
- [ ] Dual-status pattern correct (deep_scrape_curation + sitemap_import)
- [ ] domain_id is NEVER NULL
- [ ] sitemap_type is NEVER NULL
- [ ] Tenant ID correctly set on auto-created domains

### Integration & Error Handling
- [ ] End-to-end workflow works (domain → sitemap → pages)
- [ ] Mixed auto-queue scenarios work correctly
- [ ] Unauthenticated requests properly rejected
- [ ] Invalid JSON properly rejected
- [ ] Missing required fields properly rejected
- [ ] Database integrity constraints all satisfied
- [ ] Foreign key relationships correct
- [ ] ENUM values all valid

---

## Troubleshooting

### Application Won't Start

```bash
# Check for port conflicts
lsof -i :8000

# Check Docker logs
docker compose logs app --tail=100

# Rebuild and restart
docker compose down
docker compose build --no-cache
docker compose up -d
```

### Authentication Issues

```bash
# Check if app is in debug mode (might bypass auth)
docker compose logs app | grep -i debug

# Verify JWT secret is consistent
docker compose exec app env | grep JWT_SECRET_KEY
cat .env | grep JWT_SECRET_KEY
```

### Database Connection Issues

```bash
# Check database is running
docker compose ps db

# Test database connection
docker compose exec db psql -U postgres -d scrapersky -c "SELECT 1;"

# Check connection string
docker compose logs app | grep -i "database"
```

### Import Errors

```bash
# Check for Python import errors
docker compose logs app | grep -i "importerror\|modulenotfounderror"

# Verify files exist
docker compose exec app ls -la src/routers/v3/
docker compose exec app ls -la src/schemas/
```

---

## Success Criteria

✅ **All tests pass if:**

1. All 3 endpoints are accessible via HTTP POST
2. Authentication works correctly (401 for missing token)
3. Validation works (422 for invalid data)
4. Duplicate detection works (409 for existing records)
5. Domain auto-creation works (new domains created with correct tenant_id)
6. Dual-status pattern works correctly
7. Auto-queue/auto-import flags work correctly
8. Database constraints satisfied (no NULL violations)
9. Foreign key relationships correct
10. ENUM values are valid
11. No errors in application logs
12. All verification SQL queries return expected results

---

## Reporting Results

After completing all tests, create a summary document with:

1. **Environment Details:**
   - Docker version
   - Python version
   - Database version
   - Git commit hash

2. **Test Results:**
   - Total tests run
   - Passed
   - Failed (with details)

3. **Issues Found:**
   - Description
   - Steps to reproduce
   - Severity (Critical, High, Medium, Low)

4. **Database State:**
   - Number of test domains created
   - Number of test pages created
   - Number of test sitemaps created
   - Constraint violations (should be 0)

5. **Recommendations:**
   - Any bugs to fix
   - Performance observations
   - Suggested improvements

---

**End of Testing Instructions**
