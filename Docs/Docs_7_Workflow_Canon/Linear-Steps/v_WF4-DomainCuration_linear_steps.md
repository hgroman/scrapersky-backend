# Linear Steps: Workflow 4 – Domain Curation

_Last updated: 2025-05-04T23:14:35-07:00_

## Objective

Map every atomic step in the Domain Curation workflow (WF4) from Layer 6: UI Components to DB and background, referencing all files and actions. Annotate each file as [NOVEL] or [SHARED].

---

## 1. Layer 6: UI Components Initiation

- **User Action:** Selects domain(s) in the "Domain Curation" tab and sets status to "Selected".
  - File: `static/scraper-sky-mvp.html` [NOVEL]
  - File: `static/js/domain-curation-tab.js` [NOVEL]
  - Function: `applyDomainCurationBatchUpdate()` [NOVEL]

## 2. API Request

- **Action:** JS sends PUT request to `/api/v3/domains/sitemap-curation/status` with selected domain IDs and new status.
  - File: `static/js/domain-curation-tab.js` [NOVEL]

## 3. API Layer 3: Routers

- **Action:** FastAPI endpoint receives request and parses payload.
  - File: `src/routers/domains.py` [NOVEL]
  - Function: `update_domain_sitemap_curation_status_batch` [NOVEL]
  - Depends: `DomainBatchCurationStatusUpdateRequest` [SHARED], `get_db_session` [SHARED], `get_current_user` [SHARED]

## 4. DB Update & Status Logic

- **Action:**
  - Fetches Domain records by ID.
  - Sets `sitemap_curation_status = Selected`.
  - If status is 'Selected', sets `sitemap_analysis_status = Queued` and clears error.
  - Updates `updated_at`.
  - Commits transaction.
  - File: `src/routers/domains.py` [NOVEL]
  - Layer 1: Model: `Domain` [SHARED]
  - Layer 1: ENUM: `SitemapCurationStatusEnum`, `SitemapAnalysisStatusEnum` [SHARED]

## 5. Background Job Scheduling

- **Action:** APScheduler picks up domains with `sitemap_analysis_status = Queued`.
  - File: `src/services/domain_sitemap_submission_scheduler.py` [NOVEL]
  - Function: `process_pending_domain_sitemap_submissions` [NOVEL]
  - File: `src/scheduler_instance.py` [SHARED]

## 6. Sitemap Analysis

- **Action:** For each queued domain, performs sitemap analysis.
  - File: `src/scraper/sitemap_analyzer.py` [SHARED]
  - Class: `SitemapAnalyzer` [SHARED]
  - Function: `analyze_domain_sitemaps` [SHARED]

## 7. Sitemap Processing

- **Action:** Sitemap analysis is performed directly by SitemapAnalyzer.
  - File: `src/scraper/sitemap_analyzer.py` [SHARED]

## 8. Status/Result Update

- **Action:** Updates `domain.sitemap_analysis_status` to Processing/Completed/Error based on outcome.
  - File: `src/services/domain_sitemap_submission_scheduler.py` [NOVEL]
  - Layer 1: Model: `Domain` [SHARED]

---

## Atomic Steps Table

| Step | File/Function                                                                                  | Annotation |
| ---- | ---------------------------------------------------------------------------------------------- | ---------- |
| 1    | static/scraper-sky-mvp.html                                                                    | [NOVEL]    |
| 1    | static/js/domain-curation-tab.js                                                               | [NOVEL]    |
| 2    | static/js/domain-curation-tab.js                                                               | [NOVEL]    |
| 3    | src/routers/domains.py:update_domain_sitemap_curation_status_batch                             | [NOVEL]    |
| 3    | src/routers/domains.py:get_db_session                                                          | [SHARED]   |
| 3    | src/routers/domains.py:get_current_user                                                        | [SHARED]   |
| 3    | src/models/domain.py:Domain                                                                    | [SHARED]   |
| 4    | src/models/domain.py:SitemapCurationStatusEnum                                                 | [SHARED]   |
| 4    | src/models/domain.py:SitemapAnalysisStatusEnum                                                 | [SHARED]   |
| 5    | src/services/domain_sitemap_submission_scheduler.py:process_pending_domain_sitemap_submissions | [NOVEL]    |
| 5    | src/scheduler_instance.py                                                                      | [SHARED]   |
| 6    | src/scraper/sitemap_analyzer.py:SitemapAnalyzer                                               | [SHARED]   |
| 6    | src/scraper/sitemap_analyzer.py:analyze_domain_sitemaps                                       | [SHARED]   |
| 7    | src/scraper/sitemap_analyzer.py                                                               | [SHARED]   |
| 8    | src/models/domain.py:Domain                                                                    | [SHARED]   |

---

## Architectural Mandates & Principles

- All DB status transitions are enforced via ORM.
- Background jobs must be idempotent, have retry logic, and explicit transaction boundaries.
- All errors and transitions are logged for auditability.
- All steps reference [NOVEL]/[SHARED] status from 3-python_file_status_map.md.

---

## TODOs / Known Issues

- [ ] If any ambiguity or missing artifact is found, log in Known Issues and update all maps.

---

**Reviewer:** ********\_\_\_\_********
**Date:** **********\_\_\_\_**********
