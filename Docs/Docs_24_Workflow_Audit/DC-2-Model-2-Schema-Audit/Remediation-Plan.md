# Project ScraperSky: Data Layer Remediation Briefing & Action Plan

- **Date:** 2025-07-01
- **Status:** ACTIVE
- **Author:** Cascade AI
- **Objective:** To guide the systematic repair of the ScraperSky backend's data layer by resolving documented discrepancies between the application models and the live database schema.

## 1. Executive Summary

This document outlines the history, current state, and strategic plan for remediating the ScraperSky backend's data layer (Layer 1). A previous, context-unaware AI intervention caused a significant divergence between the application's SQLAlchemy models and the production database schema.

A comprehensive, evidence-based audit of six critical workflows has now been completed. This audit provides a definitive map of all schema and data mismatches. The core problem is **systemic schema drift**.

This is a salvageable situation. The path forward is not a system-wide reset, but a targeted, prioritized, one-by-one repair of the documented issues. This document serves as the single source of truth for that remediation process.

## 2. Background: How We Got Here

The project owner initiated a standardization effort to align the codebase with a set of ideal architectural patterns and conventions. As part of this, an AI agent was tasked with refactoring Layer 1 (SQLAlchemy Models and Enums).

The critical error occurred when the AI performed this refactoring **in a vacuum**. It operated solely based on documentation and architectural ideals, without first querying and respecting the state of the live database. It overwrote existing models and enums, effectively creating a new, ideal version of the data layer that did not match the deployed reality.

This action introduced a fundamental schism between the code and the database, leading to application instability, runtime errors, and data corruption. Subsequent development has been hampered by this core disconnect.

## 3. Current State: A Known, Mapped Problem

We have just completed a rigorous audit of six key workflows. For each workflow, we:
1.  Queried the live database to establish the **source of truth** for table structures, column types, and enum values.
2.  Inspected the local application code (`src/models/` and [src/models/enums.py](cci:7://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/enums.py:0:0-0:0)).
3.  Produced a detailed markdown audit report ([WF1.md](cci:7://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/Docs/Docs_24_Workflow_Audit/DC-2-Model-2-Schema-Audit/WF1.md:0:0-0:0) through [WF6.md](cci:7://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/Docs/Docs_24_Workflow_Audit/DC-2-Model-2-Schema-Audit/WF6.md:0:0-0:0)) documenting every discrepancy.

The audit revealed a consistent pattern of errors, which have been categorized by severity:

*   **P0 - Critical Schema Error:** The database schema itself is fundamentally flawed (e.g., a column has the wrong data type). This is the highest priority.
*   **P1 - Critical Data Mismatch:** The application's models or enums are missing values that exist in the database, which will cause runtime crashes.
*   **P2 - Code Health & Inconsistency:** The code contains duplicate or confusing elements that increase technical debt and risk of future errors.

## 4. The Action Plan: Strategic, Prioritized Remediation

The guiding principle is simple: **The database is the source of truth.** Our goal is to bring the application code into perfect alignment with it. Where the database schema itself is flawed, we will execute a migration to correct it.

We will address the issues in a prioritized order, starting with the most critical failures.

---

### **Remediation Queue**

#### **Priority 0: Critical Schema Errors**

1.  **Workflow 1: `places_staging` Status Column**
    *   **Problem:** The [status](cci:1://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/routers/places_staging.py:106:0-142:9) column is of type `sitemap_import_curation_status` instead of a place-specific type. This is a severe data modeling error.
    *   **Action:**
        1.  Create and execute a database migration to create a new `place_status` enum type.
        2.  `ALTER` the `places_staging.status` column to use this new type.
        3.  Handle existing invalid data as part of the migration.
    *   **Reference:** [Docs/Docs_24_Workflow_Audit/DC-2-Model-2-Schema-Audit/WF1.md](cci:7://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/Docs/Docs_24_Workflow_Audit/DC-2-Model-2-Schema-Audit/WF1.md:0:0-0:0)

2.  **Workflow 5: Missing `deep_scrape_curation_status` Column**
    *   **Problem:** The [SitemapFile](cci:2://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/sitemap.py:37:0-119:34) model is completely missing a column that exists and is used in the database.
    *   **Action:**
        1.  Add the `deep_scrape_curation_status` attribute to the [SitemapFile](cci:2://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/sitemap.py:37:0-119:34) model in [src/models/sitemap.py](cci:7://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/sitemap.py:0:0-0:0).
        2.  Ensure it uses the correct [SitemapDeepCurationStatus](cci:2://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/enums.py:213:0-220:25) enum and references the correct database type name (`SitemapCurationStatusEnum`).
    *   **Reference:** [Docs/Docs_24_Workflow_Audit/DC-2-Model-2-Schema-Audit/WF5.md](cci:7://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/Docs/Docs_24_Workflow_Audit/DC-2-Model-2-Schema-Audit/WF5.md:0:0-0:0)

#### **Priority 1: Critical Data Mismatches**

3.  **Workflow 3: `local_businesses` Status Enum**
    *   **Problem:** The application's [PlaceStatus](cci:2://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/enums.py:34:0-43:25) enum is missing the `"Archived"` value, which exists in the database. The model also references the wrong enum type name (`place_status` instead of `local_business_status`).
    *   **Action:**
        1.  Create a dedicated `LocalBusinessStatus` enum.
        2.  Update the [LocalBusiness](cci:2://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/local_business.py:25:0-114:76) model to use this new enum and the correct DB type name.
    *   **Reference:** [Docs/Docs_24_Workflow_Audit/DC-2-Model-2-Schema-Audit/WF3.md](cci:7://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/Docs/Docs_24_Workflow_Audit/DC-2-Model-2-Schema-Audit/WF3.md:0:0-0:0)

4.  **Workflow 4: `domains` Sitemap Curation Status**
    *   **Problem:** The [SitemapCurationStatus](cci:2://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/enums.py:46:0-55:25) enum is missing the `"Maybe"` value, which exists in the database.
    *   **Action:**
        1.  Add `"Maybe"` to the [SitemapCurationStatus](cci:2://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/enums.py:46:0-55:25) enum in [src/models/enums.py](cci:7://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/enums.py:0:0-0:0).
    *   **Reference:** [Docs/Docs_24_Workflow_Audit/DC-2-Model-2-Schema-Audit/WF4.md](cci:7://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/Docs/Docs_24_Workflow_Audit/DC-2-Model-2-Schema-Audit/WF4.md:0:0-0:0)

#### **Priority 2: Code Health & Inconsistency**

5.  **Workflow 6: `sitemap_files` Import Status**
    *   **Problem:** The [SitemapImportProcessingStatus](cci:2://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/enums.py:186:0-192:19) enum contains values not found in the database and a duplicate, confusingly-named enum exists.
    *   **Action:**
        1.  Align the [SitemapImportProcessingStatus](cci:2://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/enums.py:186:0-192:19) enum with the database reality.
        2.  Deprecate and remove the redundant [SitemapImportProcessStatus](cci:2://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/enums.py:177:0-183:19) enum.
    *   **Reference:** [Docs/Docs_24_Workflow_Audit/DC-2-Model-2-Schema-Audit/WF6.md](cci:7://file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/Docs/Docs_24_Workflow_Audit/DC-2-Model-2-Schema-Audit/WF6.md:0:0-0:0)

---

## 5. Next Steps

Execute the remediation plan, beginning with Priority 0. Each task will be handled as a discrete unit of work: **Propose -> Approve -> Execute -> Verify.** This methodical approach will restore stability and bring the application into alignment with its data and its intended architecture.