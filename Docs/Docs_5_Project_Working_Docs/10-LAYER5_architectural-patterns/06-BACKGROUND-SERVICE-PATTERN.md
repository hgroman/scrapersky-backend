# Background Service Architectural Pattern

## Purpose
Defines the canonical formula for implementing a new background service in ScraperSky. Ensures all services are robust, auditable, and consistent.

---

## 1. Pattern Overview
A background service is a scheduled process that:
- Monitors a specific field (usually an ENUM status) in a database table.
- Selects records matching a target value (e.g., `Queued`, `Pending`).
- Processes each record (e.g., sends data to an endpoint, transforms data).
- Updates the status to reflect progress (`Processing`, `Completed`, `Error`).
- Runs on a fixed interval, batch size, and concurrency, all controlled by environment variables.

---

## 2. Required Components

### a. Job Function
- Async function (e.g., `async def process_pending_<entity>(limit: int = 10)`)
- Acquires a DB session: `async with get_background_session() as session`
- Queries for target records using `.with_for_update(skip_locked=True)`
- Processes each record in a batch (atomic or per-item transaction)
- Updates status using authoritative ENUM values
- Handles and logs errors robustly

### b. Scheduler Registration
- Registers job with the shared `AsyncIOScheduler` instance
- Uses `scheduler.add_job()` with:
  - Job function
  - Interval (from env var)
  - Batch size (from env var)
  - Max instances, misfire grace (from env vars)

### c. Configuration
- All timing, batch, and concurrency parameters must be environment-driven
- Reference canonical env vars in `docker-compose.yml`

### d. ENUMs and Status Management
- Only use ENUM values defined in the authoritative ENUM section of the architecture doc
- Document which ENUM and status values are monitored and set

### e. Observability
- Log job start, end, errors, and diagnostic info
- Optionally write diagnostic logs to file
- Expose manual trigger endpoint for dev/test if needed

### f. Error Handling & Recovery
- On error, set status to `Error` and log details
- Optionally implement retry/backoff

---

## 3. Implementation Checklist
- [ ] Define job function with correct signature and session pattern
- [ ] Query target table for correct ENUM/status value
- [ ] Register job with shared scheduler in a `setup_<service>_scheduler` function
- [ ] Add/verify all required environment variables
- [ ] Update authoritative ENUM documentation if new statuses are introduced
- [ ] Add robust logging and error handling
- [ ] Document the service in [BACKGROUND_SERVICES_ARCHITECTURE.md](../../Docs_6_Architecture_and_Status/BACKGROUND_SERVICES_ARCHITECTURE.md)
- [ ] Add tests for job logic and error paths

---

## 4. Example Skeleton

```python
# src/services/my_new_service_scheduler.py

from src.scheduler_instance import scheduler
from src.session.async_session import get_background_session
from src.models.my_model import MyModel, MyStatusEnum
from src.config.settings import settings

async def process_pending_my_model(limit: int = settings.MY_SERVICE_BATCH_SIZE):
    async with get_background_session() as session:
        # Query for records with status == MyStatusEnum.Queued
        # Process each record, update status, handle errors

def setup_my_service_scheduler():
    scheduler.add_job(
        process_pending_my_model,
        trigger='interval',
        minutes=settings.MY_SERVICE_INTERVAL_MINUTES,
        id='process_pending_my_model',
        max_instances=settings.MY_SERVICE_MAX_INSTANCES,
        replace_existing=True,
        misfire_grace_time=1800,
    )
```

---

## 5. References

- [BACKGROUND_SERVICES_ARCHITECTURE.md](../../Docs_6_Architecture_and_Status/BACKGROUND_SERVICES_ARCHITECTURE.md)
- [docker-compose.yml](../../docker-compose.yml)
- [01-SCHEDULED-TASKS-APSCHEDULER-PATTERN.md](./01-SCHEDULED-TASKS-APSCHEDULER-PATTERN.md)

---

**This pattern is mandatory for all new background services. Attach a completed checklist to every new service PR and update as requirements evolve.**
