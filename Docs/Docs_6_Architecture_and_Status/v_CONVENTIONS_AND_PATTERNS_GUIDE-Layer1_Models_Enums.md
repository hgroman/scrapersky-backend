# ScraperSky Naming & Structural Conventions Guide - Layer 1: Models & ENUMs

**Date:** 2025-05-11
**Version:** 1.0

## Related Documentation

- **[1.0-ARCH-TRUTH-Definitive_Reference.md](./1.0-ARCH-TRUTH-Definitive_Reference.md)** - Definitive architectural reference
- **[2.0-ARCH-TRUTH-Implementation_Strategy.md](./2.0-ARCH-TRUTH-Implementation_Strategy.md)** - Implementation strategy for architectural alignment
- **[3.0-ARCH-TRUTH-Layer_Classification_Analysis_Concise.md](./3.0-ARCH-TRUTH-Layer_Classification_Analysis_Concise.md)** - Comprehensive analysis of layer classification
- **[Q&A_Key_Insights.md](./Q&A_Key_Insights.md)** - Clarifications on implementation standards

**Objective:** This document details the naming and structural conventions for Layer 1 components (SQLAlchemy Models and Python ENUMs) within the ScraperSky backend project. Adherence to these conventions is crucial for maintaining consistency, readability, and maintainability across the codebase.

---

## 2. Layer 1: Models & ENUMs

- **File Names:**

  - **Convention:** `source_table_name.py` (singular, snake_case).
  - **Derivation:** Based on the primary data entity.
  - **Example (`source_table_name = page`):** `page.py`.

- **SQLAlchemy Model Class Names:**

  - **Convention:** `{SourceTableTitleCase}`.
  - **Derivation:** From `source_table_name`.
  - **Example (`source_table_name = page`):** `Page`.

- **Status Enum Python Class Names (e.g., CurationStatus, ProcessingStatus):**

  - **Strict Convention:** Python Enum classes for workflow-specific statuses **MUST** always be named using the `{WorkflowNameTitleCase}` prefix.
    - **Format:** `{WorkflowNameTitleCase}CurationStatus`, `{WorkflowNameTitleCase}ProcessingStatus`.
    - **Base Class:** These enums should inherit from `(str, Enum)`.
  - **Rationale:** This ensures clear association with the specific workflow and maintains universal consistency. Using `{SourceTableTitleCase}` as a prefix for these workflow-specific enums is incorrect.
  - **Example (for `workflow_name = page_curation`):** `PageCurationStatus`, `PageProcessingStatus` (defined in `src/models/page.py`).
  - **Technical Debt:** Existing deviations (e.g., `SitemapImportCurationStatusEnum` in `sitemap.py` using an "Enum" suffix and a different base class, or `SitemapCurationStatusEnum` in `domain.py` using a source table prefix) are considered technical debt and should be refactored.
  - **Standard Values (Mandatory for New Workflows):**
    - `{WorkflowNameTitleCase}CurationStatus`: Members **MUST** be `New = "New"`, `Queued = "Queued"`, `Processing = "Processing"`, `Complete = "Complete"`, `Error = "Error"`, `Skipped = "Skipped"`. No custom additions to this primary curation enum are permitted.
    - `{WorkflowNameTitleCase}ProcessingStatus`: Members **MUST** be `Queued = "Queued"`, `Processing = "Processing"`, `Complete = "Complete"`, `Error = "Error"`.

- **SQLAlchemy Column Names (Primary Status Fields on Model):**

  - **Curation Status Column:**
    - **Name:** `{workflow_name}_curation_status`.
    - **Example (`workflow_name = page_curation`):** `page_curation_status`.
    - **Type Definition Example:** `Column(PgEnum(PageCurationStatus, name="pagecurationstatus", create_type=False), nullable=False, server_default=PageCurationStatus.New.value, index=True)`
  - **Processing Status Column:**
    - **Name:** `{workflow_name}_processing_status`.
    - **Example (`workflow_name = page_curation`):** `page_processing_status`.
    - **Type Definition Example:** `Column(PgEnum(PageProcessingStatus, name="pageprocessingstatus", create_type=False), nullable=True, index=True)`
  - **Processing Error Column:**
    - **Name:** `{workflow_name}_processing_error`.
    - **Example (`workflow_name = page_curation`):** `page_processing_error`.
    - **Type Definition Example:** `Column(Text, nullable=True)`

- **Handling Justified Non-Standard User States (Additional Status Fields):**
  - **Context:** In rare, highly justified cases where a workflow requires an additional user-selectable state not covered by the standard `{WorkflowNameTitleCase}CurationStatus` Enum values (e.g., "On Hold," "Pending External Review") and this state does _not_ directly trigger the primary processing queue.
  - **Strict Mandate:** Such additional states **MUST NOT** modify the standard `{WorkflowNameTitleCase}CurationStatus` or `{WorkflowNameTitleCase}ProcessingStatus` Enums or their primary columns.
  - **Solution:** The additional state **MUST** be managed by:
    1.  A **new, separate status field** on the SQLAlchemy model.
    2.  A **new, dedicated Python Enum class** for this specific status purpose.
  - **Naming Convention for Additional Status Field:**
    - **Column Name:** `{workflow_name}_{status_purpose}_status` (e.g., `page_curation_review_status`).
    - **Python Enum Class Name:** `{WorkflowNameTitleCase}{StatusPurpose}Status` (e.g., `PageCurationReviewStatus`). This Enum defines the values for the additional status.
  - **Database ENUM Type:** A corresponding new PostgreSQL ENUM type would need to be manually created (e.g., `pagecurationreviewstatus`).
  - **Integration:** The update logic for this additional status is managed independently of the primary dual-status (curation/processing) flow unless explicitly designed to interact in a controlled manner.
  - **Discouragement & Justification:** Adding such fields is **strongly discouraged** to maintain simplicity. Implementation requires:
    - Significant justification for its necessity.
    - Formal review and approval.
    - Clear documentation of its purpose, values, and interaction logic in the workflow's canonical YAML and the `CONVENTIONS_AND_PATTERNS_GUIDE.md` itself if it becomes a recurring pattern.
