# Workflow Standardization & Convention Clarification Questions

**Objective:** This document lists questions derived from the `CONVENTIONS_AND_PATTERNS_GUIDE.md`. The goal is to establish definitive, standardized answers that apply to the construction of any new workflow within the ScraperSky project. These answers will further refine our understanding and ensure consistency.

---

## 1. Base Identifiers

**Context:** These are foundational names. (`workflow_name`, `source_table_name`).

1.  **Q1.1:** When a new workflow is conceived, what is the exact process or authority for determining and assigning its official `workflow_name`?
2.  **Q1.2:** Similarly, what is the process for determining the official `source_table_name` if it's a new table or if an existing table is chosen?
3.  **Q1.3:** Are there any reserved keywords or prohibited patterns for `workflow_name` or `source_table_name`?
4.  **Q1.4:** How are pluralizations for `source_table_plural_name` consistently handled for irregular nouns or when unsure? Is there a reference or standard English pluralization library/rule-set we adhere to?

---

## 2. UI Components (`static/scraper-sky-mvp.html`)

**Context:** Naming conventions for HTML elements.

1.  **Q2.1 (Tab Button Text):** The convention is "Title Case of `workflow_name` with spaces." Is this always a direct conversion, or are there exceptions for very long `workflow_name`s or specific desired phrasing?
2.  **Q2.2 (Tab `data-panel` & Panel `id`):** The convention `{workflowNameCamelCase}Panel` seems consistent (e.g., `domainCurationPanel`). Is this the absolute standard, or are there scenarios (e.g., very long names) where an abbreviation might be preferred? If so, what's the abbreviation rule?
3.  **Q2.3 (Filter/Button IDs):** The pattern `{PanelBaseName}StatusFilter`, `apply{WorkflowNameTitleCase}FiltersBtn` is derived. Is this derivation rule fixed, or are there cases for deviation?
4.  **Q2.4 (Dropdown Options):** For the batch status update dropdown (e.g., `{PanelBaseName}BatchStatusUpdate`), should the displayed text for each option always be the exact string value of the corresponding `{WorkflowName}CurationStatus` Enum member (e.g., "New", "Queued")? Or can it be more descriptive (e.g., "Selected (Queue for X)")? If descriptive, what's the guideline?

---

## 3. JavaScript Files & Variables (`static/js/`)

**Context:** JS file naming and internal scoping.

1.  **Q3.1 (File Names):** Convention `{workflow_name_with_hyphens}-tab.js`. Is this universally applied?
2.  **Q3.2 (Internal Scoping):** The guide suggests a prefix/suffix for internal JS variables/functions (e.g., `{workflowNameCamelCase}`). Is this a strict requirement? If so, should a specific prefixing/suffixing strategy be mandated (e.g., always prefix with `wf{WorkflowNameTitleCase}_`)?
3.  **Q3.3 (Cloning vs. New):** When creating JS for a new tab, what are the guidelines for cloning an existing JS file (e.g., `domain-curation-tab.js`) versus creating one from scratch or a minimal template? What specific sections _must_ be customized?

---

## 4. Python Backend - Models (`src/models/`)

**Context:** Model files, SQLAlchemy classes, Enums, and column names.

1.  **Q4.1 (Status Enum Naming):** The guide says `PageCurationStatus` for `page_curation`. If a `workflow_name` is `foo_bar_baz_curation` and the `source_table_name` is `items`, would the Enum be `FooBarBazCurationStatus` or `ItemCurationStatus`? What's the definitive rule for choosing between `{WorkflowNameTitleCase}CurationStatus` and `{SourceTableTitleCase}CurationStatus`?
2.  **Q4.2 (Standard Enum Values):** The `CONVENTIONS_AND_PATTERNS_GUIDE.md` and the original cheat sheet mandate `New, Queued, Processing, Complete, Error, Skipped` for Curation and `Queued, Processing, Complete, Error` for Processing. Are these _the only_ allowed values for _any_ new standard workflow built with this system? Can a workflow introduce a _new_ curation status (e.g., "ArchivedAsComplete") not in this list, or must it use only these?
3.  **Q4.3 (Column Naming for Non-Standard Statuses):** If a workflow legitimately requires an _additional, non-standard_ status field (beyond `{workflow_name}_curation_status` and `{workflow_name}_processing_status`), what is the naming convention for that column and its corresponding Python Enum and DB ENUM type?

---

## 5. Python Backend - Database ENUM Types (PostgreSQL)

**Context:** Naming of DB ENUM types.

1.  **Q5.1 (DB ENUM Naming):** Conventions `{workflow_name}curationstatus` and `{workflow_name}processingstatus`. Is this always a direct concatenation without any modification to the `workflow_name` string, regardless of its length or complexity?

---

## 6. Python Backend - Schemas (Pydantic - `src/schemas/`)

**Context:** Schema file and Pydantic model naming.

1.  **Q6.1 (Schema File Location):** `{workflow_name}.py` OR `source_table_name.py`. What are the precise criteria for choosing one over the other? Is it based on the number of schemas or their specificity?
2.  **Q6.2 (Request/Response Model Naming):** The guide offers alternatives like `{WorkflowNameTitleCase}BatchStatusUpdateRequest` OR `{SourceTableTitleCase}BatchCurationUpdateRequest`. What's the rule to pick one? Should it always include "Batch" if it's a batch operation? Should "Curation" be part of it if it's updating the curation status?

---

## 7. Python Backend - Routers (`src/routers/`)

**Context:** Router file naming, endpoint paths, and function names.

1.  **Q7.1 (Router File Location):** `{workflow_name}.py` OR `source_table_plural_name}.py`. Similar to schemas, what are the precise criteria for this choice?
2.  **Q7.2 (Endpoint Path - Specific Action):** For the batch status update, the path segment is `/{workflow_name}/status` or `/status`. When is the `/{workflow_name}` prefix for the action part omitted? Is it only if the router file itself is already named `{workflow_name}.py`?
3.  **Q7.3 (Endpoint Function Naming):** `update_{source_table_name}_{workflow_name}_status_batch`. Is the `_{source_table_name}_` part always required, or can it be omitted if the router is already specific to that source table (e.g., in `pages.py`)?

---

## 8. Python Backend - Services (`src/services/`)

**Context:** Service and scheduler file/function naming.

1.  **Q8.1 (Scheduler File):** The guide mentions dedicated schedulers (`{workflow_name}_scheduler.py`) are preferred for new workflows over shared ones. Is creating a new dedicated scheduler file a strict requirement for every new workflow that involves background processing, or are there conditions where adding to an existing shared scheduler is acceptable/preferred?
2.  **Q8.2 (Scheduler Function Name):** `process_{workflow_name}_queue`. If a more descriptive name is used (e.g., `process_pending_domain_sitemap_submissions`), what's the guideline for that description part?
3.  **Q8.3 (Processing Service Function Name):** `process_single_{source_table_name}_for_{workflow_name}`. Is this structure fixed?

---

## 9. Documentation Files

**Context:** Naming of canonical YAMLs, linear steps, etc.

1.  **Q9.1 (Workflow Numbering `WF{Number}-`):** Is there a central registry or method for assigning the `{Number}` to ensure uniqueness and sequence?
2.  **Q9.2 (Main Identifier Segment):** For `WF{Number}-{WorkflowNameNoSpacesTitleCase}_CANONICAL.yaml`, if the `workflow_name` is long (e.g., `automated_page_content_categorization_curation`), would it be `WFXX-AutomatedPageContentCategorizationCuration_CANONICAL.yaml`, or is there a rule for acceptable abbreviation for file naming?
3.  **Q9.3 (Consistency across Doc Types):** The "Main Workflow Identifier Segment" seems to vary slightly between Canonical YAMLs (NoSpacesTitleCase) and Dependency Traces (Title Case With Spaces). Should these be made more uniform, or is the current variation intentional?

---

## 10. Key Architectural Patterns

**Context:** Ensuring patterns are consistently applied and documented.

1.  **Q10.1 (Dual-Status Trigger):** The `CONVENTIONS_AND_PATTERNS_GUIDE.md` states for dual-status update: "Determine if the `request.status` value should trigger background processing. This typically occurs if `request.status == {WorkflowName}CurationStatus.Selected` (or `.Queued` if that's a direct curation option as per the cheat sheet's standard Enum)."
    For a _new_ workflow following the standard `PageCurationStatus` (`New, Queued, Processing, Complete, Error, Skipped`), which of _these_ values, when set by the user via the API, should trigger the `{workflow_name}_processing_status` to be set to `Queued`? Is it always the `Queued` member of `PageCurationStatus`, or a different one like `Selected` (which isn't in that standard enum)? This needs to be absolutely explicit.
2.  **Q10.2 (Transaction Boundaries in Services):** The guide mentions transaction boundaries are "within individual processing units in Schedulers/Services for background tasks." Does each call to a `process_single_{source_table_name}_for_{workflow_name}` function (from a scheduler loop) operate within its own new transaction, or does the scheduler's loop manage a transaction for a batch of such calls? The `sitemap_import_service.py` example implies per-item transaction management by the service function itself. Is this the standard?
3.  **Q10.3 (API Response for Batch Updates):** The guide suggests `queued_count` in the API response. Is it mandatory for the API endpoint (Phase 2) to always return how many items were set to the "processing" queue as a result of the primary curation status update?

---

## 11. General & Process

1.  **Q11.1 (Deviation Protocol):** If a developer believes a standard convention is not suitable for a specific, justifiable reason in a new workflow, what is the formal process for proposing, reviewing, and approving a deviation?
2.  **Q11.2 (Guide Updates):** When a new pattern is agreed upon or an existing one refined (perhaps through answering these questions), what is the process for updating the `CONVENTIONS_AND_PATTERNS_GUIDE.md` and communicating these changes?
3.  **Q11.3 (Addressing Technical Debt):** When existing code that deviates from these established (or newly clarified) conventions is encountered, what is the standard operating procedure? Is a JIRA ticket always created? Is there a specific "technical debt" epic or label?

---

This list of questions should help solidify the standards.
