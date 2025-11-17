# INCIDENT-2025-11-17-http-service-calls

## Metadata
- **Date:** November 17, 2025 12:30 AM - 1:00 AM
- **Severity:** MEDIUM (anti-pattern)
- **Duration:** Existed since April 2025
- **Workflows Affected:** WF4
- **Status:** Resolved
- **Fixed In:** Commit 1ffa371

---

## Symptoms

DomainToSitemapAdapterService making HTTP POST requests to internal `/api/v3/sitemap/scan` endpoint instead of calling service directly.

---

## Root Cause

**Legacy anti-pattern** - Service-to-service communication via HTTP

**Code (BEFORE):**
```python
# DON'T DO THIS
scan_endpoint = f"{INTERNAL_API_BASE_URL}/api/v3/sitemap/scan"
async with httpx.AsyncClient() as client:
    response = await client.post(
        scan_endpoint,
        json=scan_payload,
        headers=headers,
        timeout=30.0
    )
```

**Problems:**
- Network overhead
- Authentication complexity
- Can't share transaction context
- **Doesn't trigger background tasks**
- Multiple failure points

---

## The Fix (Commit 1ffa371)

**Replaced with direct service call:**
```python
# DO THIS
job_data = {...}
job = await job_service.create(session, job_data)
```

**Benefits:**
- No network overhead
- No authentication needed
- Shares transaction context
- Simpler error handling

---

## Lessons Learned

### Pattern: Service Communication
**✅ CORRECT:** Direct service calls
```python
service = SomeService()
result = await service.process(item_id, session)
```

**❌ WRONG:** HTTP calls between services
```python
async with httpx.AsyncClient() as client:
    response = await client.post("http://localhost:8000/api/...")
```

**Reference:** [PATTERNS.md](../PATTERNS.md#pattern-1-service-communication)

---

## Related Incidents

- **[INCIDENT-2025-11-17-authentication-failure](./2025-11-17-authentication-failure.md)** - Exposed this anti-pattern
- **[INCIDENT-2025-11-17-sitemap-jobs-not-processing](./2025-11-17-sitemap-jobs-not-processing.md)** - HTTP didn't trigger background tasks

---

**Status:** Resolved. Pattern documented. All services now use direct calls.
