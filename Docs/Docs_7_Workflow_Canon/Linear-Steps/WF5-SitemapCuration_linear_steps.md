# Linear Steps: Workflow 5 – Sitemap Curation

_Last updated: 2025-05-05T00:40:15-07:00_

## Objective

Map every atomic step in the Sitemap Curation workflow (WF5) from Layer 6: UI Components to DB and background, referencing all files and actions. Annotate each file as [NOVEL] or [SHARED].

---

## 1. Layer 6: UI Components Initiation

- **User Action:** Selects sitemap file(s) in the "Sitemap Curation" tab and sets status to "Selected".
  - File: `static/scraper-sky-mvp.html` [NOVEL]
  - File: `static/js/sitemap-curation-tab.js` [NOVEL]
  - Function: (Likely) `sitemapBatchUpdate()` [NOVEL]

## 2. API Request

- **Action:** JS sends PUT request to `/api/v3/sitemap-files/status` with selected sitemap file IDs and new status.
  - File: `static/js/sitemap-curation-tab.js` [NOVEL]

## 3. API Layer 3: Routers

- **Action:** FastAPI endpoint receives request and delegates to service.
  - File: `src/routers/sitemap_files.py` [NOVEL]
  - Function: `update_sitemap_files_status_batch` [NOVEL]
  - Depends: `SitemapFileBatchUpdate` [SHARED], `get_db_session` [SHARED], `get_current_user` [SHARED]

## 4. Layer 4: Services Logic

- **Action:** Service updates status with Dual-Status Update Pattern.
  - File: `src/services/sitemap_files_service.py` [NOVEL]
  - Function: `update_curation_status_batch` [NOVEL]
  - Updates primary status `deep_scrape_curation_status` = "Selected".
  - If status is "Selected", also sets `sitemap_import_status` = "Queued".

## 5. Database Update

- **Action:** ORM updates sitemap_files table with new statuses.
  - File: `src/services/sitemap_files_service.py` [NOVEL]
  - Layer 1: Model: `SitemapFile` [SHARED]
  - Layer 1: ENUM: `SitemapImportCurationStatusEnum`, `SitemapImportProcessStatusEnum` [SHARED]

## 6. Background Job Scheduler (CLARIFICATION - VERIFIED)

- **Action:** Separate scheduler process handles the queued sitemap files
  - File: `src/services/sitemap_import_scheduler.py` [SHARED]
  - Function: `process_pending_sitemap_imports` specifically handles SitemapFile objects
  - Notes: This is not a gap but a different architectural pattern. Unlike other workflows which use the shared `sitemap_scheduler.py`, this workflow uses a dedicated scheduler:
    - WF5 ends by setting `sitemap_import_status = 'Queued'`
    - WF6 begins with `sitemap_import_scheduler.py` polling these queued records
    - This separation provides cleaner code organization but was not clearly documented

## 7. Deep Scrape Processing (VERIFIED)

- **Action:** SitemapImportService processes queued sitemap files
  - File: `src/services/sitemap_import_service.py` [SHARED]
  - Function: `process_single_sitemap_file` fetches, parses and processes the sitemap file
  - This step is reached through the WF6-Sitemap Import workflow
  - Note: The processing is implemented as a separate workflow (WF6) which creates a clean separation of concerns

---

## Atomic Steps Table

| Step | File/Function                                                      | Annotation |
| ---- | ------------------------------------------------------------------ | ---------- |
| 1    | static/scraper-sky-mvp.html                                        | [NOVEL]    |
| 1    | static/js/sitemap-curation-tab.js                                  | [NOVEL]    |
| 2    | static/js/sitemap-curation-tab.js                                  | [NOVEL]    |
| 3    | src/routers/sitemap_files.py:update_sitemap_files_status_batch     | [NOVEL]    |
| 3    | src/routers/sitemap_files.py:get_db_session                        | [SHARED]   |
| 3    | src/routers/sitemap_files.py:get_current_user                      | [SHARED]   |
| 3    | src/models/sitemap_file.py:SitemapFileBatchUpdate                  | [SHARED]   |
| 4    | src/services/sitemap_files_service.py:update_curation_status_batch | [NOVEL]    |
| 5    | src/models/sitemap.py:SitemapFile                                  | [SHARED]   |
| 5    | src/models/sitemap.py:SitemapImportCurationStatusEnum              | [SHARED]   |
| 5    | src/models/sitemap.py:SitemapImportProcessStatusEnum               | [SHARED]   |
| 6    | src/services/sitemap_scheduler.py:process_pending_jobs             | [SHARED]   |
| 6    | src/scheduler_instance.py                                          | [SHARED]   |

---

## Architectural Mandates & Principles

- All DB status transitions are enforced via ORM.
- All API endpoints use `/api/v3/` prefix as required.
- Router owns transaction boundaries according to architecture mandate.
- Background jobs should be idempotent and have transaction boundaries (but implementation is missing).
- JWT authentication happens only at API gateway endpoints.

---

## Known Issues / To-Dos

- [RESOLVED] The sitemap files with status "Queued" are picked up by a separate dedicated scheduler (`sitemap_import_scheduler.py`) as part of WF6.
- [RESOLVED] The processing service exists as `sitemap_import_service.py` which is part of WF6-Sitemap Import workflow.
- The transaction management in router appears correct but should be further verified.
- [DOCUMENTATION] Add clear documentation about the handoff between WF5 and WF6.

---

**Reviewer:** Cascade AI
**Date:** 2025-05-05T00:40:15-07:00
