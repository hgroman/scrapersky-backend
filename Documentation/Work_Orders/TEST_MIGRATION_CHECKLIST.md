# Migration Testing Checklist: WO-022 & WO-023
**Date:** 2025-11-20  
**Status:** Ready for Testing

---

## Pre-Test: Commit Model Changes

```bash
# Review changes
git diff src/models/

# Commit model updates
git add src/models/local_business.py
git add src/models/domain.py
git add src/models/sitemap.py
git add src/models/place.py
git commit -m "WO-022 & WO-023: Update model Column definitions to match renamed database ENUMs

- Update domain_extraction_status to use domain_extraction_status_enum
- Update sitemap_curation_status to use sitemap_curation_status_enum
- Add ForeignKey constraints to tenant_id columns
- Database migrations already applied and verified

Ref: Documentation/MIGRATION_REPORT_WO022_WO023_2025-11-20.md"
```

---

## Test 1: Application Startup ✅

### Commands

```bash
# Clean start
docker compose -f docker-compose.dev.yml down
docker compose -f docker-compose.dev.yml up --build
```

### Success Criteria

- [ ] Build completes without errors
- [ ] Application starts without ORM errors
- [ ] No `sqlalchemy.exc.ProgrammingError` in logs
- [ ] No `KeyError` about enum members in logs
- [ ] Health check passes

### Verification

```bash
# In another terminal
curl http://localhost:8000/health

# Expected: {"status": "healthy"}
```

### Logs to Watch

```bash
docker compose -f docker-compose.dev.yml logs -f scrapersky
```

**Look for:**
- ✅ "Application startup complete"
- ✅ "Uvicorn running on http://0.0.0.0:8000"
- ❌ Any errors mentioning "enum" or "type"

---

## Test 2: Router Endpoints ✅

### Test 2A: LocalBusiness Router (DomainExtractionStatusEnum)

```bash
# List local businesses
curl -X GET "http://localhost:8000/api/v1/local-businesses?limit=10" \
  -H "Authorization: Bearer scraper_sky_2024" | jq

# Expected: JSON array of businesses with domain_extraction_status field
```

**Success Criteria:**
- [ ] Returns 200 OK
- [ ] JSON response with businesses
- [ ] `domain_extraction_status` field present
- [ ] No enum-related errors

---

### Test 2B: Domains Router (SitemapCurationStatusEnum)

```bash
# List domains
curl -X GET "http://localhost:8000/api/v1/domains?limit=10" \
  -H "Authorization: Bearer scraper_sky_2024" | jq

# Expected: JSON array of domains with sitemap_curation_status field
```

**Success Criteria:**
- [ ] Returns 200 OK
- [ ] JSON response with domains
- [ ] `sitemap_curation_status` field present
- [ ] No enum-related errors

---

### Test 2C: Filter by Status (Critical Router Pattern)

```bash
# Filter domains by sitemap_curation_status
curl -X GET "http://localhost:8000/api/v1/domains?sitemap_curation_status=Selected&limit=10" \
  -H "Authorization: Bearer scraper_sky_2024" | jq

# Expected: Only domains with status "Selected"
```

**Success Criteria:**
- [ ] Returns 200 OK
- [ ] All returned domains have `sitemap_curation_status: "Selected"`
- [ ] No enum-related errors

---

## Test 3: Status Updates ✅

### Test 3A: Single Domain Status Update

**Get a domain ID first:**
```bash
DOMAIN_ID=$(curl -s -X GET "http://localhost:8000/api/v1/domains?limit=1" \
  -H "Authorization: Bearer scraper_sky_2024" | jq -r '.[0].id')

echo "Testing with domain ID: $DOMAIN_ID"
```

**Update status:**
```bash
curl -X PATCH "http://localhost:8000/api/v1/domains/$DOMAIN_ID/curation-status" \
  -H "Authorization: Bearer scraper_sky_2024" \
  -H "Content-Type: application/json" \
  -d '{"sitemap_curation_status": "Selected"}' | jq

# Expected: Success response with updated domain
```

**Success Criteria:**
- [ ] Returns 200 OK
- [ ] Response shows `sitemap_curation_status: "Selected"`
- [ ] No enum-related errors

---

### Test 3B: Batch Status Update (Critical Router Pattern)

```bash
# Get multiple domain IDs
DOMAIN_IDS=$(curl -s -X GET "http://localhost:8000/api/v1/domains?limit=3" \
  -H "Authorization: Bearer scraper_sky_2024" | jq -r '[.[].id] | @json')

echo "Testing with domain IDs: $DOMAIN_IDS"

# Batch update
curl -X POST "http://localhost:8000/api/v1/domains/batch-update-curation-status" \
  -H "Authorization: Bearer scraper_sky_2024" \
  -H "Content-Type: application/json" \
  -d "{
    \"domain_ids\": $DOMAIN_IDS,
    \"sitemap_curation_status\": \"Maybe\"
  }" | jq

# Expected: Success response with updated count
```

**Success Criteria:**
- [ ] Returns 200 OK
- [ ] Response shows `updated_count: 3`
- [ ] No enum-related errors

---

## Test 4: Scheduler Operations ✅

### Test 4A: Check Scheduler Logs

```bash
# Watch for domain extraction scheduler activity
docker compose -f docker-compose.dev.yml logs -f scrapersky | grep -i "domain extraction"
```

**Success Criteria:**
- [ ] Scheduler runs without errors
- [ ] Processes queued items (if any)
- [ ] No enum-related errors
- [ ] Status transitions work (Queued → Processing → Completed/Error)

---

### Test 4B: Trigger Domain Extraction

```bash
# Get a local business ID
BUSINESS_ID=$(curl -s -X GET "http://localhost:8000/api/v1/local-businesses?limit=1" \
  -H "Authorization: Bearer scraper_sky_2024" | jq -r '.[0].id')

# Queue for domain extraction
curl -X POST "http://localhost:8000/api/v1/local-businesses/queue-domain-extraction" \
  -H "Authorization: Bearer scraper_sky_2024" \
  -H "Content-Type: application/json" \
  -d "{\"business_ids\": [\"$BUSINESS_ID\"]}" | jq

# Watch scheduler process it
docker compose -f docker-compose.dev.yml logs -f scrapersky | grep -i "domain extraction"
```

**Success Criteria:**
- [ ] Business queued successfully
- [ ] Scheduler picks it up
- [ ] Status transitions: Queued → Processing → Completed/Error
- [ ] No enum-related errors

---

## Test 5: Automated Test Suite ✅

```bash
# Run the migration safety test suite
pytest tests/test_migration_safety.py -v

# Expected: All tests pass
```

**Success Criteria:**
- [ ] All enum rename tests pass
- [ ] All FK constraint tests pass
- [ ] All router pattern tests pass
- [ ] All service pattern tests pass
- [ ] All database verification tests pass

---

## Test 6: Database Verification ✅

### Connect to Database

```bash
# Get database connection string from .env
# Then connect with psql or use Supabase MCP
```

### Verification Queries

```sql
-- 1. Verify enum types exist
SELECT typname, typtype 
FROM pg_type 
WHERE typname IN (
    'domain_extraction_status_enum',
    'sitemap_curation_status_enum'
)
ORDER BY typname;

-- Expected: 2 rows (both enum types exist)

-- 2. Verify old enum types are gone
SELECT typname 
FROM pg_type 
WHERE typname IN (
    'domainextractionstatusenum',
    'sitemapcurationstatusenum'
);

-- Expected: 0 rows (old names gone)

-- 3. Verify FK constraints exist
SELECT constraint_name, table_name
FROM information_schema.table_constraints
WHERE constraint_type = 'FOREIGN KEY'
AND constraint_name IN (
    'fk_local_businesses_tenant',
    'fk_places_staging_tenant',
    'fk_sitemap_files_tenant',
    'fk_sitemap_urls_tenant'
)
ORDER BY table_name;

-- Expected: 4 rows (all FK constraints exist)

-- 4. Verify data integrity
SELECT 
    'local_businesses' as table_name,
    COUNT(*) as total_records,
    COUNT(domain_extraction_status) as with_status
FROM local_businesses
UNION ALL
SELECT 
    'domains',
    COUNT(*),
    COUNT(sitemap_curation_status)
FROM domains;

-- Expected: All counts match (no data loss)

-- 5. Verify no NULL tenant_ids
SELECT 
    'local_businesses' as table_name,
    COUNT(*) as null_tenant_ids
FROM local_businesses WHERE tenant_id IS NULL
UNION ALL
SELECT 'places_staging', COUNT(*) FROM places_staging WHERE tenant_id IS NULL
UNION ALL
SELECT 'sitemap_files', COUNT(*) FROM sitemap_files WHERE tenant_id IS NULL
UNION ALL
SELECT 'sitemap_urls', COUNT(*) FROM sitemap_urls WHERE tenant_id IS NULL;

-- Expected: All counts = 0 (no NULL tenant_ids)
```

**Success Criteria:**
- [ ] New enum types exist
- [ ] Old enum types gone
- [ ] All FK constraints exist
- [ ] Data integrity maintained
- [ ] No NULL tenant_ids

---

## Test 7: Integration Test (End-to-End) ✅

### Scenario: Complete Workflow

```bash
# 1. Create a local business
curl -X POST "http://localhost:8000/api/v1/local-businesses" \
  -H "Authorization: Bearer scraper_sky_2024" \
  -H "Content-Type: application/json" \
  -d '{
    "business_name": "Test Migration Business",
    "website_url": "https://test-migration.com"
  }' | jq

# 2. Queue for domain extraction
# (Use business_id from step 1)
curl -X POST "http://localhost:8000/api/v1/local-businesses/queue-domain-extraction" \
  -H "Authorization: Bearer scraper_sky_2024" \
  -H "Content-Type: application/json" \
  -d '{"business_ids": ["<business-id>"]}' | jq

# 3. Wait for scheduler to process (watch logs)
docker compose -f docker-compose.dev.yml logs -f scrapersky | grep "domain extraction"

# 4. Verify domain was created
curl -X GET "http://localhost:8000/api/v1/domains?domain=test-migration.com" \
  -H "Authorization: Bearer scraper_sky_2024" | jq

# 5. Update domain curation status
# (Use domain_id from step 4)
curl -X PATCH "http://localhost:8000/api/v1/domains/<domain-id>/curation-status" \
  -H "Authorization: Bearer scraper_sky_2024" \
  -H "Content-Type: application/json" \
  -d '{"sitemap_curation_status": "Selected"}' | jq
```

**Success Criteria:**
- [ ] Business created successfully
- [ ] Domain extraction queued
- [ ] Scheduler processes job
- [ ] Domain created with correct status
- [ ] Status update works
- [ ] No enum-related errors at any step

---

## Test 8: Error Handling ✅

### Test Invalid Enum Values

```bash
# Try to set invalid status (should fail gracefully)
curl -X PATCH "http://localhost:8000/api/v1/domains/<domain-id>/curation-status" \
  -H "Authorization: Bearer scraper_sky_2024" \
  -H "Content-Type: application/json" \
  -d '{"sitemap_curation_status": "InvalidStatus"}' | jq

# Expected: 422 Unprocessable Entity with clear error message
```

**Success Criteria:**
- [ ] Returns 422 error
- [ ] Error message is clear
- [ ] No server crash
- [ ] No enum-related exceptions

---

## Final Checklist

### Pre-Deployment

- [ ] All model changes committed
- [ ] Application starts successfully
- [ ] All router endpoints work
- [ ] Status updates work (single and batch)
- [ ] Schedulers run without errors
- [ ] Automated tests pass
- [ ] Database verification queries pass
- [ ] End-to-end integration test passes
- [ ] Error handling works correctly

### Documentation

- [ ] Migration report reviewed: `Documentation/MIGRATION_REPORT_WO022_WO023_2025-11-20.md`
- [ ] Safety verification reviewed: `Documentation/ROUTER_SERVICE_SAFETY_VERIFICATION.md`
- [ ] Test results documented

### Rollback Readiness

- [ ] Rollback SQL prepared
- [ ] Rollback procedure tested (optional, in staging)
- [ ] Team notified of deployment window

---

## If Any Test Fails

### Immediate Actions

1. **STOP** - Do not proceed to next test
2. **Document** - Capture error message and logs
3. **Analyze** - Determine if it's migration-related or pre-existing
4. **Decide** - Rollback or fix forward?

### Rollback Decision Tree

**If error is migration-related:**
- Execute database rollback SQL
- Revert model changes: `git restore src/models/`
- Restart application
- Verify rollback successful

**If error is pre-existing:**
- Document as separate issue
- Continue testing (migration is not the cause)

---

## Success Criteria Summary

✅ **Application Startup:** No ORM errors, health check passes  
✅ **Router Endpoints:** All endpoints return data without enum errors  
✅ **Status Updates:** Single and batch updates work  
✅ **Schedulers:** Process jobs without enum errors  
✅ **Automated Tests:** All tests pass  
✅ **Database Verification:** ENUMs renamed, FKs added, data intact  
✅ **Integration Test:** End-to-end workflow completes  
✅ **Error Handling:** Invalid values handled gracefully

---

## Post-Test: Deployment

### If All Tests Pass

```bash
# Tag the release
git tag -a v1.0.0-wo022-wo023 -m "WO-022 & WO-023: Database standardization complete"
git push origin v1.0.0-wo022-wo023

# Deploy to staging (if applicable)
# Deploy to production

# Monitor logs for 24 hours
```

### Monitoring

```bash
# Watch for enum-related errors
docker compose -f docker-compose.prod.yml logs -f scrapersky | grep -i "enum\|type\|constraint"

# Check error rates
# Check scheduler success rates
# Check API response times
```

---

**Testing Started:** _____________  
**Testing Completed:** _____________  
**Tested By:** _____________  
**Result:** ☐ PASS ☐ FAIL  
**Notes:** _____________
