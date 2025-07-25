# WF6 Sitemap Import - Guardian Impact Analysis

## ENUM Centralization Impact
- [ ] **SitemapImportProcessStatusEnum location:** `src/models/sitemap.py` → **Should be** in `src/models/enums.py`.
- [ ] **PageStatusEnum location:** `src/models/page.py` → **Should be** in `src/models/enums.py`.
- [ ] **Import updates needed in:** `src/services/sitemap_import_scheduler.py`, `src/models/sitemap.py`, and `src/models/page.py`.

## Schema Layer Impact
- **N/A:** This is a background processing workflow and does not have its own dedicated API endpoint or schemas. Its interface is the database state.

## WF6 File-by-File Status
- **`src/models/sitemap.py`:** **Needs updates.** Defines an ENUM locally and has the `Base`/`BaseModel` inheritance anti-pattern.
- **`src/models/page.py`:** **Needs updates.** Defines an ENUM locally and has the `Base`/`BaseModel` inheritance anti-pattern.
- **`src/services/sitemap_import_scheduler.py`:** **Needs updates.** The core of this workflow. It needs its ENUM imports updated. Its database query uses a hardcoded string `status = 'queued'` which is brittle and should use the centralized ENUM for type safety.
- **`src/services/sitemap_import_service.py`:** **Needs updates.** This service (which contains the actual parsing logic) will need its ENUM imports updated.

## Critical Issues Found
1.  **Brittle Trigger Mechanism:** The scheduler's query (`SELECT ... WHERE sitemap_import_status = 'queued'`) uses a hardcoded string. This makes it completely dependent on the producer (WF5) using that exact string. Any change to the ENUM in the future would break this consumer without warning. The query should use the ENUM member itself for type-safe lookups.
2.  **Model Integrity Risks:** Both the consumed model (`SitemapFile`) and the produced model (`Page`) suffer from the critical `Base`/`BaseModel` inheritance flaw, risking database integrity.
3.  **Decentralized ENUMs:** The workflow's logic is spread across components that all define their own status ENUMs locally, violating the core architectural principle of centralization.

## Remediation Plan (NO EXECUTION)
1.  **Move ENUMs:** Move `SitemapImportProcessStatusEnum` (from `sitemap.py`) and `PageStatusEnum` (from `page.py`) to the central `src/models/enums.py`.
2.  **Update Imports:** Update all related files (`sitemap_import_scheduler.py`, `sitemap_import_service.py`, `sitemap.py`, `page.py`) to use the centralized ENUMs.
3.  **Type-Safe Query:** Refactor the query in `sitemap_import_scheduler.py` to use the ENUM member (e.g., `SitemapImportProcessStatusEnum.QUEUED.value`) instead of the hardcoded string `'queued'`. 
4.  **Correct Model Inheritance:** Refactor `src/models/sitemap.py` and `src/models/page.py` to inherit only from `BaseModel`.

## WF6 Interface Status
- **WF5→WF6 handoff (`sitemap_files` consumption):** **Broken.** The producer (WF5) is broken and will never set the `sitemap_import_status` to `Queued`. As a result, this scheduler will never find any records to process.
- **WF6→Future handoff (`pages` production):** **Broken.** Since the scheduler never runs, it never produces any `Page` records for downstream workflows to consume.
