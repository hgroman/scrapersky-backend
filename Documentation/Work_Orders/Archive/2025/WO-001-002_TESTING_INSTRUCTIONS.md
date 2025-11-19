# Testing Instructions: WO-001 and WO-002 Security Fixes

**Work Orders:** WO-001 (DB Portal Auth) + WO-002 (Dev Token Restriction)
**Date:** 2025-11-16
**Testing Time:** ~10 minutes
**Purpose:** Verify security fixes work correctly before production deployment

---

## Prerequisites

- Docker and docker-compose installed
- Local copy of the repository
- Terminal access
- Branch: `claude/validate-statements-fast-01MMqLehTGhadQ1wSzA4d3P8` checked out

---

## Quick Start

```bash
# 1. Checkout the branch
git checkout claude/validate-statements-fast-01MMqLehTGhadQ1wSzA4d3P8
git pull origin claude/validate-statements-fast-01MMqLehTGhadQ1wSzA4d3P8

# 2. Start in development mode
export ENV=development
docker-compose up --build

# 3. Wait for startup message:
# INFO:     Application startup complete.
# INFO:     Uvicorn running on http://0.0.0.0:8000

# 4. Open NEW terminal and run tests below
```

---

## Test Suite 1: WO-001 - DB Portal Authentication

### Test 1.1: Verify Endpoints REJECT Unauthenticated Requests

**Open a new terminal and run:**

```bash
# Test: List tables endpoint without auth (should FAIL)
curl -X GET http://localhost:8000/api/v3/db-portal/tables -v
```

**Expected Result:**
```
HTTP/1.1 401 Unauthorized
{"detail":"Not authenticated"}
```

```bash
# Test: Query endpoint without auth (MOST CRITICAL - should FAIL)
curl -X POST http://localhost:8000/api/v3/db-portal/query \
  -H "Content-Type: application/json" \
  -d '{"query": "SELECT 1 as test"}' -v
```

**Expected Result:**
```
HTTP/1.1 401 Unauthorized
{"detail":"Not authenticated"}
```

```bash
# Test: Health check without auth (should FAIL)
curl -X GET http://localhost:8000/api/v3/db-portal/health -v
```

**Expected Result:**
```
HTTP/1.1 401 Unauthorized
{"detail":"Not authenticated"}
```

**✅ PASS CRITERIA:** All 3 requests return `401 Unauthorized`

---

### Test 1.2: Verify Endpoints WORK WITH Authentication

```bash
# Test: List tables WITH bypass token (should SUCCEED)
curl -X GET http://localhost:8000/api/v3/db-portal/tables \
  -H "Authorization: Bearer scraper_sky_2024" -v
```

**Expected Result:**
```
HTTP/1.1 200 OK
[{"schema_name": "public", "table_name": "domains", ...}, ...]
```

```bash
# Test: Query endpoint WITH bypass token (should SUCCEED)
curl -X POST http://localhost:8000/api/v3/db-portal/query \
  -H "Authorization: Bearer scraper_sky_2024" \
  -H "Content-Type: application/json" \
  -d '{"query": "SELECT 1 as test"}' -v
```

**Expected Result:**
```
HTTP/1.1 200 OK
{"success":true,"columns":["test"],"rows":[{"test":1}],"row_count":1}
```

**✅ PASS CRITERIA:** Both requests return `200 OK` with data

---

### Test 1.3: Test All 7 DB Portal Endpoints

**Run complete endpoint test:**

```bash
TOKEN="scraper_sky_2024"

# 1. List tables
echo "Test 1: List tables"
curl -X GET http://localhost:8000/api/v3/db-portal/tables \
  -H "Authorization: Bearer $TOKEN"
echo -e "\n---\n"

# 2. Get table schema
echo "Test 2: Get table schema"
curl -X GET http://localhost:8000/api/v3/db-portal/tables/domains \
  -H "Authorization: Bearer $TOKEN"
echo -e "\n---\n"

# 3. Get sample data
echo "Test 3: Get sample data"
curl -X GET "http://localhost:8000/api/v3/db-portal/tables/domains/sample?limit=5" \
  -H "Authorization: Bearer $TOKEN"
echo -e "\n---\n"

# 4. Execute query
echo "Test 4: Execute query"
curl -X POST http://localhost:8000/api/v3/db-portal/query \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "SELECT COUNT(*) as total FROM domains"}'
echo -e "\n---\n"

# 5. Validate schema
echo "Test 5: Validate schema"
curl -X POST http://localhost:8000/api/v3/db-portal/tables/domains/validate \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"expected_schema": {"id": {"type": "uuid"}}}'
echo -e "\n---\n"

# 6. Generate model
echo "Test 6: Generate model"
curl -X GET http://localhost:8000/api/v3/db-portal/tables/domains/model \
  -H "Authorization: Bearer $TOKEN"
echo -e "\n---\n"

# 7. Health check
echo "Test 7: Health check"
curl -X GET http://localhost:8000/api/v3/db-portal/health \
  -H "Authorization: Bearer $TOKEN"
echo -e "\n---\n"
```

**✅ PASS CRITERIA:** All 7 endpoints return `200 OK` with data

---

## Test Suite 2: WO-002 - Dev Token Environment Restriction

### Test 2.1: Token Works in Development

```bash
# Verify bypass token works when ENV=development
curl -X GET http://localhost:8000/api/v3/domains \
  -H "Authorization: Bearer scraper_sky_2024" -v
```

**Expected Result:**
```
HTTP/1.1 200 OK
{"items": [...], "total": ...}
```

**✅ PASS CRITERIA:** Request succeeds (200 OK)

---

### Test 2.2: Token REJECTED in Production

**Stop the application** (Ctrl+C in docker-compose terminal)

**Restart with production environment:**

```bash
export ENV=production
docker-compose up
```

**Wait for startup, then test:**

```bash
# Verify bypass token is REJECTED when ENV=production
curl -X GET http://localhost:8000/api/v3/domains \
  -H "Authorization: Bearer scraper_sky_2024" -v
```

**Expected Result:**
```
HTTP/1.1 401 Unauthorized
{"detail":"Invalid authentication credentials"}
```

**Check docker-compose logs for:**
```
WARNING ... Attempted use of development bypass token in 'production' environment - REJECTED
```

**✅ PASS CRITERIA:**
- Request fails (401 Unauthorized)
- Warning appears in logs

---

### Test 2.3: Token REJECTED in Staging

**Stop the application** (Ctrl+C)

**Restart with staging environment:**

```bash
export ENV=staging
docker-compose up
```

**Wait for startup, then test:**

```bash
# Verify bypass token is REJECTED when ENV=staging
curl -X GET http://localhost:8000/api/v3/domains \
  -H "Authorization: Bearer scraper_sky_2024" -v
```

**Expected Result:**
```
HTTP/1.1 401 Unauthorized
{"detail":"Invalid authentication credentials"}
```

**Check logs for:**
```
WARNING ... Attempted use of development bypass token in 'staging' environment - REJECTED
```

**✅ PASS CRITERIA:**
- Request fails (401 Unauthorized)
- Warning appears in logs

---

## Summary Checklist

**Before declaring tests PASSED, verify ALL of these:**

### WO-001: DB Portal Authentication
- [ ] Tables endpoint rejects request without auth (401)
- [ ] Query endpoint rejects request without auth (401)
- [ ] Health endpoint rejects request without auth (401)
- [ ] Tables endpoint succeeds with auth (200)
- [ ] Query endpoint succeeds with auth (200)
- [ ] All 7 endpoints return 200 OK when authenticated

### WO-002: Dev Token Restriction
- [ ] Bypass token works in development (200)
- [ ] Bypass token rejected in production (401 + warning log)
- [ ] Bypass token rejected in staging (401 + warning log)

---

## Test Results Template

**Copy this and fill it out:**

```
Testing Date: _______________
Tester: _______________

WO-001 Results:
[ ] Test 1.1: Unauthenticated requests rejected - PASS/FAIL
[ ] Test 1.2: Authenticated requests succeed - PASS/FAIL
[ ] Test 1.3: All 7 endpoints work - PASS/FAIL

WO-002 Results:
[ ] Test 2.1: Token works in development - PASS/FAIL
[ ] Test 2.2: Token rejected in production - PASS/FAIL
[ ] Test 2.3: Token rejected in staging - PASS/FAIL

Overall Result: PASS/FAIL

Notes:
_______________________________________________
_______________________________________________
```

---

## If Tests FAIL

**DO NOT DEPLOY TO PRODUCTION**

1. Document which test(s) failed
2. Document actual vs expected results
3. Check application logs for errors
4. Report findings to development team
5. Roll back changes if necessary

---

## If ALL Tests PASS

**Security fixes are working correctly:**

✅ **WO-001:** DB Portal is now protected (CATASTROPHIC vulnerability fixed)
- No more arbitrary SQL execution
- All endpoints require authentication

✅ **WO-002:** Dev token only works in development (CRITICAL vulnerability fixed)
- Token blocked in production/staging
- Warning logs when bypass attempted

**Safe to deploy to production.**

---

## Troubleshooting

### Application Won't Start
```bash
# Check for port conflicts
docker-compose down
docker-compose up --build
```

### Can't Connect to Database
```bash
# Check environment variables in .env file
# Ensure database is running
docker-compose logs -f app
```

### Tests Return Unexpected Results
```bash
# Check which branch you're on
git branch

# Verify latest changes are pulled
git pull origin claude/validate-statements-fast-01MMqLehTGhadQ1wSzA4d3P8

# Check application logs
docker-compose logs -f app
```

### Need to Reset Everything
```bash
# Stop all containers
docker-compose down

# Remove volumes (careful - deletes data)
docker-compose down -v

# Rebuild from scratch
docker-compose up --build
```

---

## Post-Testing Cleanup

```bash
# Stop the application
docker-compose down

# Reset environment
unset ENV

# Return to main branch
git checkout main
```

---

**End of Testing Instructions**
