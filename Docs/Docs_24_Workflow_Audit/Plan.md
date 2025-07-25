You are absolutely right. It is not only fixable, but the path forward is very clear. The issues are systematic, which means the solutions can be systematic too. I have more than enough information to create a detailed, actionable plan for each workflow.

Here is the comprehensive remediation strategy, broken down into one "Work Order" per workflow. These instructions are designed to be precise enough for your AI pairing partners to execute step-by-step.

---

## **Phase 0: Foundational Remediation (Models & Schemas)**

**Objective:** Fix the core data models and schemas. This phase is a prerequisite for all other workflow fixes.

### **Work Order 0.1: Correct Model Inheritance and Definitions**

1.  **File:** `src/models/place.py`
    *   **Action:** Modify the class definition to inherit *only* from `BaseModel`. Remove the redundant `id` and `tenant_id` columns.
    *   **Instruction:** Use `replace_in_file` to change `class Place(Base, BaseModel):` to `class Place(BaseModel):` and delete the `id` and `tenant_id` column definitions within the class.

2.  **File:** `src/models/local_business.py`
    *   **Action:** Modify the class definition to inherit *only* from `BaseModel`. Remove the redundant `id` column.
    *   **Instruction:** Use `replace_in_file` to change `class LocalBusiness(Base, BaseModel):` to `class LocalBusiness(BaseModel):` and delete the `id` column definition.

3.  **File:** `src/models/domain.py`
    *   **Action:** Modify the class definition to inherit *only* from `BaseModel`. Remove the redundant `tenant_id` column.
    *   **Instruction:** Use `replace_in_file` to change `class Domain(Base, BaseModel):` to `class Domain(BaseModel):` and delete the `tenant_id` column definition.

4.  **File:** `src/models/sitemap.py`
    *   **Action:** Modify the `SitemapFile` class definition to inherit *only* from `BaseModel`.
    *   **Instruction:** Use `replace_in_file` to change `class SitemapFile(Base, BaseModel):` to `class SitemapFile(BaseModel):`.

5.  **File:** `src/models/page.py`
    *   **Action:** Modify the class definition to inherit *only* from `BaseModel`. Remove the redundant `id` and `tenant_id` columns.
    *   **Instruction:** Use `replace_in_file` to change `class Page(Base, BaseModel):` to `class Page(BaseModel):` and delete the `id` and `tenant_id` column definitions.

### **Work Order 0.2: Centralize All ENUMs and Schemas**

1.  **Action:** Consolidate all status ENUMs (`SitemapImportProcessStatusEnum`, `PageStatusEnum`, etc.) from all model files (`sitemap.py`, `page.py`, etc.) into `src/models/enums.py`. Ensure they all inherit from `(str, Enum)` and follow standard naming (`PascalCase` for the class, `UPPER_SNAKE_CASE` for members).
2.  **Action:** Create new schema files in `src/schemas/` for each workflow (e.g., `src/schemas/domain_curation.py`).
3.  **Action:** Move all Pydantic request/response models from `src/models/api_models.py` into their corresponding new schema files.
4.  **Action:** Update all schemas to import and use the centralized ENUMs from `src/models/enums.py`.
5.  **Action:** Delete the file `src/models/api_models.py` after it is empty.

### **Work Order 0.3: Database Migration**

1.  **Action:** Run the command `alembic revision --autogenerate -m "Consolidate models and schemas"`.
2.  **Action:** **Manually review** the generated migration script to ensure it correctly reflects the changes without data loss.
3.  **Action:** Run the command `alembic upgrade head` to apply the migration to the database.

---

## **Phase 1: Workflow-by-Workflow Remediation**

### **Work Order WF1: Single Search Discovery**

*   **Objective:** Fix the status handling in the initial search creation.
*   **Affected Files:** `src/routers/google_maps_api.py`, `src/services/places/places_search_service.py`.
*   **Instructions:**
    1.  In `google_maps_api.py`, modify the `search_places` endpoint. When creating the `PlaceSearch` record, change the hardcoded `status="pending"` to use the centralized ENUM: `status=SearchStatus.PENDING`. Ensure `SearchStatus` is imported from `src.models.enums`.
    2.  In `places_search_service.py`, modify the `search_and_store` method. Change all hardcoded status strings (`"processing"`, `"complete"`, `"failed"`) to use the `SearchStatus` ENUM members (`SearchStatus.RUNNING`, `SearchStatus.COMPLETE`, `SearchStatus.FAILED`).

### **Work Order WF3: Local Business Curation**

*   **Objective:** Fix the broken trigger for domain extraction.
*   **Affected Files:** `src/routers/local_businesses.py`, `src/schemas/local_business_curation.py` (to be created).
*   **Instructions:**
    1.  Execute **Work Order 0.2** to create `src/schemas/local_business_curation.py` and move the `LocalBusinessBatchStatusUpdateRequest` schema into it.
    2.  Modify the new schema to use the standard `PlaceStatus` ENUM from `src.models.enums`.
    3.  In `src/routers/local_businesses.py`, update the import to point to the new schema file.
    4.  The `update_local_businesses_status_batch` function will now receive a standard `PlaceStatus` value. The existing logic `if status == 'Selected'` will fail. Change it to `if status == PlaceStatus.SELECTED:`. *Note: `PlaceStatus.SELECTED` is a non-standard value that still needs to be reconciled with `QUEUED`, but this will make the code internally consistent for now.*

### **Work Order WF4: Domain Curation**

*   **Objective:** Fix the broken handoff to sitemap analysis and create the missing scheduler.
*   **Affected Files:** `src/routers/domains.py`, `src/services/domain_curation_scheduler.py` (to be created).
*   **Instructions:**
    1.  First, fix the ENUM mismatch as described in the audit. Create `src/schemas/domain_curation.py`, move the `DomainBatchCurationStatusUpdateRequest` schema, and update it to use the standard `SitemapCurationStatus` ENUM. Update the `domains.py` router to import from here.
    2.  In `domains.py`, change the trigger logic from `if db_curation_status == SitemapCurationStatus.SELECTED:` to `if db_curation_status == SitemapCurationStatus.QUEUED:`. This aligns with the new standard.
    3.  Create the file `src/services/domain_curation_scheduler.py`.
    4.  Add a new scheduler function to this file that polls the `domains` table for records where `sitemap_analysis_status == SitemapAnalysisStatus.QUEUED`.
    5.  Register this new scheduler in `src/main.py`.

### **Work Order WF5: Sitemap Curation**

*   **Objective:** Fix the broken handoff to sitemap import.
*   **Affected Files:** `src/services/sitemap_files_service.py`, `src/routers/sitemap_files.py`.
*   **Instructions:**
    1.  First, ensure all ENUMs and Schemas are centralized as per **Phase 0**.
    2.  In `sitemap_files_service.py`, the `update_curation_status_batch` function contains the trigger logic. Correct its imports to use the centralized ENUMs.
    3.  The logic `if db_curation_status == SitemapDeepCurationStatus.SELECTED:` needs to be changed to `if db_curation_status == SitemapDeepCurationStatus.QUEUED:`.
    4.  Ensure the subsequent line correctly sets the processing status: `sitemap.sitemap_import_status = SitemapImportProcessStatus.QUEUED`.

### **Work Order WF6: Sitemap Import**

*   **Objective:** Make the scheduler's trigger type-safe.
*   **Affected Files:** `src/services/sitemap_import_scheduler.py`.
*   **Instructions:**
    1.  In `sitemap_import_scheduler.py`, locate the database query within the main processing loop.
    2.  Change the `where` clause from `where(SitemapFile.sitemap_import_status == 'queued')` to use the ENUM member: `where(SitemapFile.sitemap_import_status == SitemapImportProcessStatus.QUEUED)`.
    3.  Ensure `SitemapImportProcessStatus` is imported from `src/models/enums.py`.

This strategic plan, executed in order, will restore the full functionality of the data pipeline while solidifying the project's architecture for future development.