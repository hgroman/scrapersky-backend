# Background Service Architectural Pattern & Router Crosswalk

## Purpose
This document defines the canonical architectural pattern for background services in ScraperSky and provides a crosswalk between all background services and API routers. It is designed for maximum accessibility and auditability.

---

## 1. Background Service Architectural Pattern

**See also:** [10-architectural-patterns/06-BACKGROUND-SERVICE-PATTERN.md](../Docs_5_Project_Working_Docs/10-architectural-patterns/06-BACKGROUND-SERVICE-PATTERN.md)

### Pattern Overview
A background service is a scheduled process that:
- Monitors a specific field (usually an ENUM status) in a database table.
- Selects records matching a target value (e.g., `Queued`, `Pending`).
- Processes each record (e.g., sends data to an endpoint, transforms data).
- Updates the status to reflect progress (`Processing`, `Completed`, `Error`).
- Runs on a fixed interval, batch size, and concurrency, all controlled by environment variables.

### Required Components
- **Job Function:** Async, session-managed, robust error handling.
- **Scheduler Registration:** Shared APScheduler instance, env-driven config.
- **ENUM/Status Management:** Use only authoritative ENUMs.
- **Observability:** Logging, diagnostics, optional manual triggers.
- **Error Handling:** Status update on error, optional retry/backoff.

### Implementation Checklist
- [ ] Define job function and session pattern
- [ ] Query correct ENUM/status
- [ ] Register job with scheduler
- [ ] Env vars for timing/batch/concurrency
- [ ] ENUM doc updates
- [ ] Logging and error handling
- [ ] Document in BACKGROUND_SERVICES_ARCHITECTURE.md
- [ ] Add tests

---

## 2. Router ↔ Background Service Crosswalk

### Integration Principle
- **Background services are decoupled from API routers.** Their lifecycle is managed by the scheduler, not by HTTP endpoints.
- **Routers and background services interact only via shared models and status fields.**
- **No router directly triggers or manages background jobs** (unless explicitly documented as a manual/diagnostic endpoint).

### Summary Table
| Background Service         | Triggered By Router? | Shared Model(s)         | Manual Trigger Endpoint? |
|---------------------------|----------------------|-------------------------|-------------------------|
| Domain Scheduler          | No                   | Domain                  | (Check dev_tools.py)    |
| Sitemap Scheduler         | No                   | Sitemap, Place          | (Check dev_tools.py)    |
| Domain Sitemap Submission | No                   | Domain                  | (Check dev_tools.py)    |
| Sitemap Import Scheduler  | No                   | SitemapFile             | (Check dev_tools.py)    |

### Documentation Guidance
- In [Docs_7_Workflow_Canon/1-main_routers.md](../Docs_7_Workflow_Canon/1-main_routers.md), all routers are API-facing and do not directly manage background jobs.
- If any router exposes a manual trigger, it must be explicitly listed in both the router map and this document.
- Any new router or endpoint that interacts with background jobs must be flagged for architectural review and documentation.

---

## 3. References
- [BACKGROUND_SERVICES_ARCHITECTURE.md](./BACKGROUND_SERVICES_ARCHITECTURE.md)
- [Docs_7_Workflow_Canon/1-main_routers.md](../Docs_7_Workflow_Canon/1-main_routers.md)
- [10-architectural-patterns/06-BACKGROUND-SERVICE-PATTERN.md](../Docs_5_Project_Working_Docs/10-architectural-patterns/06-BACKGROUND-SERVICE-PATTERN.md)
- [docker-compose.yml](../docker-compose.yml)

---

**This document is a required reference for all future background service work and workflow audits.**
