# WF4 Data Layer Audit: `domains`

- **Date:** 2025-07-01
- **Status:** DRAFT
- **Author:** Cascade AI

## 1. Immediate Blockers & Recommendations

**The WF4 Domain Sitemap Curation endpoint is critically flawed.** The application cannot correctly handle records with the status `"Maybe"`, which is a valid and present value in the database.

**Immediate action is required to prevent data corruption and application errors:**

1.  **Fix the Code First:** The application's [SitemapCurationStatus](cci:2://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/enums.py:46:0-55:25) enum **must** be updated to align with the database reality.
    *   **Add the `"Maybe"` value** to the [SitemapCurationStatus](cci:2://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/enums.py:46:0-55:25) enum in [src/models/enums.py](cci:7://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/enums.py:0:0-0:0).
2.  **No Database Changes:** The database schema and type for this workflow are correct. No changes are needed on the database side.

---

## 2. Objective

This document provides a definitive audit of the data layer for **Workflow 4 (Domain Sitemap Curation)**. It details the critical discrepancies found between the live database state (the source of truth) and the SQLAlchemy models for the `domains` table.

## 3. Executive Summary

A critical mismatch exists for the `sitemap_curation_status` field within the `domains` workflow. While the model correctly points to the right database type, the application's corresponding Enum is missing a key value.

1.  **ENUM Value Mismatch:** The database contains the valid status `"Maybe"`, which is absent from the [SitemapCurationStatus](cci:2://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/enums.py:46:0-55:25) enum in the application code.
2.  **Correct Type Usage:** Unlike other workflows, the [Domain](cci:2://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/domain.py:38:0-351:25) model correctly references the `sitemap_curation_status` database type. The issue is confined to the Enum definition itself.

## 4. Layer 1: Database State (Source of Truth)

The following represents the ground truth of the `domains` table in the remote PostgreSQL database.

| Column | Database Data Type | Live Values Found |
| :--- | :--- | :--- |
| **`sitemap_curation_status`** | `sitemap_curation_status` | `New`, `Selected`, **`Maybe`** |

**Key Finding:** The database correctly uses a dedicated type and stores `Maybe` as a valid status for this workflow.

## 5. Layer 2: Application Model State (`src/models/`)

This layer defines how the application expects the database to be structured.

| File | Model/Enum | Definition | Mismatch Analysis |
| :--- | :--- | :--- | :--- |
| [domain.py](cci:7://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/domain.py:0:0-0:0) | `Domain.sitemap_curation_status` | `SQLAlchemyEnum(SitemapCurationStatus, name="sitemap_curation_status", ...)` | **OK:** The model correctly references the `sitemap_curation_status` DB type and the [SitemapCurationStatus](cci:2://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/enums.py:46:0-55:25) enum. |
| [enums.py](cci:7://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/enums.py:0:0-0:0) | [SitemapCurationStatus](cci:2://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/enums.py:46:0-55:25) | `["New", "Queued", "Processing", "Complete", "Error", "Skipped", "Selected"]` | **CRITICAL MISMATCH:** The value `"Maybe"` is missing from the enum definition. |

**Key Finding:** The application will raise a validation error when it retrieves a [Domain](cci:2://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/domain.py:38:0-351:25) record from the database where the `sitemap_curation_status` is `"Maybe"`.

## 6. Summary of Discrepancies

| Layer | `sitemap_curation_status` ENUM Type Name | `sitemap_curation_status` ENUM Allowed Values |
| :--- | :--- | :--- |
| **Database (Truth)** | `sitemap_curation_status` | `New`, `Selected`, **`Maybe`** |
| **Model (Code)** | `sitemap_curation_status` | `New`, `Selected`, `Queued`, etc. (Missing `Maybe`) |

## 7. Recommendations for Work Order

1.  **Correct Enum Definition ([src/models/enums.py](cci:7://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/enums.py:0:0-0:0)):**
    -   Add the missing member to the [SitemapCurationStatus](cci:2://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/enums.py:46:0-55:25) enum class: `MAYBE = "Maybe"`.

2.  **Verification:**
    -   Conduct endpoint testing to confirm that [Domain](cci:2://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/domain.py:38:0-351:25) records with the `"Maybe"` status can be retrieved and updated without error.