# INCIDENT-2025-11-17-authentication-failure

## Metadata
- **Date:** November 17, 2025 12:30 AM
- **Severity:** HIGH
- **Duration:** ~30 minutes
- **Workflows Affected:** WF4
- **Status:** Resolved
- **Fixed In:** Commits 8604a37, d9e4fc2, 1ffa371

---

## Symptoms

Error message: "invalid authentication submitted"

**Context:**
- Domain sitemap submission failing
- Specifically for `jenkinseyecare.com`
- After WO-001/WO-002 security fixes deployed

---

## Root Cause

**Dev bypass token restricted to development only**

WO-001/WO-002 security fixes restricted `DEV_TOKEN` ("scraper_sky_2024") to development environment only. Adapter service was using this token for internal HTTP calls in production.

**Code (BEFORE):**
```python
api_key = settings.DEV_TOKEN  # "scraper_sky_2024"
headers = {'Authorization': f'Bearer {api_key}'}
response = await client.post(scan_endpoint, headers=headers)
```

---

## Investigation & Fixes

### Attempt 1: Use Service Role Key (Commit 8604a37)
```python
api_key = settings.SUPABASE_SERVICE_ROLE_KEY  # Wrong case!
```
**Result:** AttributeError - wrong case

### Attempt 2: Fix Case (Commit d9e4fc2)
```python
api_key = settings.supabase_service_role_key  # Correct case
```
**Result:** 401 Unauthorized - service role key not valid for JWT endpoint

### Attempt 3: Remove HTTP Calls (Commit 1ffa371)
```python
# Remove HTTP call entirely
# Call job_service.create() directly
job = await job_service.create(session, job_data)
```
**Result:** Success - but exposed missing background trigger (next incident)

---

## Lessons Learned

1. **Separate dev and production auth** - Dev tokens should never work in production
2. **Service role keys ≠ JWT tokens** - Different authentication methods
3. **Internal calls shouldn't use HTTP** - Direct service calls better

---

## Related Incidents

- **[INCIDENT-2025-11-17-http-service-calls](./2025-11-17-http-service-calls.md)** - Led to this fix
- **[INCIDENT-2025-11-17-sitemap-jobs-not-processing](./2025-11-17-sitemap-jobs-not-processing.md)** - Exposed by this fix

---

**Status:** Resolved. Security fix working as intended. Adapter refactored to not need authentication.
