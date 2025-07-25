# WF4 Domain Curation - Guardian Impact Analysis

## ENUM Centralization Impact
- [ ] **SitemapCurationStatusEnum location:** `src/models/domain.py` → **Should be** in `src/models/enums.py`.
- [ ] **SitemapAnalysisStatusEnum location:** `src/models/domain.py` → **Should be** in `src/models/enums.py`.
- [ ] **Import updates needed in:** `src/routers/domains.py` and `src/models/domain.py` will need to update imports once the ENUMs are moved.
- [ ] **ENUM values preserved:** **No.** The `SitemapCurationStatusApiEnum` in `api_models.py` (used by the router) has values like "Selected", which conflict with the standardized ENUMs (`QUEUED`, `SKIPPED`) that the backend services and schedulers will expect. This is a critical logic break.

## Schema Layer Impact
- [ ] **`api_models.py` references found in:** `src/routers/domains.py` imports `DomainBatchCurationStatusUpdateRequest` from `api_models.py`.
- [ ] **`DomainBatchCurationStatusUpdateRequest` schema location:** `src/models/api_models.py` → **Should be** in `src/schemas/domain_curation.py`.
- [ ] **New schema files needed:** `src/schemas/domain_curation.py` should be created to house `DomainCurationBatchStatusUpdateRequest` and a corresponding `Response` model.
- [ ] **Import updates needed in:** `src/routers/domains.py`.

## WF4 File-by-File Status
- **`src/models/domain.py`:** **Needs updates.** Defines ENUMs locally. Suffers from the anti-pattern of inheriting from both `Base` and `BaseModel` and re-defining its `id` and `tenant_id`.
- **`src/models/api_models.py`:** **Needs migration.** Contains the request schema and a non-standard API-facing ENUM that must be reconciled and moved.
- **`src/routers/domains.py`:** **Needs updates.** Imports from incorrect locations. Uses non-standard ENUM values that break the handoff to the next workflow. Business logic for updating `sitemap_analysis_status` is improperly located in the router.

## Critical Issues Found
1.  **Fatal ENUM Mismatch:** The router (`domains.py`) uses a legacy ENUM from `api_models.py` with values like "Selected". The logic to trigger the next workflow (WF5/WF6 via a scheduler) will look for a standardized status like `QUEUED`. The handoff is broken.
2.  **Misplaced Business Logic:** The router contains the logic for setting the `sitemap_analysis_status` to `Queued`. This logic should be in a dedicated service layer to decouple it from the API.
3.  **Model and Schema Misplacement:** Core components (ENUMs, Schemas) are not in their architecturally mandated locations (`enums.py`, `schemas/`), indicating an incomplete refactor.

## Remediation Plan (NO EXECUTION)
1.  **Create Dedicated Service:** Create `src/services/domain_curation_service.py` and move the business logic for updating statuses from the `domains.py` router into this new service.
2.  **Reconcile and Move ENUMs:** Move `SitemapCurationStatusEnum` and `SitemapAnalysisStatusEnum` to `src/models/enums.py`. Delete the legacy `SitemapCurationStatusApiEnum` from `api_models.py` and refactor the `domains.py` router to use the standardized ENUMs.
3.  **Migrate Schemas:** Create `src/schemas/domain_curation.py`, move the request schema from `api_models.py` into it, and update the router's imports.
4.  **Correct Model Inheritance:** Refactor `src/models/domain.py` to inherit only from `BaseModel` and remove redundant field definitions.

## WF4 Interface Status
- **WF3→WF4 handoff (`domains` consumption):** **Working.** WF4 can read the `domain` records created by WF3.
- **WF4→WF5 handoff (`sitemap_analysis_status` production):** **Broken.** The trigger for the next workflow (sitemap analysis) is setting `sitemap_analysis_status` to `Queued`. This is supposed to happen when a user sets `sitemap_curation_status` to "Selected". Due to the ENUM mismatch, this trigger logic will fail.
