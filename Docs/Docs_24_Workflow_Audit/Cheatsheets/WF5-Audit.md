# WF5 Sitemap Curation - Guardian Impact Analysis

## ENUM Centralization Impact
- [ ] **SitemapImportCurationStatusEnum location:** `src/models/sitemap.py` → **Should be** in `src/models/enums.py`.
- [ ] **SitemapImportProcessStatusEnum location:** `src/models/sitemap.py` → **Should be** in `src/models/enums.py`.
- [ ] **SitemapDeepCurationStatusEnum location:** `src/models/sitemap.py` → **Should be** in `src/models/enums.py`.
- [ ] **Import updates needed in:** `src/routers/sitemap_files.py`, `src/services/sitemap_files_service.py`, and `src/models/sitemap.py` will need imports updated.

## Schema Layer Impact
- [ ] **`SitemapFileBatchUpdate` schema location:** `src/models/sitemap_file.py` → **Should be** in `src/schemas/sitemap_curation.py`.
- [ ] **New schema files needed:** `src/schemas/sitemap_curation.py` should be created to house `SitemapCurationBatchUpdateRequest` and a corresponding `Response` model.
- [ ] **Import updates needed in:** `src/routers/sitemap_files.py`.

## WF5 File-by-File Status
- **`src/models/sitemap.py`:** **Needs updates.** Defines three ENUMs locally. Inherits from both `Base` and `BaseModel`.
- **`src/models/sitemap_file.py`:** **Needs migration.** Contains a Pydantic schema that should be in the `schemas` directory.
- **`src/routers/sitemap_files.py`:** **Needs updates.** Imports schemas and ENUMs from incorrect locations.
- **`src/services/sitemap_files_service.py`:** **Needs updates.** Imports need to be updated to reflect centralized ENUMs.

## Critical Issues Found
1.  **Massive ENUM/Schema Misplacement:** This workflow is a prime example of the incomplete refactor. All of its ENUMs and its primary request schema are defined directly in the model layer, violating architectural principles.
2.  **Model Inheritance Violation:** The core `SitemapFile` model in `sitemap.py` has the critical `Base`/`BaseModel` dual inheritance flaw.
3.  **Broken Handoff Logic:** The trigger to queue a sitemap for import (WF6) is setting `sitemap_import_status` to `Queued`. This is supposed to happen when a user sets `deep_scrape_curation_status` to `Selected`. Because the ENUMs are not standardized and are defined locally, this cross-status logic is extremely brittle and likely to fail.

## Remediation Plan (NO EXECUTION)
1.  **Move All ENUMs:** Move `SitemapImportCurationStatusEnum`, `SitemapImportProcessStatusEnum`, and `SitemapDeepCurationStatusEnum` to `src/models/enums.py`.
2.  **Migrate Schema:** Create `src/schemas/sitemap_curation.py` and move the `SitemapFileBatchUpdate` schema into it, renaming for clarity.
3.  **Update All Imports:** Systematically update `sitemap_files.py`, `sitemap_files_service.py`, and `sitemap.py` to import from the new centralized locations.
4.  **Correct Model Inheritance:** Refactor `src/models/sitemap.py` to inherit only from `BaseModel`.

## WF5 Interface Status
- **WF4→WF5 handoff (`sitemap_files` consumption):** **Broken.** WF5 is never triggered because the producer (WF4) has a broken trigger mechanism due to its own ENUM conflicts.
- **WF5→WF6 handoff (`sitemap_import_status` production):** **Broken.** Even if WF5 were triggered, its internal logic for setting the `sitemap_import_status` to `Queued` is flawed due to using non-standard, locally-defined ENUMs. The handoff to the import scheduler (WF6) will not work.
