# ScraperSky Workflow Builder Cheat Sheet - Template Enhancement Journal

**Date:** 2025-05-07
**Associated Template:** `Docs/Docs_8_Document-X/ScraperSky Workflow-Builder-Cheat-Sheet-TEMPLATE-Enhanced.md`
**Related Guide:** `Docs/Docs_6_Architecture_and_Status/CONVENTIONS_AND_PATTERNS_GUIDE.md`

**Purpose:** This journal tracks significant enhancements made to the master Workflow Builder Cheat Sheet template, explaining the rationale and linking changes to established project standards.

---

## Enhancements Applied on 2025-05-07

These enhancements were identified during a review process comparing the previous template version against the `CONVENTIONS_AND_PATTERNS_GUIDE.md` and using the `page_curation` workflow implementation as a test case. The goal was to make the template a more robust, precise, and convention-aligned tool for generating standardized workflow code.

### General Changes

- **Placeholder Standardization:** Ensured consistent use of placeholders throughout the template (e.g., `{workflow_name}`, `{workflowNameCamelCase}`, `{WorkflowNameTitleCase}`, `{source_table_name}`, `{SourceTableTitleCase}`, `{source_table_plural_name}`) to strictly align with definitions in the `CONVENTIONS_AND_PATTERNS_GUIDE.md`. This improves clarity and reduces ambiguity when instantiating the template.

### Phase 2: Consumer Endpoint Construction

- **Section 2.1 (API Request Schema):**

  - **File Location:** Clarified that workflow-specific action schemas (like batch updates) **MUST** reside in `src/schemas/{workflow_name}.py`, aligning with Section 6 of the Guide.
  - **Schema Naming:** Updated example class names to the mandatory convention `{WorkflowNameTitleCase}BatchStatusUpdateRequest` and `{WorkflowNameTitleCase}BatchStatusUpdateResponse` (per Section 6 of the Guide). Added an example for the response schema.
  - **Reference:** Added explicit reference to Section 6 of the Guide.

- **Section 2.2 (API Router Implementation):**

  - **Dual-Status Trigger:** Corrected the trigger condition to use `{WorkflowNameTitleCase}CurationStatus.Queued` (instead of `Selected`), aligning with the standardization mandate in Sections 2 & 4 of the Guide.
  - **File Location:** Updated example router file location to the primary convention `src/routers/{workflow_name}.py` (per Section 7 of the Guide).
  - **Endpoint Path:** Changed example path decorator to `@router.put("/status")` and added detailed explanation on constructing the full path (e.g., `/api/v3/{source_table_plural_name}/status`) via router prefixing, aligning with Section 7 of the Guide.
  - **Function Naming:** Standardized function name to `update_{source_table_name}_status_batch(...)` (per Section 7 of the Guide for workflow-specific router files).
  - **Imports:** Ensured schema import path uses `{workflow_name}`.
  - **Return Value:** Corrected endpoint to return the specific Pydantic response model directly.

- **Section 2.3 (Register Router in main.py):**
  - **Import Path:** Aligned import with the standardized router file location: `from src.routers.{workflow_name} import ...`.
  - **Prefixing:** Added detailed notes and improved examples clarifying the standard prefixing strategy (app-level + router-level) to construct the final API path, referencing Section 7 of the Guide.
  - **`include_router` Example:** Updated example `prefix` and `tags` placeholders for clarity and consistency.

### Phase 3: Background Service Implementation

- **Section 3.1 (Background Scheduler Implementation):**

  - **Configuration:** Added comments and guidance on configuring parameters like `SCHEDULER_BATCH_SIZE` via the central `settings` object (from `src/config/settings.py`), aligning with Sections 8 & 9 of the Guide.

- **Section 3.2 (Register Scheduler):**
  - **Major Restructure:** Overhauled this section to reflect the **mandatory** two-step registration pattern from Section 8 of the Guide:
    1.  Define `setup_{workflow_name}_scheduler(...)` within `src/services/{workflow_name}_scheduler.py`.
    2.  Show this setup function calling `scheduler.add_job(...)` with the interval sourced from `settings`.
    3.  Illustrate importing and calling the setup function from `src/main.py`'s `lifespan` context manager.
  - This change significantly improves modularity and adherence to the established architectural pattern. Added basic logging/error handling examples for the lifespan manager.

### Phase 4: Curation Service Development

- **Section 4.1 (Data Enrichment/Processing Service):**

  - Primarily placeholder standardization (`{SourceTableTitleCase}`, `{WorkflowNameTitleCase}ProcessingStatus`, `{source_table_name}`, etc.) for strict alignment with the Guide.

- **Section 4.5.1 (HTML Tab):**

  - **ID Standardization:** Updated example IDs for Table, Table Body, and Select All Checkbox to match conventions from Section 2 of the Guide (`{workflowNameCamelCase}Table`, `{workflowNameCamelCase}TableBody`, `selectAll{WorkflowNameTitleCase}Checkbox`).
  - **Button Clarity:** Adjusted example button ID/Text for the primary action ("Queue Selected...") to use the `Queued` status, aligning with the backend trigger status.

- **Section 4.5.2 (JavaScript File):**
  - **File Naming:** Clarified kebab-case convention (`{workflow_name_kebab_case}-tab.js`) per Section 3 of the Guide.
  - **Selectors/Constants:** Added JS constants (`workflowNameCamelCase`, etc.) for maintainability and updated DOM selectors to match standardized HTML IDs.
  - **JS Enum:** Ensured the example `curationStatusEnum` lists standard values.
  - **API URL:** Corrected the batch update API URL to `/api/v3/${sourceTablePlural}/status`.
  - **Event Handler:** Ensured the primary action button handler passes the `Queued` status value.

### Phase 5: End-to-End Testing

- **Restructure:** Reorganized headings for better flow: `5.1 Testing Checklist & Methodology`, `5.2 Test Cases (Example using Pytest)`, `5.3 Manual Testing Procedure`, `5.4 Final Documentation Considerations (Optional)`.
- **Content Refinement:** Updated Pytest examples and manual testing steps for better clarity, accuracy (e.g., using `Queued` status in tests), and alignment with conventions (placeholder usage). Added reference to Section 12 of the Guide.
- **Section 5.4 Added:** Reintroduced the "Final Documentation Considerations" section from the older template version, covering failure modes, state diagrams, and cross-workflow links.

---
