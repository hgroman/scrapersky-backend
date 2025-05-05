# ScraperSky Backend: Background Services Architecture (2025-05-04)

## Executive Summary
This document serves as the **single source of truth** for all background services in the ScraperSky backend. It provides:
- A canonical list of all background services, mapped to their workflows, code files, and database tables.
- A clear explanation of their implementation, lifecycle, and integration with the application.
- Guidance for onboarding, auditing, and future extension. **No further excavation should be needed.**

---

## Table of Contents
1. [Overview](#overview)
2. [Canonical Background Services](#canonical-background-services)
3. [Implementation & Integration](#implementation--integration)
4. [Service Details](#service-details)
5. [Scheduler Architecture](#scheduler-architecture)
6. [Database & Transaction Patterns](#database--transaction-patterns)
7. [Security & Compliance](#security--compliance)
8. [Traceability & Documentation](#traceability--documentation)
9. [References](#references)

---

## Overview
The ScraperSky backend relies on a set of **background services** (a.k.a. jobs, schedulers, or workers) to automate curation, enrichment, and analysis workflows. These services:
- Run asynchronously via APScheduler, initialized at FastAPI app startup.
- Are responsible for processing, updating, and maintaining key business entities (domains, local businesses, sitemaps, staging records).
- Are tightly coupled to the main UI panels and workflow steps.

---

## Canonical Background Services

| Service Name                        | Purpose                                                      | Main Code File(s)                                             | Primary Table(s)        |
|-------------------------------------|--------------------------------------------------------------|---------------------------------------------------------------|-------------------------|
| **1. Domain Scheduler**             | Processes pending domains for enrichment/analysis             | `src/services/domain_scheduler.py`                            | `domains`               |
| **2. Domain Sitemap Submission**    | Handles queued domain-to-sitemap submissions                  | `src/services/domain_sitemap_submission_scheduler.py`          | `domains`, `sitemaps`   |
| **3. Sitemap Scheduler**            | Processes pending sitemap jobs & deep scan jobs               | `src/services/sitemap_scheduler.py`                           | `sitemaps`, `places_staging` |
| **4. Sitemap Import Scheduler**     | Handles import of discovered sitemaps                         | `src/services/sitemap_import_scheduler.py`                    | `sitemaps`              |
| **5. Local Business Enrichment**    | Enriches local business records via background jobs           | `src/services/places/places_search_service.py`                | `local_businesses`      |

---

## Implementation & Integration

- **Scheduler Engine:**
  - All background services are registered with a single APScheduler instance (`src/scheduler_instance.py`).
  - The scheduler is started/stopped via FastAPI lifespan events (`src/main.py`).
  - Each job is registered at app startup via a setup function (e.g., `setup_domain_scheduler()`).

- **Job Registration:**
  - Each service has a `setup_*` function that adds the job to the scheduler with an interval, job ID, and handler function.
  - Jobs are uniquely identified by job ID (e.g., `process_pending_domains`, `process_pending_jobs`).

- **Execution:**
  - Jobs run asynchronously, polling the database for records in a `pending` or `queued` state.
  - Each job manages its own session and transaction boundaries, following the architectural mandate: **background tasks manage their own sessions**.

---

## Service Details

### 1. **Domain Scheduler**
- **File:** `src/services/domain_scheduler.py`
- **Job:** `process_pending_domains`
- **Workflow:**
  - Polls `domains` table for entries needing enrichment.
  - Updates status, extracts metadata, and logs results.
  - Handles errors and retries.

### 2. **Domain Sitemap Submission Scheduler**
- **File:** `src/services/domain_sitemap_submission_scheduler.py`
- **Job:** `process_pending_domain_sitemap_submissions`
- **Workflow:**
  - Finds domains queued for sitemap submission.
  - Submits domains for sitemap analysis, updates status.

### 3. **Sitemap Scheduler**
- **File:** `src/services/sitemap_scheduler.py`
- **Job:** `process_pending_jobs`
- **Workflow:**
  - Handles both legacy sitemap jobs and new curation-driven deep scan jobs.
  - Polls `sitemaps` and `places_staging` tables for pending work.
  - Updates status, handles errors, logs processing.

### 4. **Sitemap Import Scheduler**
- **File:** `src/services/sitemap_import_scheduler.py`
- **Job:** `process_sitemap_imports`
- **Workflow:**
  - Handles import and processing of discovered sitemaps.
  - Updates `sitemaps` table, manages status and errors.

### 5. **Local Business Enrichment Worker**
- **File:** `src/services/places/places_search_service.py`
- **Job:** `process_places_search_background`
- **Workflow:**
  - Processes jobs for enriching local business records.
  - Updates `local_businesses` table with new data.
  - Handles errors, logs results.

---

## Scheduler Architecture
- **Centralized APScheduler instance** in `src/scheduler_instance.py`.
- Jobs are registered at startup; logs are written for all job events.
- Each job is uniquely identified and can be managed (started, stopped, debugged) via code or admin scripts.
- All jobs run asynchronously and independently.

---

## Database & Transaction Patterns
- **Routers own transaction boundaries** for API requests.
- **Services are transaction-aware** (accept session but do not manage transactions).
- **Background services manage their own sessions and transactions** (see architectural mandates).
- All jobs use the standardized session factory and dependency injection pattern for DB access.

---

## Security & Compliance
- **JWT authentication** is enforced only at API gateway endpoints (never in DB operations).
- **No tenant filtering** or JWT logic in background service DB connections.
- All connections use Supavisor pooling with correct parameters.
- Compliance is tracked via audit docs and code reviews.

---

## Traceability & Documentation
- Each background service is mapped to a UI workflow tab, API endpoint(s), and database table(s).
- All work orders, implementation plans, and audits are referenced in `/Docs/Docs_5_Project_Working_Docs/`.
- This document is the canonical reference; all future work must update this file.

---

## Code-Based Canonical Implementation (2025-05-04)

### 1. Central Scheduler Instance
- **File:** `src/scheduler_instance.py`
- **Pattern:**
  - A single `AsyncIOScheduler` instance (`scheduler`) is created and shared across all services.
  - Event listeners are attached for job execution and error logging.
  - Lifecycle is managed via `start_scheduler()` and `shutdown_scheduler()` functions, called from `main.py` during FastAPI lifespan events.

### 2. Job Registration Pattern
- Each background service module defines a `setup_*_scheduler()` function (e.g., `setup_domain_scheduler`, `setup_sitemap_scheduler`, etc.).
- This function adds the job to the shared scheduler using `scheduler.add_job`, specifying:
  - The job function (async, e.g., `process_pending_domains`)
  - An interval trigger (minutes from settings)
  - `job_id`, `name`, `replace_existing`, `max_instances`, and `misfire_grace_time`
- After registration, the job's presence and next run time are logged for observability.

### 3. Canonical Job Function Signature & Session Pattern
- **Signature:** All job functions are async and accept a `limit` argument (default 10) for batch size.
- **Session Management:**
  - Each job function uses `async with get_background_session() as session:` to acquire a dedicated DB session for the batch.
  - The entire batch is processed within a single transaction (atomic commit/rollback), unless otherwise noted.
  - For jobs processing multiple items, ORM queries use `.with_for_update(skip_locked=True)` to avoid race conditions.
  - Status enums (e.g., `DomainStatusEnum`, `SitemapImportProcessStatusEnum`) are used for filtering and updating processing state.

### 4. Polling/Status Mechanism
- Each job polls a specific table for records with a `pending`/`queued` status (using the correct Enum value).
- Status fields are updated in-memory during processing, and committed at the end of the batch.
- Error handling is robust: failures are logged, and status is set to `failed`/`error` with error details.

### 5. Relationships: Jobs, Models, and Status Enums
- **Domain Scheduler:**
  - Polls `Domain` table for `status == DomainStatusEnum.pending`
  - Updates status to `processing`, extracts metadata, sets `complete` or `failed`.
- **Sitemap Scheduler:**
  - Polls both legacy sitemap jobs and new deep scan jobs from `places_staging` (using `deep_scan_status` field)
  - Handles both workflows in a single function.
- **Domain Sitemap Submission Scheduler:**
  - Polls `Domain` table for `sitemap_analysis_status == SitemapAnalysisStatusEnum.Queued`
  - Submits domains for sitemap analysis, updates status.
- **Sitemap Import Scheduler:**
  - Polls `SitemapFile` table for `sitemap_import_status == SitemapImportProcessStatusEnum.Queued`
  - Uses a generic `run_job_loop` utility for batch processing.

### 6. Deviations & Special Notes
- All jobs use the shared scheduler; no local APScheduler instances remain.
- All session management is handled via `get_background_session` (no direct session creation).
- Enum-based status fields are strictly enforced for polling and updates.
- Manual job triggers exist for development/testing, but production jobs always run on schedule.
- Job batch sizes, intervals, and max instances are fully configurable via `settings`.

### 7. Code Reality Summary Table

| Job ID                                 | Registration Function                      | Polling Target/Table            | Status Enum Field                | Batch/Session Pattern              |
|----------------------------------------|--------------------------------------------|-------------------------------|-----------------------------------|------------------------------------|
| process_pending_domains                | setup_domain_scheduler                     | Domain                        | DomainStatusEnum.status           | Single session, batch, atomic      |
| process_pending_jobs                   | setup_sitemap_scheduler                    | Sitemap, Place (deep scan)    | Various (legacy + deep_scan)      | Single session, batch, atomic      |
| process_pending_domain_sitemap_submissions | setup_domain_sitemap_submission_scheduler | Domain                        | SitemapAnalysisStatusEnum.status  | Per-domain session, batch loop     |
| process_sitemap_imports                | setup_sitemap_import_scheduler             | SitemapFile                   | SitemapImportProcessStatusEnum    | Generic run_job_loop, batch atomic |

**NOTE:** This table and section reflect the actual code as of 2025-05-04 and supersede any prior documentation if discrepancies exist.

---

## References
- `/Docs/Docs_5_Project_Working_Docs/11-Background-Task-Scheduler/`
- `/Docs/Docs_5_Project_Working_Docs/13-Sitemaps/`
- `/Docs/Docs_5_Project_Working_Docs/14-Google-Deep-Scrape/`
- `/Docs/Docs_5_Project_Working_Docs/26-Standardize-Tab-3-Local-Business-Curation/`
- `/Docs/Docs_5_Project_Working_Docs/27-Standardize-Tab4-Domain-Curation/`
- `src/services/` (all scheduler & worker files)
- `src/scheduler_instance.py` (APScheduler integration)
- `src/main.py` (scheduler startup/shutdown)
- `docker-compose.yml` (environment variables, service configs)

---

**This document must be maintained with every architectural or workflow change involving background services.**

---

## Environment-Based Configuration & Dependency Requirements

### Scheduler Configuration via Environment Variables
- **All scheduler intervals, batch sizes, and max instances are controlled via environment variables**, set in [docker-compose.yml](../docker-compose.yml) and loaded at runtime.
- **Canonical Variables:**
  - `DOMAIN_SCHEDULER_INTERVAL_MINUTES`, `DOMAIN_SCHEDULER_BATCH_SIZE`, `DOMAIN_SCHEDULER_MAX_INSTANCES`
  - `SITEMAP_SCHEDULER_INTERVAL_MINUTES`, `SITEMAP_SCHEDULER_BATCH_SIZE`, `SITEMAP_SCHEDULER_MAX_INSTANCES`
  - `SITEMAP_IMPORT_SCHEDULER_INTERVAL_MINUTES`, `SITEMAP_IMPORT_SCHEDULER_BATCH_SIZE`, `SITEMAP_IMPORT_SCHEDULER_MAX_INSTANCES`
- **Other relevant env vars:**
  - `LOG_LEVEL`, `ENABLE_IMPORT_TRACING`, database connection details, API keys, etc.
- **Precedence:** If a value is set both in code and as an environment variable, the environment variable takes precedence at runtime.
- **Reference:** [docker-compose.yml](../docker-compose.yml) is the single source of truth for production scheduler configuration.

### Application Startup
- The FastAPI app is started via `uvicorn` (`src.main:app`).
- Reload and tracing behaviors are controlled by `ENVIRONMENT` and `ENABLE_IMPORT_TRACING` env vars.
- Scheduler lifecycle (startup/shutdown) is managed via FastAPI lifespan events in `src/main.py`.

### Dependency Requirements
- All required libraries for background services must be present in the Python environment. See [setup.py](../setup.py).
- **Critical:** Ensure `APScheduler` is included in your dependency management (add to `setup.py` or requirements file if not present).

---

This section is authoritative for environment-based configuration and dependency requirements. If discrepancies exist, this section supersedes prior documentation.

---

## Authoritative ENUM Status Values (Database Source)

The following ENUM values are sourced directly from the production database as of 2025-05-04. These are the only valid status values for background service job polling, processing, and transitions. This section supersedes all prior code-based or inferred enum documentation.

### DomainExtractionStatusEnum
- **Referenced by:** Domain Scheduler, Local Business Enrichment
- **Values:**
  - Queued
  - Processing
  - Completed
  - Error

### SitemapAnalysisStatusEnum
- **Referenced by:** Domain Sitemap Submission Scheduler
- **Values:**
  - Queued
  - Processing
  - Completed
  - Error

### SitemapCurationStatusEnum
- **Referenced by:** Sitemap Scheduler (Curation/Deep Scan)
- **Values:**
  - New
  - Selected
  - Maybe
  - Not a Fit
  - Archived

### gcp_api_deep_scan_status_enum
- **Referenced by:** Sitemap Scheduler (Deep Scan)
- **Values:**
  - Queued
  - Processing
  - Completed
  - Error

### sitemap_file_status_enum
- **Referenced by:** Sitemap Scheduler, Sitemap Import Scheduler
- **Values:**
  - Pending
  - Processing
  - Completed
  - Error

### sitemap_import_status_enum
- **Referenced by:** Sitemap Import Scheduler
- **Values:**
  - Queued
  - Processing
  - Completed
  - Error

### task_status
- **Referenced by:** (If used in background jobs)
- **Values:**
  - Queued
  - InProgress
  - Completed
  - Error
  - ManualReview
  - Cancelled
  - Paused

---

For any job or polling logic, use only the above values for status comparisons, transitions, and documentation.

If you add, rename, or deprecate an ENUM value in the database, **this document must be updated immediately to maintain architectural accuracy.**
