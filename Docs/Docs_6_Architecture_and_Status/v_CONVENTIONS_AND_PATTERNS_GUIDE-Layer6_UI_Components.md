# ScraperSky Naming & Structural Conventions Guide - Layer 6: UI Components

**Date:** 2025-05-11
**Version:** 1.0

## Related Documentation

- **[1.0-ARCH-TRUTH-Definitive_Reference.md](./1.0-ARCH-TRUTH-Definitive_Reference.md)** - Definitive architectural reference
- **[2.0-ARCH-TRUTH-Implementation_Strategy.md](./2.0-ARCH-TRUTH-Implementation_Strategy.md)** - Implementation strategy for architectural alignment
- **[3.0-ARCH-TRUTH-Layer_Classification_Analysis_Concise.md](./3.0-ARCH-TRUTH-Layer_Classification_Analysis_Concise.md)** - Comprehensive analysis of layer classification
- **[Q&A_Key_Insights.md](./Q&A_Key_Insights.md)** - Clarifications on implementation standards

**Objective:** This document details the naming and structural conventions for Layer 6 components (UI Components) within the ScraperSky backend project. Adherence to these conventions is crucial for maintaining consistency, readability, and maintainability across the codebase.

---

## 7. Layer 6: UI Components

User interface component identifiers are primarily derived from `{workflowNameCamelCase}` to ensure uniqueness and predictability. **All new workflows MUST adhere strictly to these naming conventions to ensure consistency and proper functioning of associated JavaScript.**

- **Tab Button Text & Panel Header:**

  - **Convention (Tab Button):** Generally, the direct Title Case of `workflow_name` with spaces (e.g., "Page Curation" from `page_curation`).
  - **Convention (Panel Header):** If further clarity or disambiguation is needed (e.g., multiple workflows on the same entity), the panel header (`<h3>` or `<h4>`) can use a more descriptive text.
  - **Derivation:** Convert `workflow_name` to Title Case and replace underscores with spaces for the base tab button text.
  - **Example (`workflow_name = domain_curation`):**
    - Tab Button Text: "Domain Curation"
    - Panel Header Text (for clarity): "Domain Curation for Sitemap Analysis"
  - **Guideline:** The guiding principle for modifications in the panel header is function disambiguation. The tab button itself should aim for brevity.

- **Tab `data-panel` Attribute:**

  - **Convention:** `{workflowNameCamelCase}Panel`
  - **Derivation:** Convert `workflow_name` to `camelCase` and append "Panel".
  - **Strict Requirement:** **For all new workflows, adherence to this convention is mandatory.**
  - **Example (`workflow_name = page_curation`):** `pageCurationPanel`
  - **Reference:** The `domainCurationPanel` implementation (e.g., `static/scraper-sky-mvp.html` line 577 for tab, line 809 for panel) serves as a definitive example.

- **Panel `div` `id`:**

  - **Convention:** Must match the `data-panel` attribute: `{workflowNameCamelCase}Panel`.
  - **Derivation:** Same as Tab `data-panel` attribute.
  - **Strict Requirement:** **For all new workflows, adherence to this convention is mandatory.**
  - **Example (`workflow_name = page_curation`):** `pageCurationPanel`

- **Filter and Action Control IDs (General Pattern):**

  - **Mandatory Adherence:** The following ID patterns are **exact and mandatory** for all new workflows. The `domainCurationPanel` section in `static/scraper-sky-mvp.html` serves as the reference model.
  - Let `PanelBaseName = {workflowNameCamelCase}` (e.g., `pageCuration` from `page_curation`).
  - Let `PanelTitleCase = {WorkflowNameTitleCase}` (e.g., `PageCuration` from `page_curation`).
  - **Status Filter `select` `id`:** `{PanelBaseName}StatusFilter` (e.g., `pageCurationStatusFilter`)
  - **Name/Identifier Filter `input` `id`:** `{PanelBaseName}NameFilter` (e.g., `pageCurationNameFilter`). **Note:** The "Name" part can be adapted to the specific field being filtered (e.g., `domainCurationDomainFilter`, `sitemapUrlFilter`).
  - **Apply Filters Button `id`:** `apply{PanelTitleCase}FiltersBtn` (e.g., `applyPageCurationFiltersBtn`)
  - **Reset Filters Button `id`:** `reset{PanelTitleCase}FiltersBtn` (e.g., `resetPageCurationFiltersBtn`)

- **Data Table & Body (General Pattern):**

  - Let `PanelBaseName = {workflowNameCamelCase}`.
  - **Table `id`:** `{PanelBaseName}Table` (e.g., `pageCurationTable`)
  - **Table Body `tbody` `id`:** `{PanelBaseName}TableBody` (e.g., `pageCurationTableBody`)

- **Select All Checkbox `id` (General Pattern):**

  - Let `PanelBaseName = {workflowNameCamelCase}`.
  - **Convention:** `selectAll{PanelTitleCase}Checkbox` (e.g., `selectAllPageCurationCheckbox`)

- **Batch Update Controls (General Pattern):**

  - **Mandatory Adherence:** The following ID patterns are **exact and mandatory.**
  - Let `PanelBaseName = {workflowNameCamelCase}`.
  - Let `PanelTitleCase = {WorkflowNameTitleCase}`.
  - **Batch Controls `div` `id`:** `{PanelBaseName}BatchUpdateControls` (e.g., `pageCurationBatchUpdateControls`)
  - **Batch Status `select` `id`:** `{PanelBaseName}BatchStatusUpdate` (e.g., `pageCurationBatchStatusUpdate`)
  - **Apply Batch Update Button `id`:** `apply{PanelTitleCase}BatchUpdateBtn` (e.g., `applyPageCurationBatchUpdateBtn`)
  - **Clear Selection Button `id`:** `clear{PanelTitleCase}SelectionBtn` (e.g., `clearPageCurationSelectionBtn`)

- **Batch Status Dropdown Options (UI Text vs. Backend Value):**
  - **Context:** This defines how UI dropdown options for status updates relate to backend Enum values, particularly for triggering the dual-status update (CurationStatus -> ProcessingStatus).
  - **Standard for New Workflows (Using Standard Enums like `PageCurationStatus`):**
    - **UI Text:** The dropdown option text **MUST** use the actual backend Enum member value, with optional descriptive text in parentheses for clarity if the action is non-obvious.
      - **Format:** `"{EnumValueTitleCase} (Queue for {ProcessDescription})"` or `"{EnumValueTitleCase} (Start {ProcessDescription})"`.
      - **Example (Triggering processing):** If `PageCurationStatus.Queued` triggers processing, the UI option should be: `<option value="Queued">Queued (Start Processing)</option>` or `<option value="Queued">Queued (Queue for Page Processing)</option>`.
    - **JavaScript Behavior:** The JavaScript associated with this tab **MUST** send the exact `value` selected in the dropdown (e.g., "Queued") to the API endpoint. **No client-side translation of UI text to a different backend Enum value is permitted for new standard workflows.**
    - **API Behavior:** The API endpoint will receive this exact Enum string (e.g., "Queued") and use it to update the `curation_status` field. The dual-status update logic (setting `processing_status` to `Queued`) is triggered within the API based on this received `curation_status` value.
  - **Rationale:** This ensures type safety with Pydantic validation at the API level and maintains a clear, direct link between the UI selection and the backend Enum value, simplifying the dual-status update mechanism.
  - **Legacy Note:** Older workflows might exhibit different patterns (e.g., UI "Selected" mapping to a backend "Selected" status which then triggers queuing). These are considered technical debt if they don't align with the standard Enum values (`New, Queued, Processing, Complete, Error, Skipped`). New workflows MUST use "Queued" as the primary CurationStatus value to trigger the processing queue.
