# WF3 Data Layer Audit: `local_businesses`

- **Date:** 2025-07-01
- **Status:** DRAFT
- **Author:** Cascade AI

## 1. Immediate Blockers & Recommendations

**The WF3 Local Business endpoint is critically flawed.** The application cannot correctly handle records with the status `"Archived"` and is misaligned with the database's fundamental structure.

**Immediate action is required to prevent data corruption and application errors:**

1.  **Fix the Code First:** The application's code **must** be updated to align with the database reality.
    *   **Create a `LocalBusinessStatus` Enum** in [src/models/enums.py](cci:7://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/enums.py:0:0-0:0) that correctly includes `New`, `Selected`, and `Archived`. The current [PlaceStatus](cci:2://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/enums.py:34:0-43:25) enum is incorrect for this workflow.
    *   **Update the [LocalBusiness](cci:2://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/local_business.py:25:0-114:76) Model** in [src/models/local_business.py](cci:7://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/local_business.py:0:0-0:0) to use the new `LocalBusinessStatus` enum.
    *   **Correct the DB type name** in the [LocalBusiness](cci:2://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/local_business.py:25:0-114:76) model from `"place_status"` to `"local_business_status"`.
2.  **No Database Changes Yet:** Do not attempt to alter the database schema until the application code has been fixed and verified.

---

## 2. Objective

This document provides a definitive audit of the data layer for **Workflow 3 (Local Business)**. It details the critical discrepancies found between the live database state (the source of truth) and the SQLAlchemy models for the `local_businesses` table.

## 3. Executive Summary

A critical mismatch exists for the [status](cci:1://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/routers/google_maps_api.py:219:0-276:9) field within the `local_businesses` workflow. The application is using an entirely incorrect Enum and is pointing to a non-existent database type name for this table.

1.  **ENUM Type Mismatch:** The database uses a type named `local_business_status`, while the application's model incorrectly expects [place_status](cci:1://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/routers/google_maps_api.py:351:0-387:87).
2.  **ENUM Value Mismatch:** The database contains the valid status `"Archived"`, which is absent from the [PlaceStatus](cci:2://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/enums.py:34:0-43:25) enum the model is currently using.
3.  **Incorrect Enum Usage:** The [LocalBusiness](cci:2://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/local_business.py:25:0-114:76) model uses the [PlaceStatus](cci:2://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/enums.py:34:0-43:25) enum, which is intended for a different workflow and does not reflect the actual states of a local business record.

## 4. Layer 1: Database State (Source of Truth)

The following represents the ground truth of the `local_businesses` table in the remote PostgreSQL database.

| Column | Database Data Type | Live Values Found |
| :--- | :--- | :--- |
| **[status](cci:1://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/routers/google_maps_api.py:219:0-276:9)** | `local_business_status` | `New`, `Selected`, `Archived` |

**Key Finding:** The database uses a dedicated type `local_business_status` and correctly stores `Archived` as a valid status.

## 5. Layer 2: Application Model State (`src/models/`)

This layer defines how the application expects the database to be structured.

| File | Model/Enum | Definition | Mismatch Analysis |
| :--- | :--- | :--- | :--- |
| [local_business.py](cci:7://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/local_business.py:0:0-0:0) | `LocalBusiness.status` | `SQLAlchemyEnum(PlaceStatus, name="place_status", ...)` | **CRITICAL MISMATCH:** Expects the DB type to be named [place_status](cci:1://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/routers/google_maps_api.py:351:0-387:87) and incorrectly uses the [PlaceStatus](cci:2://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/enums.py:34:0-43:25) enum. |
| [enums.py](cci:7://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/enums.py:0:0-0:0) | [PlaceStatus](cci:2://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/enums.py:34:0-43:25) | `["New", "Queued", "Processing", "Complete", "Error", "Skipped", "Selected"]` | **CRITICAL MISMATCH:** The value `"Archived"` is missing. This enum is not designed for the Local Business workflow. |

**Key Finding:** The [LocalBusiness](cci:2://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/local_business.py:25:0-114:76) model is completely misaligned with the database, referencing the wrong enum and the wrong database type name.

## 6. Summary of Discrepancies

| Layer | [status](cci:1://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/routers/google_maps_api.py:219:0-276:9) ENUM Type Name | [status](cci:1://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/routers/google_maps_api.py:219:0-276:9) ENUM Allowed Values |
| :--- | :--- | :--- |
| **Database (Truth)** | `local_business_status` | `New`, `Selected`, **`Archived`** |
| **Model (Code)** | [place_status](cci:1://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/routers/google_maps_api.py:351:0-387:87) | `New`, `Selected`, `Queued`, etc. (Missing `Archived`) |

## 7. Recommendations for Work Order

1.  **Create Correct Enum ([src/models/enums.py](cci:7://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/enums.py:0:0-0:0)):**
    -   Define a new `LocalBusinessStatus(str, Enum)` class.
    -   Add the correct members: `New = "New"`, `Selected = "Selected"`, and `Archived = "Archived"`.

2.  **Correct Model Definition ([src/models/local_business.py](cci:7://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/local_business.py:0:0-0:0)):**
    -   Import the new `LocalBusinessStatus` enum.
    -   Change the [status](cci:1://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/routers/google_maps_api.py:219:0-276:9) column definition to use `LocalBusinessStatus`.
    -   Change the `name` parameter to reference the correct database type name: `name="local_business_status"`.

3.  **Database Migration (Long-Term Fix):**
    -   After the code is fixed, create a migration to rename the `local_business_status` type to a standardized name if desired, to align with project conventions.

4.  **Verification:**
    -   Conduct endpoint testing to confirm that [LocalBusiness](cci:2://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/local_business.py:25:0-114:76) records can be correctly handled with all valid statuses.