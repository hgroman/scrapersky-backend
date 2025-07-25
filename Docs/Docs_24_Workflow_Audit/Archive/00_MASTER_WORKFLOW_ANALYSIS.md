# Master Workflow & System Analysis

**Last Verified:** 2025-06-30

## 1. Executive Summary

This document provides a comprehensive, cross-layer analysis of the ScraperSky backend system, mapping the six canonical workflows to their corresponding database tables, ENUM state transitions, and code owners. It serves as the single source of truth for understanding the application's data flow and business logic, forming the foundation for all technical audits, risk assessments, and future development.

The primary goal is to eliminate architectural drift by ensuring the documented design, the source code implementation, and the database schema remain in perfect alignment.

## 2. Verified Workflow-to-Table Mapping

This table represents the ground truth of the data flow, cross-referenced between the canonical workflow YAML files and the live Supabase database schema.

| Workflow ID | Workflow Name              | Primary Table(s)                     | Key Status Fields                                        | Produces For     |
| :---------- | :------------------------- | :----------------------------------- | :------------------------------------------------------- | :--------------- |
| **WF1**     | Single Search Discovery    | `place_searches`, `places_staging`   | `place_searches.status`, `places_staging.status`         | WF2              |
| **WF2**     | Staging Editor             | `places_staging`                     | `status`, `deep_scan_status`                             | WF3              |
| **WF3**     | Local Business Curation    | `local_businesses`                   | `status`, `domain_extraction_status`                     | WF4              |
| **WF4**     | Domain Curation            | `domains`                            | `sitemap_curation_status`, `sitemap_analysis_status`     | WF5              |
| **WF5**     | Sitemap Curation           | `sitemap_files`                      | `deep_scrape_curation_status`, `sitemap_import_status` | WF6              |
| **WF6**     | Sitemap Import             | `sitemap_files`, `pages`             | `sitemap_import_status`, `pages.status`                  | Future Workflows |


## 3. ENUM State Machine Analysis (TODO)

*This section will detail the complete lifecycle for each key status ENUM in every workflow.*

- **WF1 - place_searches.status:**
- **WF1 - places_staging.status:**
- **WF2 - places_staging.status:**
- **WF2 - places_staging.deep_scan_status:**
- ...and so on for all 6 workflows.

## 4. Code Ownership Mapping (TODO)

*This section will map specific source code modules to their respective workflows.*

- **WF1 - Single Search Discovery:**
  - **Models:** `src/models/place_search.py`, `src/models/place.py` (Defines `Place` model for the `places_staging` table)
  - **Routers:** `src/routers/google_maps_api.py` (Provides the `/search/places` entry point)
  - **Services:** `src/services/places/places_search_service.py` (Orchestrates the Google API call), `src/services/places/places_storage_service.py` (Handles writing results to the `places_staging` table)
  - **Schedulers:** N/A (This workflow is triggered directly by a user API call, not a background scheduler) 
- **WF2 - Staging Editor:**
  - **Models:** `src/models/place.py` (Defines the `Place` model and its `status` and `deep_scan_status` fields)
  - **Routers:** `src/routers/places_staging.py` (Provides the `/places/staging/status` endpoint for users to update status to `Selected`)
  - **Services:** N/A (Business logic for the initial status update is contained within the router)
  - **Schedulers:** `src/services/sitemap_scheduler.py` (Contains the background job that polls for places with `deep_scan_status = 'Queued'` and initiates the scan)
- **WF3 - Local Business Curation:**
  - **Models:** `src/models/local_business.py` (Defines the `LocalBusiness` model created by the deep scan)
  - **Routers:** `src/routers/local_businesses.py` (Provides the UI-facing endpoints for a user to curate records and set status to `Selected`)
  - **Services:** `src/services/places/places_deep_service.py` (The *producer* for this workflow; creates the `LocalBusiness` record after a successful deep scan)
  - **Schedulers:** `src/services/sitemap_scheduler.py` (The *consumer* for this workflow; polls for businesses with `domain_extraction_status = 'Queued'` and triggers the handoff to WF4)
- **WF4 - Domain Curation:**
  - **Models:** `src/models/domain.py` (Defines the `Domain` model created from a `LocalBusiness`)
  - **Routers:** `src/routers/domains.py` (Provides UI-facing endpoints for a user to curate domains and set `sitemap_curation_status` to `Selected`)
  - **Services:** `src/services/business_to_domain_service.py` (The *producer* for this workflow; creates the `Domain` record from a `LocalBusiness`)
  - **Schedulers:** N/A (The handoff to WF5 is triggered directly by the user in the router, not a background scheduler)
- **WF5 - Sitemap Curation & Analysis:**
  - **Models:** `src/models/job.py` (Defines the `Job` created for each website scan)
  - **Routers:** N/A (This is a background processing workflow with no direct user curation component identified yet)
  - **Services:** `src/services/website_scan_service.py` (The *producer* for this workflow; creates the `Job` record to track the scan)
  - **Schedulers:** `src/services/domain_sitemap_submission_scheduler.py` (The *consumer* for WF4; polls for domains with `sitemap_analysis_status = 'Pending'` and triggers the website scan)
- **WF6 - Email Scraping & Curation:**
  - **Models:** `src/models/contact.py`, `src/models/page.py` (Defines the final `Contact` and `Page` records produced by the scrape)
  - **Routers:** N/A (No user-facing curation component for `Contact` records has been identified in this audit)
  - **Services:** N/A (The core logic is contained within the task itself, not a separate service layer)
  - **Tasks:** `src/tasks/email_scraper.py` (The *producer* for this workflow; contains the `scan_website_for_emails` function that performs the scrape and creates `Contact` records)

## 5. Discrepancies & Technical Debt

- **[HIGH] WF4->WF5 Handoff Failure:** The `domains` router sets `sitemap_analysis_status` to `QUEUED`, but the `domain_sitemap_submission_scheduler` polls for `PENDING`. This mismatch will prevent any selected domains from being processed for sitemap analysis.
  - **Producer:** `src/routers/domains.py` (Line 226)
  - **Consumer:** `src/services/domain_sitemap_submission_scheduler.py` (Line 70)
- **[HIGH] WF1 Model-Table Mismatch:** The `Place` model is defined to use the `places_staging` table, but the canonical workflow for WF1 (`WF1-SingleSearch_CANONICAL.yaml`) explicitly requires the `places` table. This breaks the data handoff to WF2.
  - **Canonical Definition:** `WF1-SingleSearch_CANONICAL.yaml` (Line 10)
  - **Implementation:** `src/models/place.py` (Line 35)
- **[MEDIUM] WF1 Enum Mismatch:** The `Place` model uses the `PlaceStatus` enum, which does not conform to the canonical `PlaceStatusEnum` definition for WF1. The name is incorrect, and it is missing the required `Rejected` and `Processed` values.
  - **Canonical Definition:** `WF1-SingleSearch_CANONICAL.yaml` (Line 13)
  - **Implementation:** `src/models/enums.py` (Line 35)

## 6. Data Integrity & Foreign Key Validation (TODO)

*This section will confirm that database constraints enforce the workflow logic.*

- **WF2 consumes WF1:** Does `places_staging` have a mandatory foreign key to `place_searches`?
- **WF3 consumes WF2:** Does `local_businesses` have a mandatory foreign key to `places_staging`?
- ...and so on for all 6 workflows.

## 6. Risk & Technical Debt Register (TODO)

*This section will list identified risks and technical debt items per workflow.*

- **WF1:** [List any identified issues]
- **WF2:** [List any identified issues]
- **WF3:** [List any identified issues]
- **WF4:** [List any identified issues]
- **WF5:** [List any identified issues]
- **WF6:** [List any identified issues]
