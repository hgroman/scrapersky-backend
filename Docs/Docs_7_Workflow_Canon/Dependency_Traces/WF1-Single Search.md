# Workflow Trace: Single Search Discovery

**Version:** 1.1
**Date:** 2025-05-05
**Last Updated By:** Cascade AI

This document traces the full dependency chain for the user workflow where a user initiates a single business discovery search via the "Single Search" UI tab, resulting in backend processing via the Google Maps API and storage of results.

## Table of Contents

- [1. Involved Files & Components](#1-involved-files--components)
  - [1.1. Layer 6: UI Components & JavaScript](#11-layer-6-ui-components--javascript)
  - [1.2. Layer 3: API Router](#12-layer-3-api-router)
  - [1.3. Layer 4: Services](#13-layer-4-services)
  - [1.4. Layer 1: Models & ENUMs](#14-layer-1-models--enums)
  - [1.5. Layer 5: Configuration](#15-layer-5-configuration)
  - [1.6. Layer 7: Testing](#16-layer-7-testing)
- [2. Workflow Summary](#2-workflow-summary)
- [3. Key Logic Points](#3-key-logic-points)
- [4. Potential Generalization / Modularization](#4-potential-generalization--modularization)

---

## 1. Involved Files & Components

### 1.1. Layer 6: UI Components & JavaScript

1.  **File:** `static/scraper-sky-mvp.html` (Layer 6: UI Components) [SHARED]
    - **Role:** Contains the HTML structure for the "Single Search" tab, including input fields (`businessType`, `location`, `radius`, `jwt`, etc.) and the search button (`searchBtn`).
2.  **File:** `static/js/single-search-tab.js` (Layer 6: UI Components) [NOVEL]
    - **Role:** Handles user interactions within the Single Search tab.
    - **Function:** `searchPlaces()` (or similar function attached to `searchBtn`)
      - Triggered when the "Search Places" button is clicked.
      - Gathers input values (business type, location, radius, etc.).
      - Sends a `POST` request to `/api/v3/localminer-discoveryscan/search/places` with parameters in the request body.

### 1.2. Layer 3: API Router

1.  **File:** `src/routers/google_maps_api.py` (Layer 3: Routers) [NOVEL]
    - **Role:** Defines the API endpoint for initiating the place search.
    - **Function:** `search_places(...)`
      - Handles `POST /api/v3/localminer-discoveryscan/search/places`.
      - Receives search parameters (`business_type`, `location`, `radius_km`, `tenant_id`) via `PlacesSearchRequest` model.
      - **Synchronous Part:**
        - Generates a unique `job_id` (UUID).
        - Creates a `PlaceSearch` record in the DB (status `pending`) within a transaction.
        - Returns the `job_id` and status URL (`.../search/status/{job_id}`) immediately to the frontend with status `processing`.
      - **Asynchronous Part:**
        - Defines and `await`s an internal async function `process_places_search_background(task_args)`. This runs _after_ the initial response is sent.
        - `process_places_search_background`: Creates a new DB session using `get_session()` and calls `places_search_service.search_and_store(...)`. Handles exceptions by updating `PlaceSearch` status to `failed`.
      - Depends on `get_session_dependency`, `get_session`, `get_current_user`, `PlacesSearchRequest` (Layer 2: Schemas), `PlaceSearch` (Layer 1: Models & ENUMs), `PlacesSearchService` (Layer 4: Services).
    - **Technical Debt**: Missing explicit transaction boundary using 'async with session.begin()' (SCRSKY-250)

### 1.3. Layer 4: Services

1.  **File:** `src/services/places/places_search_service.py` (Layer 4: Services) [NOVEL]
    - **Role:** Orchestrates the search and storage process initiated by the router.
    - **Function:** `search_and_store(...)`
      - Called by the background task within the router function.
      - (Verified Logic):
        - Updates the `PlaceSearch` job status to `processing`.
        - Calls `PlacesService.search_places(...)` to interact with the Google Maps API.
        - Calls `PlacesStorageService.store_places(...)` to save the results to the `places` table.
        - Updates the `PlaceSearch` job status to `complete`.
        - Handles exceptions and updates `PlaceSearch` status to `failed`.
      - Depends on `AsyncSession`, `PlaceSearch` (Layer 1: Models & ENUMs), `PlacesService` (Layer 4: Services), `PlacesStorageService` (Layer 4: Services).
    - **Technical Debt**: Missing specific error handling for API failures (SCRSKY-251)
2.  **File:** `src/services/places/places_service.py` (Layer 4: Services) [NOVEL]
    - **Role:** Handles the direct interaction with the Google Maps Places API (or potentially a mocking layer).
    - **Function:** `search_places(...)` (Likely)
      - Called by `PlacesSearchService`.
      - Takes search parameters (location, type, radius, API key).
      - Makes the external API call to Google Maps.
      - Returns the list of place results.
    - **Technical Debt**: Hardcoded connection parameters (SCRSKY-226)
3.  **File:** `src/services/places/places_storage_service.py` (Layer 4: Services) [NOVEL]
    - **Role:** Handles saving the retrieved place data to the database.
    - **Function:** `store_places(...)`
      - Called by `PlacesSearchService`.
      - Takes a list of place data dictionaries.
      - Iterates through the results, checks for existing `Place` (Layer 1: Models & ENUMs) records based on `place_id`.
      - Creates new `Place` (Layer 1: Models & ENUMs) records or updates existing ones in the `places` table.
      - Depends on `AsyncSession`, `Place` (Layer 1: Models & ENUMs).
    - **Technical Debt**: Raw SQL query violating ORM requirement (SCRSKY-225)

### 1.4. Layer 1: Models & ENUMs

1.  **File:** `src/models/place_search.py` (Layer 1: Models & ENUMs) [NOVEL]
    - **Role:** Defines the model for tracking the search job itself.
    - **Class:** `PlaceSearch` (Layer 1: Models & ENUMs)
      - Mapped to `place_searches` table (assumption).
      - **Fields Used:** `id` (job_id), `tenant_id`, `business_type`, `location`, `params` (stores radius), `status` ('pending', 'processing', 'complete', 'failed'), `created_at`, `updated_at`, `user_id`.
2.  **File:** `src/models/place.py` (Layer 1: Models & ENUMs) [SHARED]
    - **Role:** Defines the model for storing the actual place results and acts as the producer for WF2-Staging Editor workflow.
    - **Class:** `Place` (Layer 1: Models & ENUMs)
      - Mapped to the `places` table (acts as the staging table).
      - **Fields Populated:** Contains numerous fields corresponding to Google Places data (name, address, phone, website, lat/lng, rating, types, etc.), plus `search_job_id`, `tenant_id`, `user_id`, `status` (initially likely 'New'), `created_at`, `updated_at`.
    - **Enum:** `PlaceStatusEnum` (Layer 1: Models & ENUMs)
      - Used to set the initial `status` when results are stored.
    - **Workflow Connection**: Places created with status='New' are later processed by WF2-Staging Editor.

### 1.5. Layer 5: Configuration

1.  **File:** `docker-compose.yml` or `.env` (Layer 5: Configuration) [SHARED]
    - **Variable:** `GOOGLE_MAPS_API_KEY`: Required by `PlacesService` (Layer 4: Services) for external API calls.
    - **Technical Debt**: Should reference consistent settings via `settings.py` (Layer 5: Configuration) rather than direct .env access (SCRSKY-226)

### 1.6. Layer 7: Testing

1. **File:** `tests/routers/test_google_maps_api.py` (Layer 7: Testing) [NOVEL]

   - **Role:** Tests the API endpoint functionality, authentication, and transaction boundaries.
   - **Tests:** Should verify that the router properly creates the `PlaceSearch` (Layer 1: Models & ENUMs) record and returns a valid job_id.

2. **File:** `tests/services/test_places_search_service.py` (Layer 7: Testing) [NOVEL]

   - **Role:** Tests the search orchestration service with mock `PlacesService` (Layer 4: Services) and `PlacesStorageService` (Layer 4: Services).
   - **Tests:** Should verify proper status updates, service delegation, and error handling.

3. **File:** `tests/services/test_places_storage_service.py` (Layer 7: Testing) [NOVEL]
   - **Role:** Tests the database storage logic with mock `PlaceSearch` (Layer 1: Models & ENUMs) and `Place` (Layer 1: Models & ENUMs) models.
   - **Tests:** Should verify proper ORM usage, duplicate handling, and transaction management.

_(Requires confirmation via codebase search)_

1.  **File:** `tests/routers/test_google_maps_api.py` (Layer 7: Testing) (Likely location)
    - **Potential Test Functions:**
      - `test_search_places_success`: Verify endpoint creates `PlaceSearch` (Layer 1: Models & ENUMs) record, returns correct job ID/status URL, and mocks the background task/service calls successfully.
      - `test_search_places_background_task_error`: Verify that if the mocked `search_and_store` raises an error, the `PlaceSearch` (Layer 1: Models & ENUMs) status is updated to `failed`.
2.  **File:** `tests/services/places/test_places_search_service.py` (Layer 7: Testing) (Likely location)
    - **Potential Test Functions:**
      - `test_search_and_store_success`: Mock `PlacesService` (Layer 4: Services) and `PlacesStorageService` (Layer 4: Services), verify `PlaceSearch` (Layer 1: Models & ENUMs) status transitions (processing->complete) and services are called correctly.
      - `test_search_and_store_google_api_error`: Mock `PlacesService` (Layer 4: Services) to raise error, verify `PlaceSearch` (Layer 1: Models & ENUMs) status is set to `failed`.
      - `test_search_and_store_storage_error`: Mock `PlacesStorageService` (Layer 4: Services) to raise error, verify `PlaceSearch` (Layer 1: Models & ENUMs) status is set to `failed`.
3.  **File:** `tests/services/places/test_places_storage_service.py` (Layer 7: Testing) (Likely location)
    - **Potential Test Functions:**
      - `test_store_places_new`: Verify storing new places creates correct `Place` (Layer 1: Models & ENUMs) records.
      - `test_store_places_update`: Verify storing existing places updates them correctly.

---

## 2. Workflow Summary

### Producer-Consumer Pattern

This workflow (WF1) follows the producer pattern by creating `Place` (Layer 1: Models & ENUMs) records with status='New' that are consumed by WF2-Staging Editor. The key integration points:

1. WF1 creates `Place` (Layer 1: Models & ENUMs) records in the 'places' table with status='New'
2. WF2 queries for `Place` (Layer 1: Models & ENUMs) records with status='New' in the staging editor
3. `Place.status` (Layer 1: Models & ENUMs) serves as the handoff field between workflows

4. User enters search terms in "Single Search" UI (Layer 6: UI Components) and clicks "Search Places".
5. Frontend JS (Layer 6: UI Components) calls `POST /api/v3/localminer-discoveryscan/search/places` with search parameters.
6. Backend Router (`src/routers/google_maps_api.py` (Layer 3: Routers)) receives the call.
7. Router synchronously creates a `PlaceSearch` (Layer 1: Models & ENUMs) job record (status `pending`) in the DB and immediately returns the `job_id` to the frontend (indicating status `processing`).
8. Router then `await`s an internal background async function (`process_places_search_background`).
9. The background function gets a new DB session and calls `PlacesSearchService.search_and_store` (`src/services/places/places_search_service.py` (Layer 4: Services)).
10. `PlacesSearchService` (Layer 4: Services) updates `PlaceSearch` (Layer 1: Models & ENUMs) status to `processing`.
11. `PlacesSearchService` (Layer 4: Services) calls `PlacesService` (`src/services/places/places_service.py` (Layer 4: Services)) to query the external Google Maps API.
12. `PlacesSearchService` (Layer 4: Services) calls `PlacesStorageService` (`src/services/places/places_storage_service.py` (Layer 4: Services)) to store the results in the `places` table (Layer 1: Models & ENUMs).
13. `PlacesSearchService` (Layer 4: Services) updates `PlaceSearch` (Layer 1: Models & ENUMs) status to `complete` (or `failed` on error).
14. _(Separate Flow)_ User can potentially poll the status URL (`.../search/status/{job_id}`) returned in Step 4 to check the final `PlaceSearch` (Layer 1: Models & ENUMs) status.

---

## 3. Key Logic Points

- **Asynchronous Processing:** The actual search and storage happen in a background task _after_ the initial API response, preventing long waits for the user. The job status is tracked via the `PlaceSearch` (Layer 1: Models & ENUMs) model.
- **Service Orchestration:** The router (Layer 3: Routers) delegates the main work to `PlacesSearchService` (Layer 4: Services), which in turn coordinates external API calls (`PlacesService` (Layer 4: Services)) and database storage (`PlacesStorageService` (Layer 4: Services)).
- **Staging Table:** The `places` table (Layer 1: Models & ENUMs) serves as the initial storage/staging area for discovered results.

---

## 4. Potential Generalization / Modularization

### Transaction Boundary Improvements

The transaction boundary pattern should be improved to follow the architectural principle: "Routers (Layer 3: Routers) own transaction boundaries, services (Layer 4: Services) are transaction-aware but do not create transactions". Specifically:

1. The router (Layer 3: Routers) should use `async with session.begin()` to own the transaction boundary (SCRSKY-250)
2. Services (Layer 4: Services) should be passed the session but not begin transactions themselves

### ORM Compliance

Any raw SQL in `src/services/places/places_storage_service.py` (Layer 4: Services) should be replaced with proper SQLAlchemy ORM code (SCRSKY-225). This is a critical architectural requirement.

### Configuration Externalization

Hardcoded connection parameters in `src/services/places/places_service.py` (Layer 4: Services) should be moved to `settings.py` (Layer 5: Configuration) (SCRSKY-226) for better maintainability and consistency.

### Error Handling Standardization

Improve error handling for API failures with proper status codes and standardized error messages (SCRSKY-251).

- The pattern of:
  1.  Router (Layer 3: Routers) receives request.
  2.  Router (Layer 3: Routers) creates a job record synchronously.
  3.  Router (Layer 3: Routers) immediately returns job ID.
  4.  Router (Layer 3: Routers) spawns an internal async background task to do the real work (using a new session).
  5.  Background task calls a service (Layer 4: Services) to orchestrate processing and update job status.
      ...could be a reusable pattern for other potentially long-running API requests (like maybe Batch Search). Frameworks like Celery or FastAPI's `BackgroundTasks` are often used for more robust background task management, but this internal async function approach works for simpler cases.
