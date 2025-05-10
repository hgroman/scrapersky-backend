# Workflow Trace: Domain Curation "Selected" Status to Sitemap Analysis Queueing

**Version:** 1.1
**Date:** 2025-05-05
**Last Updated By:** Cascade AI

This document traces the full dependency chain for the user workflow where items (domains) are marked with `sitemap_curation_status` = 'Selected' in the "Domain Curation" UI tab, resulting in them being queued for sitemap analysis/processing in the backend.

## Table of Contents

- [1. Involved Files & Components](#1-involved-files--components)
  - [1.1. Layer 6: UI Components & JavaScript](#11-layer-6-ui-components--javascript)
  - [1.2. Layer 3: API Router](#12-layer-3-api-router)
  - [1.3. Layer 4: Services & Background Jobs](#13-layer-4-services--background-jobs)
  - [1.4. Layer 1: Models & ENUMs](#14-layer-1-models--enums)
  - [1.5. Layer 5: Background Scheduling Configuration](#15-layer-5-background-scheduling-configuration)
  - [1.6. Layer 7: Testing](#16-layer-7-testing)
- [2. Workflow Summary](#2-workflow-summary)
- [3. Key Logic Points & Unused Parameters](#3-key-logic-points--unused-parameters)
- [4. Potential Generalization / Modularization](#4-potential-generalization--modularization)

---

## 1. Involved Files & Components

### 1.1. Layer 6: UI Components & JavaScript

1.  **File:** `../../static/scraper-sky-mvp.html` (Layer 6: UI Components) [SHARED]

    - **Role:** Contains the HTML structure for the "Domain Curation" tab, including the table, checkboxes, status dropdown (`domainCurationBatchStatusUpdate`), and update button (`applyDomainCurationBatchUpdateBtn`).
    - **UI Communication Point:** Tab "Domain Curation" displays domains ready for sitemap analysis

2.  **File:** `../../static/js/domain-curation-tab.js` (Layer 6: UI Components) [NOVEL]
    - **Role:** Handles user interactions within the Domain Curation tab.
    - **Function:** `applyDomainCurationBatchUpdate()` (or similarly named function attached to the update button)
      - Triggered when the "Update X Selected" button is clicked.
      - Collects `domain_ids` (or primary keys) from selected checkboxes.
      - Gets the target `sitemap_curation_status` ("Selected") from the dropdown.
      - **API Call:** Sends a `PUT` request to `/api/v3/domains/sitemap-curation-status` with IDs and `status` in the request body.
      - **Producer Action:** Initiates the workflow by requesting status update to "Selected"

### 1.2. Layer 3: API Router

1.  **File:** `../../src/routers/domains.py` (Layer 3: Routers) [NOVEL]
    - **Role:** Defines API endpoints for managing `Domain` (Layer 1: Models & ENUMs) entities.
    - **Function:** `update_domain_sitemap_curation_status_batch(...)`, handling `PUT /api/v3/domains/sitemap-curation/status`.
      - Receives `domain_ids` and `sitemap_curation_status` ("Selected") from the `request_body` (`DomainBatchCurationStatusUpdateRequest` (Layer 2: Schemas)).
      - **Database Interaction:** Performs updates on the `domains` table (Layer 1: Models & ENUMs)
      - **Transaction Boundary:** Owns transaction with `async with session.begin()`
      - **Key Logic (Dual-Status Update):**
        - Maps the incoming API status ("Selected") to the database enum `SitemapCurationStatusEnum.Selected` (Layer 1: Models & ENUMs).
        - Fetches the corresponding `Domain` (Layer 1: Models & ENUMs) objects from the database.
        - Iterates through the fetched `Domain` (Layer 1: Models & ENUMs) objects:
          - Updates `domain.sitemap_curation_status = SitemapCurationStatusEnum.Selected` (Layer 1: Models & ENUMs).
          - **Event Trigger:** Explicitly checks `if db_curation_status == SitemapCurationStatusEnum.Selected:` (Layer 1: Models & ENUMs). If true:
            - Sets `domain.sitemap_analysis_status = SitemapAnalysisStatusEnum.Queued` (Layer 1: Models & ENUMs).
            - Sets `domain.sitemap_analysis_error = None`.
          - Updates `domain.updated_at`.
      - **Producer Signal:** Updates `sitemap_analysis_status` (Layer 1: Models & ENUMs) to "Queued" which signals to WF5 that the domain is ready for sitemap analysis
        - Commits the transaction.
      - Depends on `get_db_session`, `get_current_user`, `DomainBatchCurationStatusUpdateRequest` (Layer 2: Schemas), `Domain` (Layer 1: Models & ENUMs), `SitemapCurationStatusEnum` (Layer 1: Models & ENUMs), `SitemapAnalysisStatusEnum` (Layer 1: Models & ENUMs).

### 1.3. Layer 4: Services & Background Jobs

1.  **File:** `../../src/services/domain_sitemap_submission_scheduler.py` (Layer 4: Services) [NOVEL]
    - **Role:** Contains the scheduled job that polls the database for domains that need sitemap analysis.
    - **Function:** `process_pending_sitemap_submissions()`
      - **Background Process:** Runs periodically based on `DOMAIN_SITEMAP_SCHEDULER_INTERVAL_MINUTES`.
      - **Database Query:** Fetches `Domain` (Layer 1: Models & ENUMs) records with `sitemap_analysis_status = "Queued"`
      - **Consumer Action:** Processes the queued items by calling the domain to sitemap adapter service (Layer 4: Services)
      - **Event Processing:** Section "Process Pending Sitemap Submissions" identifies and processes events
      - **Connection Point WF4→WF5:** This is where WF4's output (queued domains) is consumed by WF5 (sitemap analysis)
      - **Query Logic:** Selects `Domain.id` (Layer 1: Models & ENUMs) records where `sitemap_analysis_status == SitemapAnalysisStatusEnum.Queued` (Layer 1: Models & ENUMs), ordered by `updated_at`, limited by `DOMAIN_SITEMAP_SCHEDULER_BATCH_SIZE`. Uses `get_background_session()`.
      - **Action:** For each found `Domain` (Layer 1: Models & ENUMs) record (fetched individually within the loop):
        - Instantiates `DomainToSitemapAdapterService` (Layer 4: Services).
        - Calls `adapter_service.submit_domain_for_sitemap_scan(domain_id=domain.id, domain_url=domain.domain)`.
        - Updates `domain.sitemap_analysis_status` (Layer 1: Models & ENUMs) to `Processing`, `Completed`, or `Error` based on the outcome of the submission call.
2.  **File:** `../../src/services/domain_to_sitemap_adapter_service.py` (Layer 4: Services) [NOVEL]
    - **Role:** Acts as an adapter to potentially trigger a legacy or external sitemap scanning system/service.
    - **Class:** `DomainToSitemapAdapterService` (Layer 4: Services)
      - Instantiated by `domain_sitemap_submission_scheduler.py` (Layer 4: Services).
    - **Function:** `submit_domain_for_sitemap_scan(domain_id: UUID, domain_url: str)`
      - **Service Communication:** Connects WF4 to WF5 by submitting the domain for sitemap analysis
      - **External API Call:** May interact with external services for domain processing
      - Called by `domain_sitemap_submission_scheduler.py` (Layer 4: Services).
      - (Assumed Logic - _Needs Verification_): Takes the domain details and initiates the actual sitemap discovery process (e.g., by calling `src/services/sitemap/processing_service.py` (Layer 4: Services)'s relevant function, adding a job to a different queue, or calling an external API). Returns success/failure of the _submission_ step.
3.  **File:** `src/services/sitemap/processing_service.py` (Layer 4: Services) (Potential Target)
    - **Role:** May contain the actual logic for finding and parsing sitemaps for a given domain, possibly triggered by the adapter service (Layer 4: Services).
4.  **File:** `src/scheduler_instance.py`
    - **Role:** Defines the shared `AsyncIOScheduler` instance.
5.  **File:** `src/main.py`
    - **Role:** FastAPI application entry point.
    - **Function:** `@app.on_event("startup")` handler
      - Calls `setup_domain_sitemap_submission_scheduler()` (from `src/services/domain_sitemap_submission_scheduler.py` (Layer 4: Services)).

### 1.4. Layer 1: Models & ENUMs

1.  **File:** `../../src/models/domain.py` (Layer 1: Models & ENUMs) [SHARED]
    - **Role:** Defines the `Domain` (Layer 1: Models & ENUMs) SQLAlchemy model class and related enums.
    - **Schema Definition:** Defines the `domains` table (Layer 1: Models & ENUMs) structure
    - **Key Components:**
      - `Domain` (Layer 1: Models & ENUMs) class with:
        - `sitemap_curation_status` field (using `SitemapCurationStatusEnum` (Layer 1: Models & ENUMs))
        - `sitemap_analysis_status` field (using `SitemapAnalysisStatusEnum` (Layer 1: Models & ENUMs))
      - `SitemapCurationStatusEnum` (Layer 1: Models & ENUMs) defining states like `New`, `Selected`, `Maybe`, `Not_a_Fit`, `Archived`.
      - `SitemapAnalysisStatusEnum` (Layer 1: Models & ENUMs) defining states like `Queued`, `Processing`, `Completed`, `Error`.
    - **Status Transitions:** Supports transitions from any `sitemap_curation_status` (Layer 1: Models & ENUMs) to "Selected" and triggering `sitemap_analysis_status = "Queued"` (Layer 1: Models & ENUMs)
2.  **File:** `src/models/api_models.py` (Layer 2: Schemas) (or `src/routers/domains.py` (Layer 3: Routers))
    - **Role:** Defines Pydantic models for API request/response validation.
    - **Class:** (Likely) `DomainBatchCurationStatusUpdateRequest` (Layer 2: Schemas) or similar.
    - **Enum:** (Likely) An API-specific enum mapping to `SitemapCurationStatusEnum` (Layer 1: Models & ENUMs).

### 1.5. Layer 5: Background Scheduling Configuration

1.  **File:** `docker-compose.yml` (Layer 5: Configuration)
    - **Variables:** `DOMAIN_SITEMAP_SCHEDULER_INTERVAL_MINUTES`, `DOMAIN_SITEMAP_SCHEDULER_BATCH_SIZE`, `DOMAIN_SITEMAP_SCHEDULER_MAX_INSTANCES`. _(Note: There's a separate scheduler config for this vs. the `sitemap_scheduler.py` (Layer 4: Services))_.
2.  **File:** `../../src/main.py` [SHARED]
    - **Role:** Initializes and configures the background scheduler.
    - **Function:** Startup function (likely called `setup_domain_sitemap_scheduler` or similar from `src/services/domain_sitemap_submission_scheduler.py` (Layer 4: Services))
      - **Scheduler Config:** Creates the APScheduler instance (or reuses an existing one).
      - **Job Registration:** Adds the `domain_sitemap_submission_scheduler.process_pending_sitemap_submissions` (Layer 4: Services) function to the scheduler with an interval configuration.
      - **System Integration:** Ensures the background process starts with the application

### 1.6. Layer 7: Testing

1.  **File:** `../../tests/routers/test_domains.py` (Layer 7: Testing) [NOVEL]
    - **Test Coverage:**
      - `test_update_domain_sitemap_curation_status_batch`: Verifies the API endpoint's (Layer 3: Routers) behavior.
      - `test_update_sitemap_curation_status_to_selected_queues_sitemap_analysis`: Specifically verifies that setting `sitemap_curation_status` (Layer 1: Models & ENUMs) to `Selected` properly triggers the sitemap analysis queue by setting the `sitemap_analysis_status` (Layer 1: Models & ENUMs).
2.  **File:** `../../tests/models/test_domain.py` (Layer 7: Testing) [NOVEL]
    - **Test Coverage:**
      - `test_sitemap_curation_status_enum`: Verifies the enum values (Layer 1: Models & ENUMs).
      - `test_sitemap_analysis_status_enum`: Verifies the enum values (Layer 1: Models & ENUMs).
      - `test_domain_model_sitemap_fields`: Verifies field presence/types (Layer 1: Models & ENUMs).
3.  **File:** `../../tests/services/test_domain_sitemap_submission_scheduler.py` (Layer 7: Testing) [NOVEL]
    - **Test Coverage:**
      - `test_process_pending_sitemap_submissions_picks_up_queued_domains`: Verify it finds `Domain` (Layer 1: Models & ENUMs) records with `sitemap_analysis_status` 'Queued' and calls the adapter service (Layer 4: Services).

---

## 2. Workflow Summary

1. **User Interaction**: User selects domains in the "Domain Curation" tab (Layer 6: UI Components) and chooses status "Selected" from the dropdown.
2. **API Call**: When they click the update button, a PUT request is made to the `/api/v3/domains/sitemap-curation/status` endpoint (Layer 3: Routers) with the selected IDs and target status.
3. **Database Update**: The router (Layer 3: Routers) fetches the corresponding `Domain` (Layer 1: Models & ENUMs) entities and updates their `sitemap_curation_status` field (Layer 1: Models & ENUMs) with `SitemapCurationStatusEnum.Selected` (Layer 1: Models & ENUMs).
4. **Workflow Connection Point (Producer)**: When (and only when) the target status is `Selected`, the router (Layer 3: Routers) also sets `sitemap_analysis_status = SitemapAnalysisStatusEnum.Queued` (Layer 1: Models & ENUMs).
5. **Background Processing**: Periodically, the domain sitemap submission scheduler's (`src/services/domain_sitemap_submission_scheduler.py` (Layer 4: Services)) `process_pending_sitemap_submissions` function runs and checks for `Domain` (Layer 1: Models & ENUMs) records with `sitemap_analysis_status = 'Queued'`.
6. **Workflow Connection Point (Consumer)**: Any queued records are passed to the domain to sitemap adapter service (`src/services/domain_to_sitemap_adapter_service.py` (Layer 4: Services)) for processing.

**Producer-Consumer Relationship**: WF4-DomainCuration acts as a consumer for WF3-LocalBusinessCuration and as a producer for WF5-SitemapCuration. As a producer, the signal is the status change to "Queued" in the `sitemap_analysis_status` field (Layer 1: Models & ENUMs), which is consumed by the `domain_sitemap_submission_scheduler.py` background process (Layer 4: Services).

---

## 3. Key Logic Points & Unused Parameters

- **Dual-Status Update Pattern:** If `sitemap_curation_status` (Layer 1: Models & ENUMs) is set to "Selected", two fields are updated:

  - `domain.sitemap_curation_status = SitemapCurationStatusEnum.Selected` (Layer 1: Models & ENUMs)
  - `domain.sitemap_analysis_status = SitemapAnalysisStatusEnum.Queued` (Layer 1: Models & ENUMs)

- **Producer-Consumer Queue Mechanism:** The logic that determines "Should a sitemap analysis be queued?" is very specific: `if db_curation_status == SitemapCurationStatusEnum.Selected` (Layer 1: Models & ENUMs).

- **Status as Signal:** The status field serves as the communication mechanism between WF4 and WF5, following the producer-consumer pattern documented in `PRODUCER_CONSUMER_WORKFLOW_PATTERN.md`.

- **Dual-Status Update Logic:** Verified implementation in `src/routers/domains.py::update_domain_sitemap_curation_status_batch` (Layer 3: Routers). Setting the main `sitemap_curation_status` (Layer 1: Models & ENUMs) to `Selected` automatically sets the `sitemap_analysis_status` (Layer 1: Models & ENUMs) to `Queued`.
- **Dedicated Scheduler:** This workflow uses a specific scheduler (`src/services/domain_sitemap_submission_scheduler.py` (Layer 4: Services)) distinct from the one handling deep scans and domain extraction (`src/services/sitemap_scheduler.py` (Layer 4: Services)), configured with its own interval/batch settings.
- **Adapter Service:** The `DomainToSitemapAdapterService` (`src/services/domain_to_sitemap_adapter_service.py` (Layer 4: Services)) acts as an intermediary, decoupling the queue polling from the actual sitemap processing logic.

---

## 4. Potential Generalization / Modularization

- **Status Transition Configuration:** The "when `sitemap_curation_status` is Selected, also set `sitemap_analysis_status` to Queued" appears to be hardcoded. A more general approach would be to configure status transitions that trigger other workflows.

- **Producer-Consumer Formalization:** This workflow follows the standardized producer-consumer pattern documented in `PRODUCER_CONSUMER_WORKFLOW_PATTERN.md`, with consistent naming and separation of concerns.

## 5. Workflow Connections

### As Producer

- **Produces For:** WF5-SitemapCuration
- **Production Signal:** Sets `sitemap_analysis_status = "Queued"` in `domains` table (Layer 1: Models & ENUMs)
- **Connection Point:** `src/routers/domains.py::update_domain_sitemap_curation_status_batch()` (Layer 3: Routers) → `src/services/domain_sitemap_submission_scheduler.py::process_pending_sitemap_submissions()` (Layer 4: Services)

### As Consumer

- **Consumes From:** WF3-LocalBusinessCuration
- **Consumption Signal:** Reads `local_businesses` records with `domain_extraction_status = "Queued"` (Layer 1: Models & ENUMs)
- **Connection Point:** `src/services/sitemap_scheduler.py::process_pending_jobs()` (Layer 4: Services) → `src/services/business_to_domain_service.py::process_single_business()` (Layer 4: Services)

- The "Dual-Status Update Logic" pattern is repeated here and remains a candidate for refactoring into a shared utility.
- The scheduler polling logic is quite similar across the different schedulers (fetch IDs with 'Queued' status, loop, call a service). This polling pattern could potentially be generalized, although the specific tables, status fields, and services called differ.
