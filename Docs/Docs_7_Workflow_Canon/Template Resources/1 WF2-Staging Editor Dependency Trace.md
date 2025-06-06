# Workflow Trace: Staging Editor "Selected" Status to Deep Scan Queueing

**Version:** 1.0
**Date:** 2025-05-02

This document traces the full dependency chain for the user workflow where items are marked as "Selected" in the Staging Editor UI, resulting in them being queued for deep scan processing in the backend.

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

---
**[Status Mapping Note]**
All Python files below are annotated with [NOVEL] or [SHARED] per python_file_status_map.md (last verified during WF2 audit, 2025-05-04).
---

## 1. Involved Files & Components

### 1.1. Frontend (UI & JS)

1.  **File:** `static/scraper-sky-mvp.html`
    - **Role:** Contains the HTML structure for the "Staging Editor" tab, including the table, checkboxes, status dropdown, and update button.
2.  **File:** `static/js/staging-editor-tab.js`
    - **Role:** Handles user interactions within the Staging Editor tab.
    - **Function:** `batchUpdateStagingStatus()`
      - Triggered when the "Update X Selected" button is clicked.
      - Collects `place_ids` from selected checkboxes.
      - Gets the target `status` ("Selected") from the dropdown.
      - Sends a `PUT` request to `/api/v3/places/staging/status` with `place_ids` and `status` in the request body.
      - **Crucially:** This function **does not** check for or send the `trigger_deep_scan` query parameter.

### 1.2. Backend (API Router)

1.  **File:** `src/routers/places_staging.py` [NOVEL]
    - **Role:** Defines the API endpoint for updating place statuses.
    - **Function:** `update_places_status_batch(request_body: PlaceBatchStatusUpdateRequest, trigger_deep_scan: bool = Query(False, ...), ...)`
      - Handles `PUT /api/v3/places/staging/status` requests.
      - Receives `place_ids` and `status` ("Selected") from the `request_body`.
      - **Unused Parameter:** Defines a query parameter `trigger_deep_scan: bool` which defaults to `False`, but this parameter is **ignored** by the internal logic responsible for queueing.
      - **Key Logic (Dual-Status Update):**
        - Maps the incoming API status ("Selected") to the database enum `PlaceStatusEnum.Selected`.
        - Calculates a local boolean variable `trigger_deep_scan_logic` based _only_ on whether the target status equals `PlaceStatusEnum.Selected`. (Result: `True`).
        - Fetches the corresponding `Place` objects from the database.
        - Iterates through the fetched `Place` objects:
          - Updates `place.status = PlaceStatusEnum.Selected`.
          - Checks `if trigger_deep_scan_logic and place.deep_scan_status in [None, DeepScanStatusEnum.Error]:` (Condition is met).
          - Sets `place.deep_scan_status = DeepScanStatusEnum.Queued`.
          - Sets `place.deep_scan_error = None`.
          - Updates `place.updated_at`.
        - Commits the transaction using `session.begin()` context manager.
      - Depends on `get_db_session`, `get_current_user`, `PlaceBatchStatusUpdateRequest`, `Place`, `PlaceStatusEnum`, `DeepScanStatusEnum`.

### 1.3. Backend (Services & Background Jobs)

1.  **File:** `src/services/sitemap_scheduler.py` [SHARED]
    - **Role:** Contains the scheduled job that polls the database for items needing processing, including deep scans.
    - **Function:** `process_pending_jobs()`
      - Runs periodically based on `SITEMAP_SCHEDULER_INTERVAL_MINUTES`.
      - Includes a section "Process Pending Deep Scans".
      - **Query Logic:** Selects `Place` records where `deep_scan_status == DeepScanStatusEnum.Queued`, ordered by `updated_at`, limited by `SITEMAP_SCHEDULER_BATCH_SIZE`. Uses `get_background_session()`.
      - **Action:** For each found `Place` record:
        - Instantiates `PlacesDeepService`.
        - Calls `places_deep_service.process_single_deep_scan(place_id=place.place_id, tenant_id=place.tenant_id)`.
        - Updates `place.deep_scan_status` to `Processing`, `Completed`, or `Error` based on the outcome.
    - **Function:** `setup_sitemap_scheduler()`
      - Adds the `process_pending_jobs` function to the shared APScheduler instance (defined in `src/scheduler_instance.py`) on application startup (called from `src/main.py`). Uses settings from environment variables.
2.  **File:** `src/services/places/places_deep_service.py` [SHARED]
    - **Role:** Contains the core logic for performing the deep scan for a single place.
    - **Class:** `PlacesDeepService`
      - Instantiated by `sitemap_scheduler.py`.
    - **Function:** `process_single_deep_scan(place_id: str, tenant_id: str)`
      - Called by `sitemap_scheduler.py`.
      - (Assumed Logic - _Needs Verification by Reading File_): Fetches detailed place data (likely from Google API again or other sources), performs analysis/scraping, potentially updates the `Place` record with results or links to results. Returns success/failure indication. Logs progress and errors (observed DEBUG log).
3.  **File:** `src/scheduler_instance.py` [SHARED]
    - **Role:** Defines and exports the shared `AsyncIOScheduler` instance used by various background jobs.
4.  **File:** `src/main.py`
    - **Role:** FastAPI application entry point.
    - **Function:** `@app.on_event("startup")` handler
      - Calls `setup_sitemap_scheduler()` (and potentially others) to initialize background jobs.

### 1.4. Database (Models & Enums)

1.  **File:** `src/models/place.py` [SHARED]
    - **Role:** Defines the primary data model involved.
    - **Class:** `Place`
      - Mapped to the `places` table.
      - **Fields Updated:** `status`, `deep_scan_status`, `deep_scan_error`, `updated_at`.
    - **Enum:** `PlaceStatusEnum`
      - Defines possible values for the main `status` field (e.g., `Selected`). Used by the router for mapping.
    - **Enum:** `DeepScanStatusEnum`
      - Defines possible values for the `deep_scan_status` field (e.g., `Queued`, `Processing`, `Completed`, `Error`). Used by router and scheduler.
2.  **File:** `src/models/api_models.py`
    - **Role:** Defines Pydantic models for API request/response validation.
    - **Class:** `PlaceBatchStatusUpdateRequest`
      - Used by the router (`update_places_status_batch`) to validate the incoming request body (`place_ids`, `status`).
    - **Enum:** `PlaceStagingStatusEnum`
      - Used in the Pydantic model for API validation. The backend router maps this to the database's `PlaceStatusEnum`.

### 1.5. Background Scheduling Config

1.  **File:** `docker-compose.yml`
    - **Role:** Sets environment variables used by the application, including scheduler settings.
    - **Variables:**
      - `SITEMAP_SCHEDULER_INTERVAL_MINUTES`: How often `process_pending_jobs` runs.
      - `SITEMAP_SCHEDULER_BATCH_SIZE`: Max number of queued deep scans processed per run.
      - `SITEMAP_SCHEDULER_MAX_INSTANCES`: Typically `1`.
2.  **File:** `src/config/settings.py` (Implied)
    - **Role:** Likely uses Pydantic's `BaseSettings` to load environment variables (like scheduler intervals/batch sizes) into a usable settings object referenced by `sitemap_scheduler.py`.

### 1.6. Testing

_(Based on previous searches/knowledge - requires confirmation via codebase search if unsure)_

1.  **File:** `tests/routers/test_places_staging.py` (Likely location)
    - **Role:** Contains tests for the `/api/v3/places/staging` endpoints.
    - **Potential Test Functions:**
      - `test_update_places_status_batch_selected_queues_deep_scan`: Should verify that calling the endpoint with `status='Selected'` results in `deep_scan_status` being set to `Queued` in the mocked DB, irrespective of the `trigger_deep_scan` query parameter.
      - `test_update_places_status_batch_other_status_no_queue`: Should verify that using statuses other than 'Selected' does _not_ change `deep_scan_status`.
      - `test_update_places_status_batch_already_processing_no_queue`: Should verify that if `deep_scan_status` is already 'Processing' or 'Completed', setting main status to 'Selected' doesn't re-queue it.
2.  **File:** `tests/services/places/test_places_deep_service.py` (Likely location)
    - **Role:** Contains unit/integration tests for the `PlacesDeepService`.
    - **Potential Test Functions:**
      - `test_process_single_deep_scan_success`: Mocks external API calls, verifies successful processing updates the `Place` record correctly (e.g., status to 'Completed').
      - `test_process_single_deep_scan_api_error`: Mocks external API errors, verifies it correctly sets `deep_scan_status` to 'Error' and populates `deep_scan_error`.
3.  **File:** `tests/services/test_sitemap_scheduler.py` (Likely location, but might be integration tests)
    - **Role:** Tests the scheduler's ability to pick up queued items.
    - **Potential Test Functions:**
      - `test_process_pending_jobs_picks_up_queued_deep_scans`: Mocks the database session to return `Place` objects with `deep_scan_status='Queued'`, verifies that `PlacesDeepService.process_single_deep_scan` is called for them.

---

## 2. Workflow Summary

1.  User selects items and "Selected" status in Staging Editor UI.
2.  Frontend JS (`batchUpdateStagingStatus`) calls `PUT /api/v3/places/staging/status` with place IDs and status="Selected".
3.  Backend Router (`update_places_status_batch`) receives the call.
4.  Backend **internally** determines deep scan should be triggered because status is "Selected" (ignores unused `trigger_deep_scan` query param).
5.  Backend updates `places.status` to `Selected` and `places.deep_scan_status` to `Queued` in the database.
6.  Background Job (`sitemap_scheduler.process_pending_jobs`) runs periodically.
7.  Background Job queries `places` table for `deep_scan_status == 'Queued'`.
8.  Background Job finds the newly queued item(s).
9.  Background Job calls `PlacesDeepService.process_single_deep_scan` for each item.
10. `PlacesDeepService` performs the deep scan and updates the `places` record's `deep_scan_status` upon completion or error.

---

## 3. Key Logic Points & Unused Parameters

- **Dual-Status Update Logic:** The core logic resides in `src/routers/places_staging.py::update_places_status_batch`. It explicitly checks if the target status is `Selected` and uses that result _alone_ to decide whether to queue for deep scan.
- **Unused Parameter:** The `trigger_deep_scan: bool` query parameter in `update_places_status_batch` is defined but **completely ignored** by the queueing logic. This is a significant potential source of confusion.
- **Scheduler Query:** The background job in `src/services/sitemap_scheduler.py` correctly polls the `places` table for the `Queued` status in the `deep_scan_status` field.

---

## 4. Potential Generalization / Modularization

The "Dual-Status Update Logic" pattern (where updating a primary status field conditionally triggers an update to a secondary processing/queue status field) seems common in this application (as hinted in the architecture doc footnote `[^‡]`).

- **Potential Refactor:** This logic could potentially be extracted into a reusable service function or a method on a base model class (if using shared model logic is desired).
  - **Example Service Function:**
    ```python
    # In a hypothetical 'src/services/curation_service.py'
    async def update_status_and_queue(
        session: AsyncSession,
        model_class: Type[Base], # e.g., Place, Domain
        item_ids: List[Any], # List of primary keys or unique identifiers
        id_field_name: str, # e.g., 'place_id'
        target_status_enum_member: Enum,
        status_field_name: str = "status",
        queueing_status_enum_member: Enum = None, # e.g., DeepScanStatusEnum.Queued
        queueing_field_name: str = None, # e.g., "deep_scan_status"
        queueing_error_field_name: str = None, # e.g., "deep_scan_error"
        trigger_queue_on_statuses: List[Enum] = [] # e.g., [PlaceStatusEnum.Selected]
    ):
        # ... implement generic fetch, update main status, check if target_status_enum_member
        # is in trigger_queue_on_statuses, update queueing field if needed ...
    ```
  - **Benefit:** Centralizes the pattern, makes it easier to test, reduces code duplication in routers.
  - **Consideration:** Requires careful handling of different model types, field names, and enum types. Might add complexity if the patterns aren't _exactly_ the same across different models.

This refactoring is outside the scope of just documentation but addresses the "Bonus" point.
