# Workflow Trace: Local Business Curation "Selected" Status to Domain Extraction Queueing

**Version:** 1.1
**Date:** 2025-05-05
**Last Updated By:** Cascade AI

This document traces the full dependency chain for the user workflow where items (local businesses) are marked as "Selected" in the "Local Business Curation" UI tab, resulting in them being queued for domain extraction/processing in the backend.

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

    - **Role:** Contains the HTML structure for the "Local Business Curation" tab, including the table, checkboxes, status dropdown (`localBusinessBatchStatusUpdate`), and update button (`applyLocalBusinessBatchUpdate`).
    - **UI Communication Point:** Tab "Local Business Curation" displays businesses ready for domain extraction

2.  **File:** `../../static/js/local-business-curation-tab.js` (Layer 6: UI Components) [NOVEL]
    - **Role:** Handles user interactions within the Local Business Curation tab.
    - **Function:** `applyLocalBusinessBatchUpdate()` (or similarly named function attached to the update button)
      - Triggered when the "Update X Selected" button is clicked.
      - Collects `local_business_ids` (or primary keys) from selected checkboxes.
      - Gets the target `status` ("Selected") from the dropdown.
      - **API Call:** Sends a `PUT` request to `/api/v3/local-businesses/status` with IDs and `status` in the request body.
      - **Producer Action:** Initiates the workflow by requesting status update to "Selected"

### 1.2. Layer 3: API Router

1.  **File:** `../../src/routers/local_businesses.py` (Layer 3: Routers) [NOVEL]
    - **Role:** Defines API endpoints for managing `LocalBusiness` (Layer 1: Models & ENUMs) entities.
    - **Function:** `update_local_businesses_status_batch(...)`, handling `PUT /api/v3/local-businesses/status`.
      - Receives `local_business_ids` and `status` ("Selected") from the `update_request` (`LocalBusinessBatchStatusUpdateRequest` (Layer 2: Schemas)).
      - **Database Interaction:** Performs updates on the `local_businesses` table (Layer 1: Models & ENUMs)
      - **Transaction Boundary:** Owns transaction with `async with session.begin()`
      - **Key Logic (Dual-Status Update):**
        - Maps the incoming API status ("Selected") to the database enum `PlaceStatusEnum.Selected` (Layer 1: Models & ENUMs) (Note: Uses `PlaceStatusEnum`, not a dedicated `LocalBusinessStatusEnum`).
        - Calculates internal trigger logic: `trigger_domain_extraction = target_db_status_member == PlaceStatusEnum.Selected` (Layer 1: Models & ENUMs).
        - Fetches the corresponding `LocalBusiness` (Layer 1: Models & ENUMs) objects from the database.
        - Iterates through the fetched `LocalBusiness` (Layer 1: Models & ENUMs) objects:
          - Updates `local_business.status = PlaceStatusEnum.Selected` (Layer 1: Models & ENUMs).
          - **Event Trigger:** Explicitly checks `if trigger_domain_extraction:`. If true:
            - Sets `local_business.domain_extraction_status = DomainExtractionStatusEnum.Queued` (Layer 1: Models & ENUMs).
            - Sets `local_business.domain_extraction_error = None`.
          - Updates `local_business.updated_at`.
        - Commits the transaction using `session.begin()` context manager.
      - Depends on `get_db_session`, `get_current_user`, `LocalBusinessBatchStatusUpdateRequest` (Layer 2: Schemas), `LocalBusiness` (Layer 1: Models & ENUMs), `PlaceStatusEnum` (Layer 1: Models & ENUMs), `DomainExtractionStatusEnum` (Layer 1: Models & ENUMs).

### 1.3. Layer 4: Services & Background Jobs

1.  **File:** `../../src/services/sitemap_scheduler.py` (Layer 4: Services) [SHARED]
    - **Role:** Contains the scheduled job that polls the database. Although named "sitemap", it handles multiple types of pending jobs.
    - **Function:** `process_pending_jobs()`
      - **Background Process:** Runs periodically based on `SITEMAP_SCHEDULER_INTERVAL_MINUTES`.
      - **Database Query:** Fetches `LocalBusiness` (Layer 1: Models & ENUMs) records with `domain_extraction_status = "Queued"`
      - **Consumer Action:** Processes the queued items by calling the domain extraction service (Layer 4: Services)
      - **Event Processing:** Section "Process Pending Domain Extractions" identifies and processes events
      - **Connection Point WF3→WF4:** This is where WF3's output (queued businesses) is consumed by WF4 (domain extraction)
      - **Query Logic:** Selects `LocalBusiness` (Layer 1: Models & ENUMs) records where `domain_extraction_status == DomainExtractionStatusEnum.Queued` (Layer 1: Models & ENUMs), ordered by `updated_at`, limited by `SITEMAP_SCHEDULER_BATCH_SIZE`. Uses `get_background_session()`.
      - **Action:** For each found `LocalBusiness` (Layer 1: Models & ENUMs) record:
        - Instantiates `LocalBusinessToDomainService` (Layer 4: Services).
        - Calls `local_business_to_domain_service.process_single_business(local_business_id=business.id)`.
        - Updates `local_business.domain_extraction_status` to `Processing`, `Completed`, or `Error` based on the outcome.
2.  **File:** `src/services/business_to_domain_service.py` (Layer 4: Services)
    - **Role:** Contains the core logic for extracting/associating a domain from a `LocalBusiness` (Layer 1: Models & ENUMs) record and potentially creating/updating a `Domain` (Layer 1: Models & ENUMs) record.
    - **Class:** `LocalBusinessToDomainService` (Layer 4: Services)
      - Instantiated by `sitemap_scheduler.py` (Layer 4: Services).
    - **Function:** `process_single_business(local_business_id: UUID)`
      - Called by `sitemap_scheduler.py` (Layer 4: Services).
      - (Assumed Logic - _Needs Verification_): Fetches the `LocalBusiness` (Layer 1: Models & ENUMs), attempts to find/validate a website URL, standardizes it to a domain, checks if a `Domain` (Layer 1: Models & ENUMs) record exists, creates/updates the `Domain` (Layer 1: Models & ENUMs) record, potentially sets initial status on the `Domain` (Layer 1: Models & ENUMs) record (e.g., `sitemap_curation_status='New'`), and returns success/failure.
3.  **File:** `src/scheduler_instance.py`
    - **Role:** Defines the shared `AsyncIOScheduler` instance.
4.  **File:** `src/main.py`
    - **Role:** FastAPI application entry point.
    - **Function:** `@app.on_event("startup")` handler
      - Calls `setup_sitemap_scheduler()` (from `src/services/sitemap_scheduler.py` (Layer 4: Services)).

### 1.4. Layer 1: Models & ENUMs

1.  **File:** `../../src/models/local_business.py` (Layer 1: Models & ENUMs) [SHARED]
    - **Role:** Defines the `LocalBusiness` (Layer 1: Models & ENUMs) SQLAlchemy model class and related enums.
    - **Schema Definition:** Defines the `local_businesses` table structure (Layer 1: Models & ENUMs)
    - **Key Components:**
      - `LocalBusiness` (Layer 1: Models & ENUMs) class with:
        - `status` field (using `PlaceStatusEnum` (Layer 1: Models & ENUMs) from another file, not a dedicated enum)
        - `domain_extraction_status` field (using `DomainExtractionStatusEnum` (Layer 1: Models & ENUMs))
      - `DomainExtractionStatusEnum` (Layer 1: Models & ENUMs) defining states like `Queued`, `InProgress`, `Complete`, `Error`.
    - **Status Transitions:** Supports transitions from any status to "Queued" for domain extraction
      - **Fields Read:** `website_url` (likely read by `business_to_domain_service.py` (Layer 4: Services)).
    - **Enum:** Uses `PlaceStatusEnum` (Layer 1: Models & ENUMs) from `src/models/place.py` (Layer 1: Models & ENUMs) for the main `status` field.
    - **Enum:** `DomainExtractionStatusEnum` (Layer 1: Models & ENUMs)
      - Defines values for the `domain_extraction_status` field (e.g., `Queued`, `Processing`, `Completed`, `Error`). Used by router (Layer 3: Routers) and scheduler (Layer 4: Services).
2.  **File:** `src/models/domain.py` (Layer 1: Models & ENUMs)
    - **Role:** Defines the `Domain` (Layer 1: Models & ENUMs) model.
    - **Class:** `Domain` (Layer 1: Models & ENUMs)
      - **Fields potentially created/updated** by `business_to_domain_service.py` (Layer 4: Services): `domain`, `sitemap_curation_status`, etc.

### 1.5. Layer 5: Background Scheduling Configuration

_(Identical to the previous workflow as the same scheduler job handles multiple tasks)_

1.  **File:** `docker-compose.yml` (Layer 5: Configuration)
    - **Variables:** `SITEMAP_SCHEDULER_INTERVAL_MINUTES`, `SITEMAP_SCHEDULER_BATCH_SIZE`, `SITEMAP_SCHEDULER_MAX_INSTANCES`.
2.  **File:** `src/config/settings.py` (Layer 5: Configuration) (Implied)
    - **Role:** Loads scheduler environment variables.

### 1.6. Layer 7: Testing

1.  **File:** `../../tests/routers/test_local_businesses.py` (Layer 7: Testing) [NOVEL]

    - **Test Coverage:**
      - `test_update_local_businesses_status_batch`: Verifies the API endpoint's (Layer 3: Routers) behavior.
      - `test_update_status_to_selected_queues_domain_extraction`: Specifically verifies that setting status to `Selected` properly triggers the domain extraction queue by setting the `domain_extraction_status` (Layer 1: Models & ENUMs).

2.  **File:** `../../tests/models/test_local_business.py` (Layer 7: Testing) [NOVEL]

    - **Test Coverage:**
      - `test_domain_extraction_status_enum`: Verifies the enum values (Layer 1: Models & ENUMs).
      - `test_local_business_model_domain_extraction_fields`: Verifies field presence/types (Layer 1: Models & ENUMs).

3.  **File:** `../../tests/services/test_sitemap_scheduler.py` (Layer 7: Testing) [NOVEL]
    - **Test Coverage:**
      - `test_process_pending_jobs_picks_up_queued_domain_extractions`: Verify it finds `LocalBusiness` (Layer 1: Models & ENUMs) with status 'Queued' and calls `LocalBusinessToDomainService` (Layer 4: Services).

---

## 2. Workflow Summary

1. **User Interaction**: User selects one or more items from the "Local Business Curation" tab (Layer 6: UI Components) and chooses status "Selected" from the dropdown.
2. **API Call**: When they click the update button, a PUT request is made to the `/api/v3/local-businesses/status` endpoint (Layer 3: Routers) with the selected IDs and target status.
3. **Database Update**: The router (Layer 3: Routers) fetches the corresponding `LocalBusiness` (Layer 1: Models & ENUMs) entities and updates their `status` field with `PlaceStatusEnum.Selected` (Layer 1: Models & ENUMs).
4. **Workflow Connection Point (Producer)**: When (and only when) the target status is `Selected`, the router (Layer 3: Routers) also sets `domain_extraction_status = DomainExtractionStatusEnum.Queued` (Layer 1: Models & ENUMs).
5. **Background Processing**: Periodically, the sitemap scheduler's (`src/services/sitemap_scheduler.py` (Layer 4: Services)) `process_pending_jobs` function runs and checks for `LocalBusiness` (Layer 1: Models & ENUMs) records with `domain_extraction_status = 'Queued'`.
6. **Workflow Connection Point (Consumer)**: Any queued records are passed to a service (`src/services/business_to_domain_service.py` (Layer 4: Services)) for domain extraction processing.

**Producer-Consumer Relationship**: WF3-LocalBusinessCuration acts as a producer for WF4-DomainCuration. The producer signal is the status change to "Queued" in the `domain_extraction_status` field (Layer 1: Models & ENUMs), which is consumed by the sitemap_scheduler background process (Layer 4: Services).

**Note**: The domain extraction process is implemented in WF4-DomainCuration, which is triggered by this workflow.

---

## 3. Key Logic Points & Unused Parameters

- **Dual-Status Update Logic:** Verified implementation in `src/routers/local_businesses.py::update_local_businesses_status_batch` (Layer 3: Routers). Setting the main `status` (using `PlaceStatusEnum` (Layer 1: Models & ENUMs)) to `Selected` automatically sets `domain_extraction_status` (Layer 1: Models & ENUMs) to `Queued`.
- **Unused Parameters:** No unused trigger parameters identified in the relevant router function signature (Layer 3: Routers).
- **Scheduler Query:** The background job in `src/services/sitemap_scheduler.py` (Layer 4: Services) correctly polls the `local_businesses` table (Layer 1: Models & ENUMs) for the `Queued` status in the `domain_extraction_status` field (Layer 1: Models & ENUMs).
- **Eligibility Check Note:** The router (Layer 3: Routers) code currently appears to queue for domain extraction whenever status is set to 'Selected', potentially overriding previous extraction states (due to a commented-out eligibility check).

---

## 4. Potential Generalization / Modularization

- **Status Transition Configuration:** The "when status is Selected, also set `domain_extraction_status` to Queued" appears to be hardcoded. A more general approach would be to configure status transitions that trigger other workflows.

- **Naming Inconsistency:** The file is named `sitemap_scheduler.py` (Layer 4: Services), but it handles non-sitemap jobs like domain extraction. This suggests potential refactoring opportunity.

- **Producer-Consumer Formalization:** This workflow would benefit from the standardized producer-consumer pattern documented in `PRODUCER_CONSUMER_WORKFLOW_PATTERN.md`, including consistent naming and separation of concerns.

## 5. Workflow Connections

### As Producer

- **Produces For:** WF4-DomainCuration
- **Production Signal:** Sets `domain_extraction_status = "Queued"` in `local_businesses` table (Layer 1: Models & ENUMs)
- **Connection Point:** `src/routers/local_businesses.py::update_local_businesses_status_batch()` (Layer 3: Routers) → `src/services/sitemap_scheduler.py::process_pending_jobs()` (Layer 4: Services)

### As Consumer

- **Consumes From:** WF2-StagingEditor
- **Consumption Signal:** Reads place records with `status = "Selected"` (Layer 1: Models & ENUMs)
- **Connection Point:** `src/routers/places_staging.py::update_places_status_batch()` (Layer 3: Routers) → `src/routers/local_businesses.py::get_local_businesses()` (Layer 3: Routers)
