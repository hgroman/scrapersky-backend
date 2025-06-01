# ScraperSky Naming & Structural Conventions Guide - Layer 2: Schemas

**Date:** 2025-05-11
**Version:** 1.0

## Related Documentation

- **[1.0-ARCH-TRUTH-Definitive_Reference.md](./1.0-ARCH-TRUTH-Definitive_Reference.md)** - Definitive architectural reference
- **[2.0-ARCH-TRUTH-Implementation_Strategy.md](./2.0-ARCH-TRUTH-Implementation_Strategy.md)** - Implementation strategy for architectural alignment
- **[3.0-ARCH-TRUTH-Layer_Classification_Analysis.md](./3.0-ARCH-TRUTH-Layer_Classification_Analysis.md)** - Comprehensive analysis of layer classification
- **[Q&A_Key_Insights.md](./Q&A_Key_Insights.md)** - Clarifications on implementation standards

**Objective:** This document details the naming and structural conventions for Layer 2 components (Pydantic Schemas) within the ScraperSky backend project. Adherence to these conventions is crucial for maintaining consistency, readability, and maintainability across the codebase.

---

## 3. Layer 2: Schemas

Pydantic schemas are used to define the structure of API request and response bodies, ensuring data validation and clear contracts.

- **File Names:**

  - **Primary Convention (Mandatory for New Workflows):** For Pydantic schemas related to specific workflow actions (e.g., batch status updates, workflow-specific request/response models), the file **MUST** be named `src/schemas/{workflow_name}.py`.
    - **Rationale:** This aligns with clear separation of concerns and emphasizes the workflow-specific nature of these operations.
    - **Example (`workflow_name = page_curation`):** `src/schemas/page_curation.py` (contains `PageCurationUpdateRequest`, `PageCurationUpdateResponse`).
  - **Secondary Convention (for Generic Entity Schemas):** If schemas are genuinely generic, intended for reuse by _other distinct workflows_, or define core CRUD operations for an entity (unrelated to a specific workflow's actions), they should be placed in `src/schemas/{source_table_name}.py`.
    - **Example (`source_table_name = sitemap_file`):** `src/schemas/sitemap_file.py` (contains generic `SitemapFileBase`, `SitemapFileCreate`, `SitemapFileRead`).
    - **Note:** Workflow-specific schemas (like batch updates) should _not_ reside in these entity-based files, even if they operate on that entity.

- **Request & Response Model Naming (for Workflow-Specific Actions):**
  - **Strict Naming Convention (Mandatory for New Workflows):**
    - **Prefix:** Models **MUST** use the `{WorkflowNameTitleCase}` prefix. This ensures clarity and consistency with Python Enum naming (Section 4). Using `{SourceTableTitleCase}` for workflow-specific action schemas is generally incorrect unless the schema is truly generic and resides in a `{source_table_name}.py` file (see above).
    - **Suffixes:** Request models **MUST** end with "Request". Response models **MUST** end with "Response".
    - **Core Structure:**
      - Request: `{WorkflowNameTitleCase}[ActionDescription][Batch]Request`
      - Response: `{WorkflowNameTitleCase}[ActionDescription][Batch]Response`
    - **Specific Example (Batch Status Update):**
      - Request: `{WorkflowNameTitleCase}BatchStatusUpdateRequest`
        - **Example (`workflow_name = page_curation`):** `PageCurationBatchStatusUpdateRequest`.
      - Response: `{WorkflowNameTitleCase}BatchStatusUpdateResponse`
        - **Example (`workflow_name = page_curation`):** `PageCurationBatchStatusUpdateResponse`.
    - **Example (Single Item Update/Create - if needed specifically for a workflow beyond generic CRUD):**
      - Request: `{WorkflowNameTitleCase}StatusUpdateRequest`, `{WorkflowNameTitleCase}CreateRequest`
      - Response: `{WorkflowNameTitleCase}StatusUpdateResponse`, `{WorkflowNameTitleCase}CreateResponse`
  - **Example (from `src/schemas/page_curation.py`):**
    - `PageCurationUpdateRequest`
    - `PageCurationUpdateResponse`
  - **Technical Debt:** Existing schemas like `SitemapFileBatchUpdate` (in `sitemap_file.py`) that do not use the `{WorkflowNameTitleCase}` prefix for a workflow-specific action or omit the "Request"/"Response" suffix are considered technical debt. It should ideally be in a `sitemap_import.py` schema file and named `SitemapImportBatchUpdateRequest`.
