# WF6 Data Layer Audit: `sitemap_files` Import Status

- **Date:** 2025-07-01
- **Status:** DRAFT
- **Author:** Cascade AI

## 1. Immediate Blockers & Recommendations

The WF6 Sitemap Import workflow has a **low-severity data mismatch** that could cause silent data inconsistencies. The application's status enum contains values that are not present in the live database.

**Recommendations:**

1.  **Align Enum with Reality:** The [SitemapImportProcessingStatus](cci:2://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/enums.py:186:0-192:19) enum in [src/models/enums.py](cci:7://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/enums.py:0:0-0:0) should be updated to match the values actually present in the database.
    *   The values `Queued` and [Processing](cci:2://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/enums.py:148:0-154:19) should be reviewed. If they are part of the intended workflow but no records currently exist with these statuses, this should be noted. If they are deprecated, they should be removed.
    *   The casing of `Complete` should be verified against the database's `Complete`.
2.  **Cleanup Redundant Enums:** The [SitemapImportProcessStatus](cci:2://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/enums.py:177:0-183:19) enum in [src/models/enums.py](cci:7://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/enums.py:0:0-0:0) appears to be a duplicate and should be deprecated and removed to avoid confusion.

---

## 2. Objective

This document provides a definitive audit of the data layer for **Workflow 6 (Sitemap Import)**. It details the discrepancies found between the live database state and the SQLAlchemy models for the `sitemap_import_processing_status` column in the `sitemap_files` table.

## 3. Executive Summary

A low-severity enum mismatch exists for the `sitemap_import_processing_status` field. The application's enum definition includes values not found in the live database.

1.  **Enum Value Mismatch:** The [SitemapImportProcessingStatus](cci:2://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/enums.py:186:0-192:19) enum in [src/models/enums.py](cci:7://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/enums.py:0:0-0:0) contains the values `Queued` and [Processing](cci:2://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/enums.py:148:0-154:19), which are not found in the `sitemap_import_processing_status` column in the database.
2.  **Casing Mismatch:** The application uses `Complete` while the database uses `Complete`.
3.  **Redundant Enum:** A nearly identical enum, [SitemapImportProcessStatus](cci:2://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/enums.py:177:0-183:19), exists in the same file, creating a risk of developer error.
4.  **Database is Correct:** The database contains the `sitemap_import_processing_status` column with the type `sitemapimportprocessingstatus` and valid data.

## 4. Layer 1: Database State (Source of Truth)

The following represents the ground truth of the `sitemap_files` table in the remote PostgreSQL database.

| Column | Database Data Type | Live Values Found |
| :--- | :--- | :--- |
| **`sitemap_import_processing_status`** | `sitemapimportprocessingstatus` | `Complete`, `Error` |

**Key Finding:** The database contains a limited, specific set of status values for this column.

## 5. Layer 2: Application Model State (`src/models/`)

This layer defines how the application expects the database to be structured.

| File | Model/Enum | Definition | Mismatch Analysis |
| :--- | :--- | :--- | :--- |
| [sitemap.py](cci:7://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/sitemap.py:0:0-0:0) | [SitemapFile](cci:2://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/sitemap.py:37:0-119:34) | `sitemap_import_processing_status = Column(SQLAlchemyEnum(SitemapImportProcessingStatus, name="sitemap_import_processing_status", ...))` | **OK:** The model correctly references the enum and database column name. |
| [enums.py](cci:7://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/enums.py:0:0-0:0) | [SitemapImportProcessingStatus](cci:2://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/enums.py:186:0-192:19) | `["Queued", "Processing", "Complete", "Error"]` | **MISMATCH:** Contains `Queued` and [Processing](cci:2://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/enums.py:148:0-154:19), which are not in the database. |
| [enums.py](cci:7://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/enums.py:0:0-0:0) | [SitemapImportProcessStatus](cci:2://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/enums.py:177:0-183:19) | `["Queued", "Processing", "Completed", "Error"]` | **REDUNDANT:** A nearly identical enum that adds to confusion. Note the "Completed" vs "Complete" difference. |

**Key Finding:** The application's enum definition is broader than the data found in the database, which could lead to application logic that can never be executed.

## 6. Summary of Discrepancies

| Layer | `sitemap_import_processing_status` ENUM Allowed Values |
| :--- | :--- |
| **Database (Truth)** | `Complete`, `Error` |
| **Model (Code)** | `Queued`, [Processing](cci:2://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/enums.py:148:0-154:19), `Complete`, `Error` |

## 7. Recommendations for Work Order

1.  **Update Enum Definition ([src/models/enums.py](cci:7://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/enums.py:0:0-0:0)):**
    *   Investigate the business logic for the `Queued` and [Processing](cci:2://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/enums.py:148:0-154:19) statuses. If they are valid, no change is needed, but this implies a gap in test data. If they are no longer in use, they should be removed.
    *   Correct the casing in the enum from `Complete` to `Completed` to match the [SitemapImportProcessStatus](cci:2://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/enums.py:177:0-183:19) enum and align with the likely intended standard, even though the database currently holds `Complete`. This is a case where the code's intent seems more correct than the current data.
    *   Deprecate and remove the [SitemapImportProcessStatus](cci:2://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/enums.py:177:0-183:19) enum to leave only one source of truth.

2.  **Data Correction (Optional):**
    *   If `Completed` is the correct standard, a data migration should be considered to update all instances of `Complete` in the database to `Completed`.

3.  **Verification:**
    *   Conduct endpoint testing to confirm that [SitemapFile](cci:2://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/sitemap.py:37:0-119:34) records can be correctly updated with all valid statuses.