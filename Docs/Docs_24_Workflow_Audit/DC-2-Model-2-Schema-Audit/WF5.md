# WF5 Data Layer Audit: `sitemap_files`

- **Date:** 2025-07-01
- **Status:** DRAFT
- **Author:** Cascade AI

## 1. Immediate Blockers & Recommendations

**The WF5 Sitemap Curation workflow is completely non-functional and architecturally broken.** The application's data model is missing a critical column, `deep_scrape_curation_status`, that exists in the database. This will cause the application to fail when trying to process any `sitemap_files` record.

**Immediate action is required to prevent catastrophic application failure:**

1.  **Fix the Code First:** The application's [SitemapFile](cci:2://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/sitemap.py:37:0-119:34) model **must** be updated to reflect the database reality.
    *   **Add the `deep_scrape_curation_status` column** to the [SitemapFile](cci:2://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/sitemap.py:37:0-119:34) model in [src/models/sitemap.py](cci:7://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/sitemap.py:0:0-0:0).
    *   **Use the correct Enum:** The column should use the [SitemapDeepCurationStatus](cci:2://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/enums.py:213:0-220:25) enum from [src/models/enums.py](cci:7://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/enums.py:0:0-0:0), which correctly contains the values found in the database.
    *   **Correct the DB type name:** The `name` parameter for the `SQLAlchemyEnum` must be set to `"SitemapCurationStatusEnum"` to match the type name in the database.
2.  **No Database Changes:** The database schema appears correct for this workflow's business logic. No changes are needed on the database side.

---

## 2. Objective

This document provides a definitive audit of the data layer for **Workflow 5 (Sitemap Curation to Deep Scrape Queueing)**. It details the critical discrepancies found between the live database state and the SQLAlchemy models for the `sitemap_files` table.

## 3. Executive Summary

A critical structural mismatch exists for the `deep_scrape_curation_status` field. The application is blind to this field's existence, making this workflow inoperable.

1.  **Missing Model Column:** The [SitemapFile](cci:2://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/sitemap.py:37:0-119:34) model in [src/models/sitemap.py](cci:7://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/sitemap.py:0:0-0:0) is completely missing the `deep_scrape_curation_status` column.
2.  **Correct Enum Exists but is Unused:** The [SitemapDeepCurationStatus](cci:2://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/enums.py:213:0-220:25) enum, which contains the correct values (`New`, `Selected`, `Archived`, `Not a Fit`, `Maybe`), already exists in [src/models/enums.py](cci:7://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/enums.py:0:0-0:0) but is not being used by any model.
3.  **Database is Correct:** The database correctly has the `deep_scrape_curation_status` column, which uses the type `SitemapCurationStatusEnum` and contains valid data.

## 4. Layer 1: Database State (Source of Truth)

The following represents the ground truth of the `sitemap_files` table in the remote PostgreSQL database.

| Column | Database Data Type | Live Values Found |
| :--- | :--- | :--- |
| **`deep_scrape_curation_status`** | `SitemapCurationStatusEnum` | `New`, `Selected`, `Archived`, `Not a Fit` |

**Key Finding:** The database has the correct column, type, and data for the workflow.

## 5. Layer 2: Application Model State (`src/models/`)

This layer defines how the application expects the database to be structured.

| File | Model/Enum | Definition | Mismatch Analysis |
| :--- | :--- | :--- | :--- |
| [sitemap.py](cci:7://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/sitemap.py:0:0-0:0) | [SitemapFile](cci:2://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/sitemap.py:37:0-119:34) | (Column does not exist) | **CRITICAL MISMATCH:** The model is missing the `deep_scrape_curation_status` column entirely. |
| [enums.py](cci:7://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/enums.py:0:0-0:0) | [SitemapDeepCurationStatus](cci:2://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/enums.py:213:0-220:25) | `["New", "Selected", "Maybe", "Not a Fit", "Archived"]` | **OK (BUT UNUSED):** This enum correctly reflects the database values but is not used in the [SitemapFile](cci:2://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/sitemap.py:37:0-119:34) model. |

**Key Finding:** The application's ORM is unaware of the `deep_scrape_curation_status` column, which will lead to errors during any read or write operation on the `sitemap_files` table.

## 6. Summary of Discrepancies

| Layer | `deep_scrape_curation_status` Column | `deep_scrape_curation_status` ENUM Allowed Values |
| :--- | :--- | :--- |
| **Database (Truth)** | **Exists** (Type: `SitemapCurationStatusEnum`) | `New`, `Selected`, `Archived`, `Not a Fit` |
| **Model (Code)** | **Missing** | `New`, `Selected`, `Maybe`, `Not a Fit`, `Archived` (in the unused [SitemapDeepCurationStatus](cci:2://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/enums.py:213:0-220:25) enum) |

## 7. Recommendations for Work Order

1.  **Update Model Definition ([src/models/sitemap.py](cci:7://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/sitemap.py:0:0-0:0)):**
    *   Import the [SitemapDeepCurationStatus](cci:2://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/enums.py:213:0-220:25) enum from [src/models/enums.py](cci:7://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/enums.py:0:0-0:0).
    *   Add the `deep_scrape_curation_status` column to the [SitemapFile](cci:2://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/sitemap.py:37:0-119:34) model.
    *   The definition should be:
        ```python
        deep_scrape_curation_status = Column(
            SQLAlchemyEnum(
                SitemapDeepCurationStatus,
                name="SitemapCurationStatusEnum", # Must match DB type name
                create_type=False,
            ),
            nullable=True, # Or False, based on business rules
            default=SitemapDeepCurationStatus.NEW,
            index=True,
        )
        ```

2.  **Verification:**
    *   Conduct endpoint testing to confirm that [SitemapFile](cci:2://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/sitemap.py:37:0-119:34) records can be created, read, and updated correctly.