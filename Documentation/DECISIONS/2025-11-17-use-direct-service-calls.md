# DECISION-2025-11-17-use-direct-service-calls

## Metadata
- **Date:** November 17, 2025
- **Decider:** Team (during incident response)
- **Status:** Active
- **Impact:** HIGH (affects all service communication)

---

## Context

DomainToSitemapAdapterService was making HTTP calls to internal API endpoint. This caused authentication issues and didn't trigger background processing.

---

## Decision

**Use direct service calls instead of HTTP for internal service-to-service communication.**

---

## Alternatives

1. **Fix HTTP authentication** - Make HTTP calls work
2. **Direct service calls** - Remove HTTP entirely (CHOSEN)

---

## Rationale

Direct calls are:
- Simpler (no auth needed)
- Faster (no network overhead)
- More reliable (fewer failure points)
- Transaction-aware (shared session)
- Can trigger background tasks

---

## Implementation (Commit 1ffa371)

**BEFORE:**
```python
async with httpx.AsyncClient() as client:
    response = await client.post(endpoint, json=payload, headers=headers)
```

**AFTER:**
```python
job = await job_service.create(session, job_data)
```

---

## Outcome

✅ **SUCCESS**

- Simpler code
- No authentication issues
- Pattern documented
- Applied to all services

**Reference:** [PATTERNS.md](../PATTERNS.md#pattern-1-service-communication)

---

## Related

- [INCIDENT-2025-11-17-http-service-calls](../INCIDENTS/2025-11-17-http-service-calls.md)
- [INCIDENT-2025-11-17-authentication-failure](../INCIDENTS/2025-11-17-authentication-failure.md)

---

**Status:** Active. Standard pattern for all internal service communication.
