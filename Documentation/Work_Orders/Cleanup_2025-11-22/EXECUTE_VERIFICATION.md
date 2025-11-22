# Execute WO-022 & WO-023 Verification

**Status:** Ready to Execute  
**Date:** 2025-11-20

---

## Current State

✅ **Database Migrations:** COMPLETE (executed via Supabase MCP)
- `20251120000000_fix_enums_and_fks.sql` - Applied
- `20251120000001_fix_local_business_status_type.sql` - Applied

✅ **Model Changes:** STAGED (ready to commit)
- `src/models/local_business.py` - Updated
- `src/models/domain.py` - Updated
- `src/models/sitemap.py` - Updated
- `src/models/place.py` - Updated

✅ **Verification Script:** CREATED
- `tests/verify_wo022_wo023_comprehensive.py`

---

## Step-by-Step Execution

### Step 1: Commit Model Changes

```bash
cd /Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend

# Review changes one more time
git diff src/models/

# Commit
git add src/models/local_business.py
git add src/models/domain.py
git add src/models/sitemap.py
git add src/models/place.py

git commit -m "WO-022 & WO-023: Sync model Column definitions with database

Database migrations already applied:
- Renamed ENUMs to snake_case (domain_extraction_status_enum, sitemap_curation_status_enum)
- Added FK constraints (tenant_id -> tenants.id)
- Fixed local_businesses.status type (place_status_enum)

Model changes:
- Update Column name= parameters to match renamed database ENUM types
- Add ForeignKey constraints to tenant_id columns
- No changes to Python Enum classes or values

Migrations executed: 2025-11-20 via Supabase MCP
Verified: Zero NULL tenant_ids, all data intact
Safety: Zero breaking changes (routers/services use Python ENUMs, not DB type names)

Ref: Documentation/Work_Orders/WO-022_WO-023_VERIFICATION_PLAN.md"
```

---

### Step 2: Run Verification Script

```bash
# Ensure DATABASE_URL is set (check .env)
export DATABASE_URL="postgresql+asyncpg://..."  # Or load from .env

# Run verification
python tests/verify_wo022_wo023_comprehensive.py
```

**Expected Output:**
```
🚀 Starting Comprehensive Verification for WO-022 & WO-023...
🔹 TEST 1: Verifying LocalBusiness Status (WO-023)...
✅ TEST 1 PASSED: Successfully saved and retrieved LocalBusiness with status 'Maybe'.
🔹 TEST 2: Verifying Domain Sitemap Curation Status (WO-022)...
✅ TEST 2 PASSED: Successfully saved Domain with SitemapCurationStatusEnum.
🔹 TEST 3: Verifying Foreign Key Constraint Enforcement...
✅ TEST 3 PASSED: Database correctly blocked invalid tenant_id (IntegrityError).
🧹 Cleaning up test data...
🎉 ALL TESTS PASSED SUCCESSFULLY!
```

**Exit Code:** 0 (success)

---

### Step 3: Start Application (Docker)

```bash
# Clean start
docker compose -f docker-compose.dev.yml down
docker compose -f docker-compose.dev.yml up --build
```

**Watch for:**
- ✅ Build completes without errors
- ✅ Application starts without ORM errors
- ✅ No `sqlalchemy.exc.ProgrammingError` in logs
- ✅ Health check passes

---

### Step 4: Test Health Endpoint

```bash
# In another terminal
curl http://localhost:8000/health

# Expected: {"status":"healthy"}
```

---

### Step 5: Test Router Endpoints

```bash
# Test LocalBusiness router (uses DomainExtractionStatusEnum)
curl -X GET "http://localhost:8000/api/v1/local-businesses?limit=5" \
  -H "Authorization: Bearer scraper_sky_2024" | jq

# Test Domains router (uses SitemapCurationStatusEnum)
curl -X GET "http://localhost:8000/api/v1/domains?limit=5" \
  -H "Authorization: Bearer scraper_sky_2024" | jq
```

**Expected:**
- ✅ Both return 200 OK
- ✅ JSON data with status fields
- ✅ No enum-related errors

---

### Step 6: Monitor Logs

```bash
# Watch for any enum-related errors
docker compose -f docker-compose.dev.yml logs -f scrapersky | grep -i "enum\|error\|type"
```

**Expected:**
- ✅ No errors
- ✅ Normal application logs
- ✅ Schedulers running (if configured)

---

## Troubleshooting

### If Verification Script Fails

**TEST 1 Fails (LocalBusiness status):**
```bash
# Check model definition
grep -A 5 "status = Column" src/models/local_business.py

# Should see: name="place_status_enum"
```

**TEST 2 Fails (Domain sitemap_curation_status):**
```bash
# Check model definition
grep -A 5 "sitemap_curation_status = Column" src/models/domain.py

# Should see: name="sitemap_curation_status_enum"
```

**TEST 3 Fails (FK not enforced):**
```bash
# Check if FK constraint exists in database
# Use Supabase MCP or psql to verify
```

---

### If Application Fails to Start

**Error: "type ... does not exist"**
```
This means the database migration didn't run.
Solution: Re-run migrations via Supabase MCP (already done, shouldn't happen)
```

**Error: "cannot find enum member"**
```
This means model Column definition doesn't match database.
Solution: Check model files, ensure name= parameter is correct
```

---

## Success Criteria

- [x] Database migrations applied
- [ ] Model changes committed
- [ ] Verification script passes (all 3 tests)
- [ ] Application starts without errors
- [ ] Health endpoint responds
- [ ] Router endpoints work
- [ ] No enum-related errors in logs

---

## Rollback (If Needed)

### Database Rollback
```sql
-- Via Supabase MCP or psql
ALTER TYPE domain_extraction_status_enum RENAME TO domainextractionstatusenum;
ALTER TYPE sitemap_curation_status_enum RENAME TO sitemapcurationstatusenum;

ALTER TABLE local_businesses DROP CONSTRAINT fk_local_businesses_tenant;
ALTER TABLE places_staging DROP CONSTRAINT fk_places_staging_tenant;
ALTER TABLE sitemap_files DROP CONSTRAINT fk_sitemap_files_tenant;
ALTER TABLE sitemap_urls DROP CONSTRAINT fk_sitemap_urls_tenant;

ALTER TABLE local_businesses ALTER COLUMN status DROP DEFAULT;
ALTER TABLE local_businesses ALTER COLUMN status TYPE sitemap_import_curation_status
    USING status::text::sitemap_import_curation_status;
ALTER TABLE local_businesses ALTER COLUMN status SET DEFAULT 'New'::sitemap_import_curation_status;
```

### Code Rollback
```bash
git restore src/models/local_business.py
git restore src/models/domain.py
git restore src/models/sitemap.py
git restore src/models/place.py
```

---

## Next Steps After Verification

1. **If all tests pass:**
   - Tag the release: `git tag -a v1.0.0-wo022-wo023 -m "Database standardization complete"`
   - Push to remote: `git push origin main --tags`
   - Deploy to staging (if applicable)
   - Monitor for 24 hours
   - Deploy to production

2. **If any test fails:**
   - Document the failure
   - Determine if migration-related or pre-existing
   - Decide: rollback or fix forward
   - Do NOT proceed to production

---

## Documentation References

- **Verification Plan:** `Documentation/Work_Orders/WO-022_WO-023_VERIFICATION_PLAN.md`
- **Migration Report:** `Documentation/Work_Orders/MIGRATION_REPORT_WO022_WO023_2025-11-20.md`
- **Safety Verification:** `Documentation/Work_Orders/ROUTER_SERVICE_SAFETY_VERIFICATION.md`
- **Test Checklist:** `TEST_MIGRATION_CHECKLIST.md`

---

**Ready to execute. Follow steps 1-6 in order.**
