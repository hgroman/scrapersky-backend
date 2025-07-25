# WF1 Data Layer Audit: `places_staging`

- **Date:** 2025-07-01
- **Status:** DRAFT
- **Author:** Cascade AI

## 1. Immediate Blockers & Recommendations

**The WF1 Single Search Discovery workflow is critically broken due to a fundamental schema mismatch.** The `places_staging.status` column is using the wrong enum type in the database, which will cause unpredictable behavior and data corruption.

**This is the highest-priority issue found in the audit and requires immediate remediation:**

1.  **Fix the Database Schema:** A database migration **must** be executed to change the data type of the [status](cci:1://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/services/staging_editor_service.py:115:4-168:9) column in the `places_staging` table.
    *   The column's type must be changed from `sitemap_import_curation_status` to a new, correctly defined `place_status` enum type.
    *   This new `place_status` enum type must be created with the correct values required for the places workflow (`New`, `Selected`, `Archived`, etc.).
2.  **Align the Application Code:** The application's [Place](cci:2://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/place.py:27:0-81:70) model must be updated to use the correct enum.
    *   The [status](cci:1://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/services/staging_editor_service.py:115:4-168:9) column in the [Place](cci:2://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/place.py:27:0-81:70) model in [src/models/place.py](cci:7://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/place.py:0:0-0:0) should use the [PlaceStatus](cci:2://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/enums.py:34:0-43:25) enum from [src/models/enums.py](cci:7://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/enums.py:0:0-0:0).
    *   The `name` parameter for the `SQLAlchemyEnum` must be set to `"place_status"` to match the new, corrected database type name.

---

## 2. Objective

This document provides a definitive audit of the data layer for **Workflow 1 (Single Search Discovery)**. It details the critical discrepancies found between the live database state and the SQLAlchemy models for the `places_staging` table.

## 3. Executive Summary

A critical schema-level error exists for the [status](cci:1://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/services/staging_editor_service.py:115:4-168:9) field in the `places_staging` table. The database is using an enum from an entirely different workflow, a severe data modeling flaw.

1.  **Incorrect DB Column Type:** The `places_staging.status` column is incorrectly defined with the database type `sitemap_import_curation_status`. It should be using a type related to place status.
2.  **Application Model is Correct (but will fail):** The [Place](cci:2://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/place.py:27:0-81:70) model in [src/models/place.py](cci:7://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/place.py:0:0-0:0) correctly attempts to use the [PlaceStatus](cci:2://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/enums.py:34:0-43:25) enum and references the DB type name `place_status`. However, because the database is wrong, this will fail at runtime.
3.  **Data Mismatch:** The live values in the column (`New`, `Selected`, `Maybe`) are a blend of values from different enums, indicating that this error has been present for some time and has already led to data corruption.

## 4. Layer 1: Database State (Source of Truth)

The following represents the ground truth of the `places_staging` table in the remote PostgreSQL database.

| Column | Database Data Type | Live Values Found |
| :--- | :--- | :--- |
| **[status](cci:1://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/services/staging_editor_service.py:115:4-168:9)** | `sitemap_import_curation_status` | `New`, `Selected`, `Maybe` |

**Key Finding:** The database is using the wrong enum type for a critical status column, a severe schema error.

## 5. Layer 2: Application Model State (`src/models/`)

This layer defines how the application expects the database to be structured.

| File | Model/Enum | Definition | Mismatch Analysis |
| :--- | :--- | :--- | :--- |
| [place.py](cci:7://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/place.py:0:0-0:0) | [Place](cci:2://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/place.py:27:0-81:70) | `status = Column(SQLAlchemyEnum(PlaceStatus, name="place_status", ...))` | **MISMATCH:** The model correctly specifies the `place_status` enum type, but this is not what is in the database. |
| [enums.py](cci:7://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/enums.py:0:0-0:0) | [PlaceStatus](cci:2://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/enums.py:34:0-43:25) | `["New", "Queued", "Processing", "Complete", "Error", "Skipped", "Selected"]` | **OK (BUT WILL FAIL):** The enum contains the correct values for this workflow, but it cannot be used because the database column type is wrong. |

## 6. Summary of Discrepancies

| Layer | [status](cci:1://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/services/staging_editor_service.py:115:4-168:9) Column Type | [status](cci:1://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/services/staging_editor_service.py:115:4-168:9) ENUM Allowed Values |
| :--- | :--- | :--- |
| **Database (Truth)** | **`sitemap_import_curation_status`** | `New`, `Selected`, `Maybe` |
| **Model (Code)** | **`place_status`** | `New`, `Queued`, [Processing](cci:2://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/enums.py:148:0-154:19), `Complete`, `Error`, `Skipped`, `Selected` |

## 7. Recommendations for Work Order

1.  **Create Database Migration:**
    *   A new migration must be created and applied via MCP to perform the following:
        1.  Create a new enum type in the database named `place_status` with the values from the application's [PlaceStatus](cci:2://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/enums.py:34:0-43:25) enum.
        2.  `ALTER` the `places_staging` table to change the data type of the [status](cci:1://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/services/staging_editor_service.py:115:4-168:9) column to `place_status`.
        3.  Include a data migration step to handle the existing `Maybe` values, mapping them to an appropriate value in the new `place_status` enum (e.g., `New` or a new `Needs Review` status).

2.  **Update Model Definition ([src/models/place.py](cci:7://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/place.py:0:0-0:0)):**
    *   No change is needed in the model itself, as it is already pointing to the correct [PlaceStatus](cci:2://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/enums.py:34:0-43:25) enum. The fix is purely on the database side.

3.  **Verification:**
    *   After the migration, conduct endpoint testing to confirm that [Place](cci:2://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/place.py:27:0-81:70) records can be created, read, and updated with the correct status values.