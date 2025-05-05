# Workflow Trace: Local Business Curation "Selected" Status to Domain Extraction Queueing

**Version:** 1.1
**Date:** 2025-05-05
**Last Updated By:** Cascade AI

This document traces the full dependency chain for the user workflow where items (local businesses) are marked as "Selected" in the "Local Business Curation" UI tab, resulting in them being queued for domain extraction/processing in the backend.

## Table of Contents

- [1. Involved Files & Components](#1-involved-files--components)
  - [1.1. Frontend (UI & JS)](#11-frontend-ui--js)
  - [1.2. Backend (API Router)](#12-backend-api-router)
  - [1.3. Backend (Services & Background Jobs)](#13-backend-services--background-jobs)
  - [1.4. Database (Models & Enums)](#14-database-models--enums)
  - [1.5. Background Scheduling Config](#15-background-scheduling-config)
  - [1.6. Testing](#16-testing)
- [2. Workflow Summary](#2-workflow-summary)
- [3. Key Logic Points & Unused Parameters](#3-key-logic-points--unused-parameters)
- [4. Potential Generalization / Modularization](#4-potential-generalization--modularization)

---

## 1. Involved Files & Components

### 1.1. Frontend (UI & JS)

1.  **File:** `/Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/static/scraper-sky-mvp.html` [SHARED]
    - **Role:** Contains the HTML structure for the "Local Business Curation" tab, including the table, checkboxes, status dropdown (`localBusinessBatchStatusUpdate`), and update button (`applyLocalBusinessBatchUpdate`).
    - **UI Communication Point:** Tab "Local Business Curation" displays businesses ready for domain extraction

2.  **File:** `/Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/static/js/local-business-curation-tab.js` [NOVEL]
    - **Role:** Handles user interactions within the Local Business Curation tab.
    - **Function:** `applyLocalBusinessBatchUpdate()` (or similarly named function attached to the update button)
      - Triggered when the "Update X Selected" button is clicked.
      - Collects `local_business_ids` (or primary keys) from selected checkboxes.
      - Gets the target `status` ("Selected") from the dropdown.
      - **API Call:** Sends a `PUT` request to `/api/v3/local-businesses/status` with IDs and `status` in the request body.
      - **Producer Action:** Initiates the workflow by requesting status update to "Selected"

### 1.2. Backend (API Router)

1.  **File:** `/Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/routers/local_businesses.py` [NOVEL]
    - **Role:** Defines API endpoints for managing `LocalBusiness` entities.
    - **Function:** `update_local_businesses_status_batch(...)`, handling `PUT /api/v3/local-businesses/status`.
      - Receives `local_business_ids` and `status` ("Selected") from the `update_request` (`LocalBusinessBatchStatusUpdateRequest`).
      - **Database Interaction:** Performs updates on the local_businesses table
      - **Transaction Boundary:** Owns transaction with `async with session.begin()`
      - **Key Logic (Dual-Status Update):**
        - Maps the incoming API status ("Selected") to the database enum `PlaceStatusEnum.Selected` (Note: Uses PlaceStatusEnum, not a dedicated LocalBusinessStatusEnum).
        - Calculates internal trigger logic: `trigger_domain_extraction = target_db_status_member == PlaceStatusEnum.Selected`.
        - Fetches the corresponding `LocalBusiness` objects from the database.
        - Iterates through the fetched `LocalBusiness` objects:
          - Updates `local_business.status = PlaceStatusEnum.Selected`.
          - **Event Trigger:** Explicitly checks `if trigger_domain_extraction:`. If true:
            - Sets `local_business.domain_extraction_status = DomainExtractionStatusEnum.Queued`.
            - Sets `local_business.domain_extraction_error = None`.
          - Updates `local_business.updated_at`.
        - Commits the transaction using `session.begin()` context manager.
      - Depends on `get_db_session`, `get_current_user`, `LocalBusinessBatchStatusUpdateRequest`, `LocalBusiness`, `PlaceStatusEnum`, `DomainExtractionStatusEnum`.

### 1.3. Backend (Services & Background Jobs)

1.  **File:** `/Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/services/sitemap_scheduler.py` [SHARED]
    - **Role:** Contains the scheduled job that polls the database. Although named "sitemap", it handles multiple types of pending jobs.
    - **Function:** `process_pending_jobs()`
      - **Background Process:** Runs periodically based on `SITEMAP_SCHEDULER_INTERVAL_MINUTES`.
      - **Database Query:** Fetches LocalBusiness records with domain_extraction_status = "Queued"
      - **Consumer Action:** Processes the queued items by calling the domain extraction service
      - **Event Processing:** Section "Process Pending Domain Extractions" identifies and processes events
      - **Connection Point WF3→WF4:** This is where WF3's output (queued businesses) is consumed by WF4 (domain extraction)
      - **Query Logic:** Selects `LocalBusiness` records where `domain_extraction_status == DomainExtractionStatusEnum.Queued`, ordered by `updated_at`, limited by `SITEMAP_SCHEDULER_BATCH_SIZE`. Uses `get_background_session()`.
      - **Action:** For each found `LocalBusiness` record:
        - Instantiates `LocalBusinessToDomainService`.
        - Calls `local_business_to_domain_service.process_single_business(local_business_id=business.id)`.
        - Updates `local_business.domain_extraction_status` to `Processing`, `Completed`, or `Error` based on the outcome.
2.  **File:** `src/services/business_to_domain_service.py`
    - **Role:** Contains the core logic for extracting/associating a domain from a `LocalBusiness` record and potentially creating/updating a `Domain` record.
    - **Class:** `LocalBusinessToDomainService`
      - Instantiated by `sitemap_scheduler.py`.
    - **Function:** `process_single_business(local_business_id: UUID)`
      - Called by `sitemap_scheduler.py`.
      - (Assumed Logic - _Needs Verification_): Fetches the `LocalBusiness`, attempts to find/validate a website URL, standardizes it to a domain, checks if a `Domain` record exists, creates/updates the `Domain` record, potentially sets initial status on the `Domain` record (e.g., `sitemap_curation_status='New'`), and returns success/failure.
3.  **File:** `src/scheduler_instance.py`
    - **Role:** Defines the shared `AsyncIOScheduler` instance.
4.  **File:** `src/main.py`
    - **Role:** FastAPI application entry point.
    - **Function:** `@app.on_event("startup")` handler
      - Calls `setup_sitemap_scheduler()`.

### 1.4. Database (Models & Enums)

1.  **File:** `/Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/local_business.py` [SHARED]
    - **Role:** Defines the `LocalBusiness` SQLAlchemy model class and related enums.
    - **Schema Definition:** Defines the `local_businesses` table structure
    - **Key Components:**
      - `LocalBusiness` class with:
        - `status` field (using `PlaceStatusEnum` from another file, not a dedicated enum)
        - `domain_extraction_status` field (using `DomainExtractionStatusEnum`)
      - `DomainExtractionStatusEnum` defining states like `Queued`, `InProgress`, `Complete`, `Error`.
    - **Status Transitions:** Supports transitions from any status to "Queued" for domain extraction
      - **Fields Read:** `website_url` (likely read by `business_to_domain_service`).
    - **Enum:** Uses `PlaceStatusEnum` from `src/models/place.py` for the main `status` field.
    - **Enum:** `DomainExtractionStatusEnum`
      - Defines values for the `domain_extraction_status` field (e.g., `Queued`, `Processing`, `Completed`, `Error`). Used by router and scheduler.
2.  **File:** `src/models/domain.py`
    - **Role:** Defines the `Domain` model.
    - **Class:** `Domain`
      - **Fields potentially created/updated** by `business_to_domain_service`: `domain`, `sitemap_curation_status`, etc.

### 1.5. Background Scheduling Config

_(Identical to the previous workflow as the same scheduler job handles multiple tasks)_

1.  **File:** `docker-compose.yml`
    - **Variables:** `SITEMAP_SCHEDULER_INTERVAL_MINUTES`, `SITEMAP_SCHEDULER_BATCH_SIZE`, `SITEMAP_SCHEDULER_MAX_INSTANCES`.
2.  **File:** `src/config/settings.py` (Implied)
    - **Role:** Loads scheduler environment variables.

### 1.6. Testing

1.  **File:** `/Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/tests/routers/test_local_businesses.py` [NOVEL]
    - **Test Coverage:**
      - `test_update_local_businesses_status_batch`: Verifies the API endpoint's behavior.
      - `test_update_status_to_selected_queues_domain_extraction`: Specifically verifies that setting status to `Selected` properly triggers the domain extraction queue by setting the domain_extraction_status.

2.  **File:** `/Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/tests/models/test_local_business.py` [NOVEL]
    - **Test Coverage:**
      - `test_domain_extraction_status_enum`: Verifies the enum values.
      - `test_local_business_model_domain_extraction_fields`: Verifies field presence/types.

3.  **File:** `/Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/tests/services/test_sitemap_scheduler.py` [NOVEL]
    - **Test Coverage:**
      - `test_process_pending_jobs_picks_up_queued_domain_extractions`: Verify it finds `LocalBusiness` with status 'Queued' and calls `LocalBusinessToDomainService`.

---

## 2. Workflow Summary

1. **User Interaction**: User selects one or more items from the "Local Business Curation" tab and chooses status "Selected" from the dropdown.
2. **API Call**: When they click the update button, a PUT request is made to the `/api/v3/local-businesses/status` endpoint with the selected IDs and target status.
3. **Database Update**: The router fetches the corresponding `LocalBusiness` entities and updates their `status` field with `PlaceStatusEnum.Selected`.
4. **Workflow Connection Point (Producer)**: When (and only when) the target status is `Selected`, the router also sets `domain_extraction_status = DomainExtractionStatusEnum.Queued`.
5. **Background Processing**: Periodically, the sitemap scheduler's `process_pending_jobs` function runs and checks for `LocalBusiness` records with `domain_extraction_status = 'Queued'`.
6. **Workflow Connection Point (Consumer)**: Any queued records are passed to a service for domain extraction processing.

**Producer-Consumer Relationship**: WF3-LocalBusinessCuration acts as a producer for WF4-DomainCuration. The producer signal is the status change to "Queued" in the domain_extraction_status field, which is consumed by the sitemap_scheduler background process.

**Note**: The domain extraction process is implemented in WF4-DomainCuration, which is triggered by this workflow.

---

## 3. Key Logic Points & Unused Parameters

- **Dual-Status Update Logic:** Verified implementation in `src/routers/local_businesses.py::update_local_businesses_status_batch`. Setting the main `status` (using `PlaceStatusEnum`) to `Selected` automatically sets `domain_extraction_status` to `Queued`.
- **Unused Parameters:** No unused trigger parameters identified in the relevant router function signature.
- **Scheduler Query:** The background job in `src/services/sitemap_scheduler.py` correctly polls the `local_businesses` table for the `Queued` status in the `domain_extraction_status` field.
- **Eligibility Check Note:** The router code currently appears to queue for domain extraction whenever status is set to 'Selected', potentially overriding previous extraction states (due to a commented-out eligibility check).

---

## 4. Potential Generalization / Modularization

- **Status Transition Configuration:** The "when status is Selected, also set domain_extraction_status to Queued" appears to be hardcoded. A more general approach would be to configure status transitions that trigger other workflows.

- **Naming Inconsistency:** The file is named `sitemap_scheduler.py`, but it handles non-sitemap jobs like domain extraction. This suggests potential refactoring opportunity.

- **Producer-Consumer Formalization:** This workflow would benefit from the standardized producer-consumer pattern documented in PRODUCER_CONSUMER_WORKFLOW_PATTERN.md, including consistent naming and separation of concerns.

## 5. Workflow Connections

### As Producer
- **Produces For:** WF4-DomainCuration
- **Production Signal:** Sets domain_extraction_status = "Queued" in local_businesses table
- **Connection Point:** src/routers/local_businesses.py::update_local_businesses_status_batch() → src/services/sitemap_scheduler.py::process_pending_jobs()

### As Consumer
- **Consumes From:** WF2-StagingEditor
- **Consumption Signal:** Reads place records with status = "Selected"
- **Connection Point:** src/routers/places_staging.py::update_places_status_batch() → src/routers/local_businesses.py::get_local_businesses()
