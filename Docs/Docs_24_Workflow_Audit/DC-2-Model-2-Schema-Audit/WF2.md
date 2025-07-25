# WF2 Data Layer Audit: `places_staging`

- **Date:** 2025-07-01
- **Status:** DRAFT
- **Author:** Cascade AI

## 2. Immediate Blockers & Recommendations

**The WF2 Staging Editor endpoint is non-functional and completely blocked.** The application will crash or return validation errors when handling records with the [status](cci:1://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/routers/google_maps_api.py:219:0-276:9) of `"Maybe"`.

**Immediate action is required to unblock development and testing:**

1.  **Fix the Code First:** The application's code **must** be updated to align with the database reality *before* any new database migrations are attempted.
    *   **Add `"Maybe"` to the [PlaceStatus](cci:2://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/enums.py:34:0-43:25) Enum** in [src/models/enums.py](cci:7://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/enums.py:0:0-0:0).
    *   **Correct the DB type name** in the [Place](cci:2://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/place.py:27:0-81:70) model ([src/models/place.py](cci:7://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/place.py:0:0-0:0)) from `"place_status"` to `"sitemap_import_curation_status"`.
2.  **No Database Changes Yet:** Do not attempt to alter the database schema until the application code has been fixed, deployed, and verified.

---

## 3. Objective

This document provides a definitive audit of the data layer for **Workflow 2 (Staging Editor Curation)**. It details the critical discrepancies found between the live database state (the source of truth), the SQLAlchemy models, and the Pydantic API schemas for the `places_staging` table. The purpose is to create a clear work order for remediation.

## 4. Executive Summary

A critical and multi-layered mismatch exists for the [status](cci:1://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/routers/google_maps_api.py:219:0-276:9) field within the `places_staging` workflow, rendering the API non-functional.

1.  **ENUM Type Mismatch:** The database uses a type named `sitemap_import_curation_status`, while the application's model expects a type named [place_status](cci:1://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/routers/google_maps_api.py:351:0-387:87).
2.  **ENUM Value Mismatch:** The database contains the valid business status `"Maybe"`, which is completely absent from the application's [PlaceStatus](cci:2://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/enums.py:34:0-43:25) enum definition.
3.  **API Schema Inheritance:** The API schema ([StagingUpdateRequest](cci:2://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/schemas/staging_editor.py:7:0-10:91)) inherits the incorrect enum from the model, meaning it cannot validate or process the true data from the database.

These conflicts guarantee application failure and must be resolved before the WF2 endpoint can be used.

## 5. Layer 1: Database State (Source of Truth)

The following represents the ground truth of the `places_staging` table in the remote PostgreSQL database.

| Column | Database Data Type | Live Values Found |
| :--- | :--- | :--- |
| **[status](cci:1://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/routers/google_maps_api.py:219:0-276:9)** | `sitemap_import_curation_status` | `New`, `Selected`, `Maybe` |
| **[deep_scan_status](cci:1://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/services/staging_editor_scheduler.py:106:4-130:84)** | `gcp_api_deep_scan_status` | (Not part of this audit) |

**Key Finding:** The database correctly stores `"Maybe"` as a valid status and uses the type name `sitemap_import_curation_status`.

## 6. Layer 2: Application Model State (`src/models/`)

This layer defines how the application expects the database to be structured.

| File | Model/Enum | Definition | Mismatch Analysis |
| :--- | :--- | :--- | :--- |
| [place.py](cci:7://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/place.py:0:0-0:0) | `Place.status` | `SQLAlchemyEnum(PlaceStatus, name="place_status", ...)` | **CRITICAL MISMATCH:** Expects the DB type to be named [place_status](cci:1://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/routers/google_maps_api.py:351:0-387:87). |
| [enums.py](cci:7://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/enums.py:0:0-0:0) | [PlaceStatus](cci:2://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/enums.py:34:0-43:25) | `["New", "Queued", "Processing", "Complete", "Error", "Skipped", "Selected"]` | **CRITICAL MISMATCH:** The value `"Maybe"` is missing. Contains backend-only statuses not relevant to user curation. |

**Key Finding:** The application's model is fundamentally misaligned with the database reality on both the type name and the allowed values for the [status](cci:1://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/routers/google_maps_api.py:219:0-276:9) column.

## 7. Layer 3: API Schema State ([src/schemas/](cci:7://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/schemas:0:0-0:0))

This layer defines the data contract for API endpoints.

| File | Schema | Field Definition | Mismatch Analysis |
| :--- | :--- | :--- | :--- |
| [staging_editor.py](cci:7://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/schemas/staging_editor.py:0:0-0:0) | [StagingUpdateRequest](cci:2://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/schemas/staging_editor.py:7:0-10:91) | `status: PlaceStatus` | **INHERITED MISMATCH:** The API schema uses the flawed [PlaceStatus](cci:2://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/enums.py:34:0-43:25) enum from the model layer. |

**Key Finding:** The API is incapable of accepting or processing a record with the status `"Maybe"`. It will raise a validation error, blocking all legitimate updates for records with this status.

## 8. Summary of Discrepancies

| Layer | [status](cci:1://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/routers/google_maps_api.py:219:0-276:9) ENUM Type Name | [status](cci:1://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/routers/google_maps_api.py:219:0-276:9) ENUM Allowed Values |
| :--- | :--- | :--- |
| **Database (Truth)** | `sitemap_import_curation_status` | `New`, `Selected`, **`Maybe`** |
| **Model (Code)** | [place_status](cci:1://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/routers/google_maps_api.py:351:0-387:87) | `New`, `Selected`, `Queued`, [Processing](cci:2://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/enums.py:148:0-154:19), etc. |
| **API Schema (Code)** | [place_status](cci:1://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/routers/google_maps_api.py:351:0-387:87) (via model) | `New`, `Selected`, `Queued`, [Processing](cci:2://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/enums.py:148:0-154:19), etc. |

## 9. Recommendations for Work Order

To bring the application into alignment with the database truth, the following steps are required:

1.  **Correct Model Enum ([src/models/enums.py](cci:7://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/enums.py:0:0-0:0)):**
    -   Add `Maybe = "Maybe"` to the [PlaceStatus](cci:2://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/enums.py:34:0-43:25) enum.
    -   Audit and remove any values not relevant to user-facing curation (e.g., [Processing](cci:2://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/enums.py:148:0-154:19), `Error`) and move them to a separate backend-only enum if necessary to maintain clear separation of concerns.

2.  **Correct Model Definition ([src/models/place.py](cci:7://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/place.py:0:0-0:0)):**
    -   Change the [status](cci:1://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/routers/google_maps_api.py:219:0-276:9) column definition to reference the correct database type name: `name="sitemap_import_curation_status"`.

3.  **Database Migration (Long-Term Fix):**
    -   After the code is fixed and deployed, create a new database migration to rename the `sitemap_import_curation_status` type to [place_status](cci:1://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/routers/google_maps_api.py:351:0-387:87). This aligns the database with the application's naming standard permanently.

4.  **Verification:**
    -   After all changes are applied, conduct endpoint testing to confirm that records can be successfully read and updated with all valid statuses, including `Maybe`.