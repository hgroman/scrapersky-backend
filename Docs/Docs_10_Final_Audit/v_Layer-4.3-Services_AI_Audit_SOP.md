# AI Standard Operating Procedure: Layer 4 (Services & Schedulers) Audit

**Document Version:** 2.1
**Date:** 2025-05-13
**Purpose:** This Standard Operating Procedure (SOP) guides an AI assistant in performing a comprehensive audit of Layer 4 (Services, including Schedulers, and relevant Router-based logic) for a given ScraperSky workflow. The goal is to identify deviations from established architectural standards (as defined in the Blueprint) and populate the relevant section of the workflow-specific cheat sheet.

---

## Introduction: Context from Architectural Truth

This SOP is designed to be used in conjunction with the `Layer-4-Services_Blueprint.md` (Version 2.1 or later). Both documents are informed by the overarching architectural standards outlined in the `Docs/Docs_6_Architecture_and_Status/1.0-ARCH-TRUTH-Definitive_Reference.md` and its supporting documents. For a broader understanding of how Layer 4 components have been historically classified and the types of functionalities they encompass, consult `Docs/Docs_6_Architecture_and_Status/3.0-ARCH-TRUTH-Layer_Classification_Analysis.md`.

---

## 1. Prerequisites & Inputs

## 1.A Layer 4 Audit Workflow Checklist

This checklist tracks the progress of Layer 4 audits across all relevant workflows.

- [x] WF1-SingleSearch
- [x] WF2-StagingEditor
- [x] WF3-LocalBusinessCuration
- [x] WF4-DomainCuration
- [x] WF5-SitemapCuration
- [x] WF6-SitemapImport
- [x] WF7-PageCuration

Before starting the audit for a specific workflow, ensure you have access to and have reviewed:

Before starting the audit for a specific workflow, ensure you have access to and have reviewed:

1.  **The Layer 4 Blueprint (Version 2.1 or later):**
    - `Docs/Docs_10_Final_Audit/Layer-4-Services_Blueprint.md` (This is the primary standard defining "what good looks like".)
2.  **Core Architectural & Convention Guides (for context and detailed naming/patterns):**
    - `Docs/Docs_6_Architecture_and_Status/1.0-ARCH-TRUTH-Definitive_Reference.md`
    - `Docs/Docs_6_Architecture_and_Status/CONVENTIONS_AND_PATTERNS_GUIDE.md`
    - `Docs/Docs_6_Architecture_and_Status/Q&A_Key_Insights.md`
    - `Docs/Docs_6_Architecture_and_Status/3.0-ARCH-TRUTH-Layer_Classification_Analysis.md` (especially for understanding the scope of typical Layer 4 work).
3.  **Workflow-Specific Cheat Sheet:**
    - The target cheat sheet file (e.g., `Docs/Docs_10_Final_Audit/WF{X}-{WorkflowName}_Cheat_Sheet.md`). You will be populating Section 2.1 (or the re-prioritized Layer 4 section).
4.  **Relevant Source Code Files for the Target Workflow:**
    - Associated service files (e.g., `src/services/{workflow_name}_service.py`, `src/services/{workflow_name}_scheduler.py`).
    - Associated router files (e.g., `src/routers/{workflow_name}.py` or `src/routers/{workflow}_CRUD.py` or `src/routers/{source_table_plural_name}.py`).
5.  **Workflow Definition (for context):**
    - `Docs/Docs_7_Workflow_Canon/v_4_PATTERN_COMPARISON.yaml` (provides high-level overview of workflow structure).

---

## 2. Audit Procedure

For each target workflow (as per the checklist in Section 1.A), perform the following steps for its Layer 4 components:

### Step 2.1: Identify Service/Logic Implementation Pattern

1.  **Review `v_4_PATTERN_COMPARISON.yaml` and relevant router/service filenames** for the target workflow.
2.  **Consult Section 4 (Audit & Assessment Guidance) of the `Layer-4-Services_Blueprint.md`.**
3.  **Determine the primary pattern used for this workflow's core logic:**
    - **Pattern A: Dedicated Service Layer** (Logic primarily in `src/services/{workflow_name}_service.py` and `..._scheduler.py`).
    - **Pattern B: Router-Handled CRUD & Dual-Status Updates** (Logic primarily in `src/routers/{workflow}_CRUD.py` or a similar entity-specific router handling these specific tasks).
    - **Note:** Some workflows might have schedulers (Pattern A) even if some synchronous logic is in a router (Pattern B).

### Step 2.2: Analyze Relevant Code Files Against the Blueprint

1.  **If Pattern A (Dedicated Service Layer) applies:**
    - Thoroughly review `src/services/{workflow_name}_service.py` and `src/services/{workflow_name}_scheduler.py` (if it exists).
    - Assess against all criteria in **Section 2.2 (Key Compliance Criteria for Dedicated Services)** of the `Layer-4-Services_Blueprint.md`.
2.  **If Pattern B (Router-Handled CRUD & Dual-Status Updates) applies to the router logic:**
    - Thoroughly review the relevant router file (e.g., `src/routers/{workflow}_CRUD.py`).
    - Assess against all criteria in **Section 3.2 (Key Compliance Criteria for {workflow}\_CRUD.py Routers)** of the `Layer-4-Services_Blueprint.md`.
    - **Crucially, assess if the logic in the router exceeds the defined scope for this pattern.** If it performs complex orchestration, interacts with many other components beyond the primary entity, or makes significant external API calls not related to simple entity lookups, this is a deviation even if the router is named `..._CRUD.py`. Such overreach should be flagged as technical debt with a recommendation to refactor towards Pattern A.
3.  **For ALL Files Analyzed (Services, Schedulers, Routers contributing to Layer 4 logic):**
    - Identify every deviation from the applicable Blueprint criteria.
    - Note any use of deprecated patterns or anti-patterns (e.g., raw SQL, incorrect session handling, hardcoded values, missing tenant ID isolation).
    - Cross-reference with JIRA tickets if specific issues are already known (e.g., SCRSKY-225 for raw SQL).

### Step 2.3: Populate the Workflow-Specific Cheat Sheet (Layer 4 Section)

For each identified service, scheduler, or router file contributing to Layer 4:

1.  **File Path:** Document the full path to the file.
2.  **Current State Summary:** Briefly describe its current purpose, key functionalities relevant to Layer 4, and the **implemented pattern** identified in Step 2.1 (e.g., "Dedicated Service Layer" or "Router-Handled CRUD & Dual-Status Updates").
3.  **Gap Analysis (Technical Debt Identification):**
    - Follow the logic outlined in **Section 4, Step 2 ("Assess Against Ideal & Specific Criteria")** and **Section 4, Step 3 ("Document Technical Debt")** of the `Layer-4-Services_Blueprint.md`.
    - Clearly list each deviation identified.
    - **Specifically state if the primary deviation is the use of the "Router-Handled" pattern when the "Dedicated Service" pattern is the ideal for that type of logic.**
    - **If the "Router-Handled" pattern is implemented, explicitly state whether its logic is within or exceeds the bounded scope defined in Blueprint Section 3.2. If it exceeds, this is a critical gap.**
    - For all identified gaps, reference the specific Blueprint section/criterion that is not being met.
    - Use `<!-- NEED_CLARITY: [Your question here] -->` if anything is ambiguous.
4.  **Prescribed Refactoring Actions:**
    - Suggest concrete actions aligned with **Section 4, Step 4 ("Prescribe Refactoring Actions")** of the `Layer-4-Services_Blueprint.md`.
    - Actions should guide towards the ideal pattern, prioritizing critical fixes (e.g., refactoring out-of-scope router logic, eliminating raw SQL).
    - If the current pattern is "Router-Handled" (and within its defined scope) but the ideal is "Dedicated Service," the action might be: "Consider refactoring to a dedicated service for long-term architectural alignment. For now, ensure full compliance with Blueprint Section 3.2 criteria."
    - Reference relevant JIRA tickets if applicable.
5.  **Verification Checklist (Post-Refactoring):**
    - List key items to check to confirm compliance after refactoring (e.g., "Verify no raw SQL queries remain," "Confirm session is passed from router and not created in service," "Ensure scheduler uses settings for batch size and interval").

### Step 2.4: Summarize Audit Findings & Create Audit Report

1.  **Consolidate Findings:** Gather all deviations, technical debt, and key observations documented in the cheat sheet for the current workflow.
2.  **Create Workflow-Specific Audit Report:**
    *   Generate a new Markdown file for the current workflow.
    *   **Naming Convention:** `WF{X}-{WorkflowName}_Layer4_Audit_Report.md` (e.g., `WF1-SingleSearch_Layer4_Audit_Report.md`).
    *   **Location:** Save the report in the `Docs/Docs_10_Final_Audit/Audit Reports Layer 4/` directory.
    *   **Content:** The report should include:
        *   **Workflow Audited:** (e.g., WF1-SingleSearch)
        *   **Date of Audit:**
        *   **Auditor:** (Your AI Persona Name)
        *   **Files Audited:** List all service, scheduler, and router files reviewed.
        *   **Consolidated Summary of Findings:** A narrative summarizing the overall state, implemented patterns, major blueprint violations (e.g., Tenant ID issues, Raw SQL, Hardcoding), and any critical out-of-scope logic in routers.
        *   **Detailed Findings per File:** For each audited file, reiterate the key "Gap Analysis" points from the cheat sheet.
        *   **Blueprint Adherence Score (Optional - TBD):** (e.g., A rating or percentage indicating overall compliance.)
        *   **Key Areas Requiring Attention (for Remediation Persona):** Highlight the most critical issues that the remediation team should focus on.
3.  **Final Review:** Ensure the audit report is clear, accurate, and directly references the cheat sheet and Blueprint. Mark with `<!-- STOP_FOR_REVIEW -->` if human review is needed.

### Step 2.5: Confirm Audit Scope, Update Checklist, and Proceed

1.  **Audit Focus & No Refactoring:** Before proceeding, explicitly confirm that the activities performed for the just-audited workflow (Steps 2.1-2.4) were strictly for auditing. The primary outputs are the updated workflow-specific cheat sheet and the creation of the `WF{X}-{WorkflowName}_Layer4_Audit_Report.md` in the `Docs/Docs_10_Final_Audit/Audit Reports Layer 4/` directory. No code refactoring is undertaken during this audit phase; all identified issues and refactoring actions are documented for future work.
2.  **Update Checklist:** Mark the corresponding workflow as complete in the "Layer 4 Audit Workflow Checklist" (Section 1.A).
3.  **Next Workflow or Completion:**
    *   If there are unchecked workflows remaining in the checklist, proceed to the next one and repeat the Audit Procedure (Steps 2.1 to 2.5).
    *   If all workflows in the checklist are complete, notify the USER that the entire Layer 4 Services audit (covering all workflows as per this SOP) is now complete. Await further instructions.

---

## 3. Output

-   Updated workflow-specific cheat sheet (`Docs/Docs_10_Final_Audit/WF{X}-{WorkflowName}_Cheat_Sheet.md`) with a comprehensive Layer 4 assessment for each audited workflow.
-   Individual Layer 4 audit reports for each audited workflow, saved in `Docs/Docs_10_Final_Audit/Audit Reports Layer 4/` with the naming convention `WF{X}-{WorkflowName}_Layer4_Audit_Report.md`.

---

This SOP is a living document and may be updated as new insights are gained from further workflow audits.
