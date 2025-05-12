# ScraperSky Workflow Audit & Refactoring Cheat Sheet TEMPLATE

**Document Version:** 1.0
**Date:** {YYYY-MM-DD}
**Workflow Under Audit:** `{WorkflowName}` (e.g., `page_curation`, `sitemap_import`)
**Lead Auditor/Implementer:** {Your Name/Team}

## 0. Purpose & Pre-Requisites

**Purpose:** This document guides the systematic audit of the existing `{WorkflowName}` workflow against the ScraperSky `CONVENTIONS_AND_PATTERNS_GUIDE.md` and `Q&A_Key_Insights.md`. Its goal is to identify all technical debt and deviations, prescribe refactoring actions, and track the workflow's journey to full standardization. Upon completion, this document (or a derivative) should serve as the updated, authoritative "Workflow-Specific Cheat Sheet" for the now-standardized `{WorkflowName}`.

**Core Guiding Principles (from AI Collaboration Constitution & Project Work Order):**

- **Zero Assumptions:** If any aspect of the current state, the target standard, or the refactoring path is unclear, HALT and seek explicit clarification.
- **Document-First Iteration:** Findings and refactoring plans for each section should be documented _before_ extensive code changes are made. This sheet is the living record of that process.
- **Blueprint as Authority:** The `CONVENTIONS_AND_PATTERNS_GUIDE.md` and `Q&A_Key_Insights.md` are the final arbiters of the target state.

**Key Reference Documents for this Audit:**

1.  **Target Standard:** `Docs/Docs_6_Architecture_and_Status/CONVENTIONS_AND_PATTERNS_GUIDE.md`
2.  **Standard Clarifications:** `Docs/Docs_6_Architecture_and_Status/Q&A_Key_Insights.md`
3.  **Existing Workflow Analysis (if available, e.g., from `Docs/Docs_5_Project_Working_Docs/52-Gold-Standard-Blue-Print/`):**
    - `52.B-Analysis-Layer_Main_App_Integration.md` (for `{WorkflowName}` if covered)
    - `52.C-Analysis-Layer_API_Routers.md` (for `{WorkflowName}` if covered)
    - `52.D-Analysis-Layer_Services.md` (for `{WorkflowName}` if covered)
    - `52.E-Analysis-Layer_Data_Models.md` (for `{WorkflowName}` if covered)
4.  **Existing Workflow Files (e.g., `Docs/Docs_7_Workflow_Canon/workflows/WF<X>-{WorkflowName}_CANONICAL.yaml`):** {Link to specific canonical YAML if it exists}
5.  **Source Code:** Direct review of `src/` files related to `{WorkflowName}`.
6.  **Audit Log (if pre-existing issues noted):** `Docs/Docs_7_Workflow_Canon/Audit/WORKFLOW_AUDIT_JOURNAL.md`

---

## 1. Workflow Overview & Initial Assessment

### 1.1 Workflow Name & Core Details

- **Current Workflow Name (as in code/docs):** `{Actual_Current_Workflow_Name}`
- **Target Standardized Workflow Name (snake_case, as per Conventions Guide):** `{Standardized_Workflow_Name}`
  - _Note: This name will drive all other naming conventions._
- **Primary Source Table(s):** `{source_table_name(s)}`
- **Primary Purpose/Functionality:** {Brief description}
- **Key Entry Points (e.g., API routes, Scheduler job names):** {List current known entry points}

### 1.2 Overall Current State Summary & Major Known Issues

- {Summarize the general condition of this workflow based on prior knowledge or initial quick review. List any major technical debt areas already identified in `WORKFLOW_AUDIT_JOURNAL.md` or other analyses.}

---

## 2. Component-by-Component Audit & Refactoring Plan

**Strategic Note on Layer Prioritization:** To better inform the analysis of all architectural layers, the audit for each workflow will begin with Layer 4 (Services). The understanding gained from the service layer's logic and data handling will provide critical context for subsequently auditing other components. The methodology outlined in `Docs/Docs_10_Final_Audit/Layer-4-Service-Audit.md` should be referenced for conducting the Layer 4 audit when using this template.

For each component type below, assess the current state of the `{WorkflowName}` workflow, compare it to the standards, identify gaps, and plan refactoring actions.

### 2.1 Python Backend - Services (Processing Logic & Schedulers)

- **Relevant `CONVENTIONS_AND_PATTERNS_GUIDE.md` Section(s):** {e.g., Section 8}
- **Relevant `Q&A_Key_Insights.md` Section(s):** {"Python Backend - Services", "Python Backend - Task Management"}

| Service/Scheduler File(s) & Path(s)                   | Current State Assessment (Function Naming, Logic Separation, Registration)                                                                                                                                                                       | Standard Comparison & Gap Analysis (Deviations)                                                                                                                                                                                                                  | Prescribed Refactoring Actions                                                                                                                                                                                                                                                                              | Verification Checklist                                                                                                                                                                                                                                                                                                                                  | Status  |
| :---------------------------------------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | :------ |
| `src/services/{current_service_scheduler_name(s)}.py` | `{Describe current service/scheduler structure: Are scheduler and processing logic in same/separate files? Function names (`process*...\_queue`, `process_single*...`). Scheduler registration in `main.py`. Session handling. Settings usage.}` | `{List deviations: Scheduler file organization (dedicated `{workflow_name}\_scheduler.py`), function naming standards, separation of scheduling vs. processing logic, scheduler registration pattern, `get_background_session` usage, settings import pattern.}` | `{Detail actions: Create/rename files to standard (e.g., `{workflow_name}\_scheduler.py`, `{workflow_name}\_service.py`). Refactor functions to standard names. Separate logic. Implement `setup\*{workflow_name}\_scheduler()`function. Update`main.py` lifespan. Ensure correct session/settings usage.}` | `[ ] Dedicated `{workflow_name}\_scheduler.py`.<br>[ ] Scheduler function `process*{workflow_name}\_queue()`.<br>[ ] Processing function `process_single*{source_table_name}\_for*{workflow_name}`.<br>[ ] `setup*{workflow_name}\_scheduler()`implemented.<br>[ ] Correct registration in`main.py` lifespan.<br>[ ] Correct session & settings usage.` | `To Do` |

### 2.2 Python Backend - Models & ENUMs

- **Relevant `CONVENTIONS_AND_PATTERNS_GUIDE.md` Section(s):** {Specify section numbers, e.g., Section 4}
- **Relevant `Q&A_Key_Insights.md` Section(s):** {Specify, e.g., "Python Backend - Models", "Python Backend - Database ENUM Types"}

| Model File(s) & Path(s)                           | Current State Assessment (Key Classes, Fields, ENUMs)                                             | Standard Comparison & Gap Analysis (Deviations from Blueprint)                                                                                                   | Prescribed Refactoring Actions                                                                                                                                                                                                                | Verification Checklist                                                                                                                                                                                                                                                                                 | Status (To Do, In Progress, Done) |
| :------------------------------------------------ | :------------------------------------------------------------------------------------------------ | :--------------------------------------------------------------------------------------------------------------------------------------------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :-------------------------------- |
| **`src/models/{source_table_name}.py` (Primary)** | `{Briefly describe current model structure, status columns, ENUM definitions, location of ENUMs}` | `{List deviations: ENUM values, ENUM naming (Python & DB type), ENUM location, `create_type`usage, status column naming/types,`server_default`, indexing, etc.}` | `{Detail actions: Rename ENUMs, change ENUM values, move ENUM definitions to model file, update DB ENUM types (manual SQL step needed!), rename columns, set `create_type=False`, add/fix defaults/indexes. Specify exact new names/values.}` | `[ ] Python ENUM classes match standard values & naming (`{WorkflowName}CurationStatus`, etc.)<br>[ ] DB ENUM types match standard naming (`{workflow_name}curationstatus`, etc.)<br>[ ] ENUMs defined in model file.<br>[ ] `create_type=False` used.<br>[ ] Status columns correctly named & typed.` | `To Do`                           |
| **Other related model files (if any):**           | `{Describe}`                                                                                      | `{List deviations}`                                                                                                                                              | `{Detail actions}`                                                                                                                                                                                                                            | `{List checks}`                                                                                                                                                                                                                                                                                        | `To Do`                           |

### 2.3 Python Backend - Schemas (Pydantic)

- **Relevant `CONVENTIONS_AND_PATTERNS_GUIDE.md` Section(s):** {e.g., Section 6}
- **Relevant `Q&A_Key_Insights.md` Section(s):** {"Python Backend - Schemas (Pydantic)"}

| Schema File(s) & Path(s)                   | Current State Assessment (Key Request/Response Models)                                          | Standard Comparison & Gap Analysis (Deviations)                                                                                                                       | Prescribed Refactoring Actions                                                                                                                                                        | Verification Checklist                                                                                                                                                                                   | Status  |
| :----------------------------------------- | :---------------------------------------------------------------------------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :------ |
| `src/schemas/{workflow_name_or_entity}.py` | `{Describe current schema file structure, request/response model naming, use of `Batch`, etc.}` | `{List deviations: File location (workflow vs. entity specific), naming conventions (`{WorkflowNameTitleCase}Request`), use of `Batch` prefix/suffix, organization.}` | `{Detail actions: Rename/move files, rename schema classes, adjust fields to match new model definitions. Ensure workflow-specific schemas are in `src/schemas/{workflow_name}.py`.}` | `[ ] Workflow-specific schemas in `src/schemas/{workflow_name}.py`.<br>[ ] Request/Response models use `{WorkflowNameTitleCase}`prefix and`Request`/`Response`suffix.<br>[ ]`Batch` used appropriately.` | `To Do` |

### 2.4 Python Backend - Routers

- **Relevant `CONVENTIONS_AND_PATTERNS_GUIDE.md` Section(s):** {e.g., Section 7}
- **Relevant `Q&A_Key_Insights.md` Section(s):** {"Python Backend - Routers"}

| Router File(s) & Path(s)               | Current State Assessment (Endpoints, Function Naming, Patterns)                                                                                 | Standard Comparison & Gap Analysis (Deviations)                                                                                                                                                    | Prescribed Refactoring Actions                                                                                                                                                                            | Verification Checklist                                                                                                                                                                                                                                                  | Status  |
| :------------------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :------ |
| `src/routers/{current_router_name}.py` | `{Describe current router structure, endpoint paths, function names, transaction handling, dual-status update implementation (if applicable).}` | `{List deviations: File location/naming (e.g., `{workflow}_CRUD.py`standard), endpoint paths, function naming (e.g.,`update_{workflow}\_status_batch`), dual-status pattern, session dependency.}` | `{Detail actions: Rename/move router file. Standardize endpoint paths and function names. Implement/correct dual-status update logic. Ensure correct session dependency. Update `main.py` registration.}` | `[ ] Router file named `{workflow_name}\_CRUD.py`or`{workflow_name}.py` as appropriate.<br>[ ] Endpoint paths/functions follow standards.<br>[ ] Dual-status update correctly implemented.<br>[ ] Transaction management in router.<br>[ ] Correct session dependency.` | `To Do` |

### 2.5 Python Backend - Configuration & Environment Variables

- **Relevant `CONVENTIONS_AND_PATTERNS_GUIDE.md` Section(s):** {e.g., Section 10}
- **Relevant `Q&A_Key_Insights.md` Section(s):** {"Configuration and Environment Variables"}

| Configuration Aspect                              | Current State Assessment                                                                                                                    | Standard Comparison & Gap Analysis (Deviations)                                                                                                                                                                                       | Prescribed Refactoring Actions                                                                                                                                                  | Verification Checklist                                                                                                                                                              | Status  |
| :------------------------------------------------ | :------------------------------------------------------------------------------------------------------------------------------------------ | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :------ |
| **Env Var Naming & Loading for `{WorkflowName}`** | `{List current env vars used by this workflow (e.g., for scheduler interval/batch size). How are they named and loaded via `settings.py`?}` | `{List deviations: Env var naming (standard: `SCS*{WORKFLOW_NAME}*{SETTING_NAME}`or`{WORKFLOW_NAME}\_SCHEDULER\*{PARAMETER}`), definition in `Settings`class, inclusion in`.env.example`, access pattern (`settings.SOME_SETTING`).}` | `{Detail actions: Rename env vars. Update `src/config/settings.py`and`.env.example`. Ensure code uses the `settings` instance for access. Standardize scheduler config names.}` | `[ ] Env vars follow `SCS*{WORKFLOW_NAME}*{SETTING_NAME}`or specific scheduler pattern.<br>[ ] Defined in`Settings`class &`.env.example`.<br>[ ] Accessed via `settings` instance.` | `To Do` |

### 2.6 UI Components (HTML & JavaScript) - If Applicable

- **Relevant `CONVENTIONS_AND_PATTERNS_GUIDE.md` Section(s):** {e.g., Section 2 & 3}
- **Relevant `Q&A_Key_Insights.md` Section(s):** {"UI Components", "JavaScript Files & Variables"}

| Component Type & File(s)       | Current State Assessment                                                                                          | Standard Comparison & Gap Analysis (Deviations)                                                                                                                                                                                        | Prescribed Refactoring Actions                                                                                                                                                                                                                           | Verification Checklist                                                                                                                                                                                                                         | Status  |
| :----------------------------- | :---------------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :------ |
| **HTML Tab (`templates/...`)** | `{Describe current HTML structure for this workflow's tab, panel IDs, element IDs (table, buttons, checkboxes).}` | `{List deviations: Panel/element ID conventions (e.g., `{workflowNameCamelCase}Panel`, `apply{WorkflowNameTitleCase}FiltersBtn`), use of `domain-curation-tab.js` as reference for structure.}`                                        | `{Detail actions: Update HTML IDs to match strict conventions. Ensure structure aligns with de facto standard (`domain-curation-tab.js`).}`                                                                                                              | `[ ] Panel/element IDs match strict conventions.<br>[ ] Structure aligns with `domain-curation-tab.js` principles.`                                                                                                                            | `To Do` |
| **JS File (`static/js/...`)**  | `{Describe current JS file naming, variable/function naming, DOM selectors, API call structure, event handling.}` | `{List deviations: JS filename (`{workflow-name-kebab-case}-tab.js`), variable scoping/naming, DOM selector accuracy, comprehensiveness of updates if cloned from `domain-curation-tab.js`, API endpoint usage, status enum mapping.}` | `{Detail actions: Rename JS file. Update all variable/function names and DOM selectors. Ensure all aspects (API endpoints, comments, state variables) are specific to `{WorkflowName}`. Verify correct status enum usage directly without translation.}` | `[ ] JS filename is `{workflow_name_kebab_case}-tab.js`.<br>[ ] Variables/functions correctly named/scoped.<br>[ ] DOM selectors accurate.<br>[ ] All logic specific to `{WorkflowName}`.<br>[ ] Correct API endpoints and status enum usage.` | `To Do` |

### 2.7 Testing

- **Relevant `CONVENTIONS_AND_PATTERNS_GUIDE.md` Section(s):** {e.g., Section 12}
- **Relevant `Q&A_Key_Insights.md` Section(s):** {"Testing"}

| Test File(s) & Path(s)                                      | Current State Assessment (Coverage, Organization)                                               | Standard Comparison & Gap Analysis (Deviations)                                                                                                                                                                                                                                                                    | Prescribed Refactoring/Creation Actions                                                                                                                                                                                                                                  | Verification Checklist                                                                                                                                                                                                                                                   | Status  |
| :---------------------------------------------------------- | :---------------------------------------------------------------------------------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :------ |
| `tests/services/test_{current_workflow_name}_service.py`    | `{Describe existing service tests, coverage of processing logic, error handling, idempotency.}` | `{List deviations: File naming (`test\_{workflow_name}\_service.py`), missing high-priority coverage (service logic, scheduler logic), component-based organization, incremental testing methodology adherence, required test coverage for services/schedulers, workflow integration test presence/completeness.}` | `{Detail actions: Create/rename test files. Write new tests for service logic, scheduler interactions. Ensure component isolation and progressive testing. Implement workflow integration tests covering full lifecycle. Add fixtures. Address specific coverage gaps.}` | `[ ] Service tests in `test*{workflow_name}\_service.py`.<br>[ ] Scheduler tests in `test*{workflow_name}\_scheduler.py`.<br>[ ] High-priority components covered.<br>[ ] Workflow integration tests cover full lifecycle.<br>[ ] Adherence to incremental methodology.` | `To Do` |
| `tests/scheduler/test_{current_workflow_name}_scheduler.py` | `{Describe existing scheduler tests.}`                                                          | `{As above}`                                                                                                                                                                                                                                                                                                       | `{As above}`                                                                                                                                                                                                                                                             | `{As above}`                                                                                                                                                                                                                                                             | `To Do` |
| `tests/routers/test_{current_workflow_name}_router.py`      | `{Describe existing router tests for API endpoints, status updates, validation.}`               | `{As above, focusing on API endpoint coverage, critical paths, validation tests.}`                                                                                                                                                                                                                                 | `{As above, focusing on API tests.}`                                                                                                                                                                                                                                     | `{As above, focusing on API tests.}`                                                                                                                                                                                                                                     | `To Do` |
| **Workflow Integration Tests**                              | `{Describe if any end-to-end style workflow tests exist and what they cover.}`                  | `{Focus on completeness of lifecycle testing: API trigger -> DB state -> Scheduler pickup -> Service execution -> Final DB state -> Side effects.}`                                                                                                                                                                | `{Design and implement comprehensive workflow integration tests for `{WorkflowName}`.}`                                                                                                                                                                                  | `[ ] Workflow integration tests verify all key state transitions and outcomes.`                                                                                                                                                                                          | `To Do` |

---

## 3. Refactoring Implementation Log & Decisions

- **Date:** {YYYY-MM-DD}
  - **Action Taken:** {e.g., Renamed `src/models/old_enum.py` to embed ENUMs in `src/models/{source_table_name}.py`}
  - **Rationale:** {e.g., Align with standard for ENUM location.}
  - **Key Files Changed:** {List files}
  - **Associated Commit(s):** {Link to commit(s)}
  - **Issues Encountered/Clarifications Needed:** {Detail any}
- **Date:** {YYYY-MM-DD}
  - **Action Taken:** ...
  - **Rationale:** ...
  - ...

---

## 4. Post-Refactoring Verification & Sign-off

### 4.1 Overall Workflow Verification Checklist:

- [ ] All components listed in Section 2 have status "Done".
- [ ] `{WorkflowName}` successfully processes items from end-to-end as per its intended functionality.
  - [ ] UI interaction (if applicable) correctly triggers API.
  - [ ] API correctly updates curation and processing statuses (dual-status).
  - [ ] Scheduler picks up queued items and marks them as 'Processing'.
  - [ ] Processing service executes its logic successfully.
  - [ ] Final status (e.g., 'Completed', 'Error') is correctly set in the database.
  - [ ] Error messages (if any) are correctly logged/recorded.
- [ ] All automated tests for `{WorkflowName}` (unit, integration, workflow) pass.
- [ ] Manual testing procedure (as defined by an equivalent to Section 5.3 of the Workflow Builder Template) completed successfully.
- [ ] All code changes adhere strictly to the `CONVENTIONS_AND_PATTERNS_GUIDE.md` and `Q&A_Key_Insights.md`.
- [ ] This Audit & Refactoring Cheat Sheet is complete and accurately reflects the standardized state of the workflow.
- [ ] Any related documentation (e.g., `*_CANONICAL.yaml`, high-level diagrams) has been updated to reflect the standardized workflow.

### 4.2 Auditor/Implementer Sign-off:

- **Name:**
- **Date:**

### 4.3 Reviewer Sign-off (Optional):

- **Name:**
- **Date:**

---

This Audit & Refactoring Cheat Sheet, once completed and verified, should represent the new source of truth for the `{WorkflowName}` workflow's standardized structure and implementation details.
