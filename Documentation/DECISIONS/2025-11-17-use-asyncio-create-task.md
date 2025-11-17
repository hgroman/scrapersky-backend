# DECISION-2025-11-17-use-asyncio-create-task

## Metadata
- **Date:** November 17, 2025
- **Decider:** Team (during incident response)
- **Status:** Active
- **Impact:** HIGH (affects all background job processing)

---

## Context

Jobs were being created in database but never processed. HTTP endpoints use `BackgroundTasks.add_task()` but direct service calls had no equivalent.

---

## Decision

**Use `asyncio.create_task()` to trigger background processing when creating jobs from services.**

---

## Rationale

- HTTP endpoints: `background_tasks.add_task(func, ...)`
- Service methods: `asyncio.create_task(func(...))`
- Both achieve same result: non-blocking background execution

---

## Implementation (Commit 9f091f6)

```python
# After creating job
import asyncio
asyncio.create_task(
    process_domain_with_own_session(
        job_id=job_id,
        domain=domain,
        user_id=None,
        max_urls=1000
    )
)
```

---

## Outcome

✅ **SUCCESS**

- Jobs now process immediately
- No dependency on scheduler
- Consistent with HTTP endpoint behavior

**Reference:** [PATTERNS.md](../PATTERNS.md#pattern-2-background-task-triggering)

---

## Related

- [INCIDENT-2025-11-17-sitemap-jobs-not-processing](../INCIDENTS/2025-11-17-sitemap-jobs-not-processing.md)

---

**Status:** Active. Required pattern for all job creation.
