
# Work Order: End-to-End Verification of WF5-WF6 Pipeline

**Date:** 2025-08-07
**Issued To:** L7 Test Sentinel (Environment-Aware Guardian v1.4)
**Issued By:** The Architect
**DART Task:** `[Link to DART Task]`

---

## 1.0 Mandate

It has been asserted that the WF5->WF6 data pipeline is fully functional. As The Architect, I require empirical proof. Your mission is to design and execute a comprehensive, environment-aware test plan to verify this claim from end to end, with zero risk to production systems.

This work order is issued under the authority of the ScraperSky Development Constitution, Article I, and leverages your unique capabilities as the Environment-Aware Test Sentinel (v1.4).

## 2.0 Test Objectives

1.  **Prove the Dual-Status Update Pattern:** Confirm that updating a `SitemapFile`'s `deep_scrape_curation_status` to `Selected` via the API correctly sets the `sitemap_import_status` to `Queued`.
2.  **Prove the Background Scheduler Consumption:** Confirm that the `sitemap_import_scheduler` correctly identifies and processes `SitemapFile` records in the `Queued` state.
3.  **Prove the Service Layer Logic:** Confirm that the `SitemapImportService` correctly downloads, parses, and creates `Page` records from the target sitemap file.
4.  **Prove Data Integrity:** Confirm that the newly created `Page` records are correctly associated with their parent `SitemapFile` and `Domain`.
5.  **Prove Final State Transition:** Confirm the `sitemap_import_status` of the `SitemapFile` is set to `Complete` upon successful processing.

## 3.0 Environment & Safety Protocols (The WF7 Covenant)

**This is non-negotiable.** All testing must adhere to the Docker-First Testing doctrine.

1.  **Environment:** All operations will be conducted within the isolated Docker development environment (`docker-compose.yml`). At no point shall any test interact with production resources.
2.  **Verification Before Action:** Before executing any test that modifies data, you must first verify the existence and current state of all required components (database records, API endpoints) using read-only operations.
3.  **Health Checks:** The test sequence must begin with a health check (`/health` and `/health/db`) to ensure the environment is stable.

## 4.0 Test Plan

You are to devise the precise execution steps, but they must follow this sequence:

### Phase 1: Setup & Pre-flight Checks

1.  **Identify Test Candidate:** Write and execute a read-only script to find a suitable `SitemapFile` ID from the database. The ideal candidate should have a `sitemap_import_status` of `NULL` or any state other than `Complete`.
2.  **Generate Authentication:** Generate a valid, short-lived JWT to be used for the API call. Do not use hardcoded tokens.
3.  **Initial State Verification:** Log the initial state of the target `SitemapFile` record for later comparison.

### Phase 2: Execution (WF5 Trigger)

1.  **Simulate User Action:** Execute a `PUT` request to the `/api/v3/sitemap-files/status` endpoint, passing the selected `SitemapFile` ID and setting the `curation_status` to `Selected`.
2.  **Verify Queued State:** Immediately after the API call, query the database and verify that the `sitemap_import_status` for the target `SitemapFile` has been updated to `Queued`.

### Phase 3: Execution (WF6 Trigger & Processing)

1.  **Trigger Scheduler:** Manually invoke the `process_pending_sitemap_imports` job. You may need to create a temporary script or use a debug endpoint for this. Do not wait for the natural interval.
2.  **Monitor Processing:** Observe the application logs (`docker-compose logs -f`) to monitor the progress of the `sitemap_import_scheduler` and `SitemapImportService`.

### Phase 4: Verification & Teardown

1.  **Verify Final `SitemapFile` State:** Query the database and confirm the `sitemap_import_status` is now `Complete` and the `sitemap_import_error` field is `NULL`.
2.  **Verify `Page` Creation:** Query the `pages` table to confirm that new records have been created with the correct `sitemap_file_id` and `domain_id`.
3.  **Data Integrity Check:** Spot-check one of the newly created `Page` records to ensure its URL is plausible based on the source sitemap.
4.  **Report Findings:** Document the entire process, including all commands, scripts, and query results, in a new Markdown file within your DART Journal. The report must clearly state whether the WF5->WF6 pipeline is confirmed as fully operational.

## 5.0 Required Tools

- `run_shell_command` (for `curl`, `docker-compose`, and executing scripts)
- `read_file`, `write_file` (for creating and managing test scripts)
- Your own persona's knowledge of safe testing patterns.

## 6.0 Acceptance Criteria

This work order is complete when a final report is generated and logged in your DART Journal, providing definitive, evidence-backed proof of the operational status of the WF5-WF6 pipeline.

---

**As The Architect, I delegate this critical verification task to you. The integrity of our system's documentation and my understanding of its state rests on the successful and safe execution of this order. Proceed with the caution and precision your station demands.**
