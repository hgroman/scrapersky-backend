# AI Session Context: Workflow Audit & Refactoring TEMPLATE

**Document Version:** 1.0
**Date:** {YYYY-MM-DD}
**Status:** Active Context for Current AI Chat Session
**Workflow Under Audit & Refactor:** `{WorkflowName}` (e.g., `page_curation`, `sitemap_import`)

---

## 0. Core Guiding Documents for this Session

1.  **AI Collaboration Constitution:** `Docs/Docs_8_Document-X/8.0-AI-COLLABORATION-CONSTITUTION.md` (Establishes foundational rules of AI engagement).
2.  **Project Work Order (This Refactoring Initiative):** `Docs/Docs_5_Project_Working_Docs/52-Gold-Standard-Blue-Print/52.0-Draft-Work-Order.md` (Outlines the overall strategy and goals for codebase standardization).
3.  **The Golden Standard Blueprint:** `Docs/Docs_6_Architecture_and_Status/CONVENTIONS_AND_PATTERNS_GUIDE.md` (The definitive source for all target naming conventions and structural patterns).
4.  **Blueprint Clarifications & Q&A:** `Docs/Docs_6_Architecture_and_Status/Q&A_Key_Insights.md` (Actionable answers to common implementation questions).
5.  **Active Audit & Refactor Cheat Sheet (This Workflow's Instance):** `Docs/Docs_8_Document-X/INSTANCES/Audit_And_Refactor_{WorkflowName}_Cheat_Sheet.md` (This is the primary document for recording audit findings and refactoring plans for the current workflow. **This session will focus on populating and actioning this document.**)
6.  **This Document:** Sets the immediate task focus for the current AI session.

---

## 1. CURRENT TASK FOCUS (AUDIT & REFACTORING)

**1.1. Primary Goal (from Work Order & Constitution, reaffirmed for this task):**

- Systematically audit the existing `{WorkflowName}` workflow against the **Golden Standard Blueprint** (`CONVENTIONS_AND_PATTERNS_GUIDE.md` and `Q&A_Key_Insights.md`).
- Identify all technical debt and deviations from the Blueprint.
- Prescribe and execute refactoring actions to bring the `{WorkflowName}` workflow into full conformity.
- Ensure all findings, plans, and actions are meticulously documented in the **Active Audit & Refactor Cheat Sheet** for `{WorkflowName}`.
- Operate under the **"Zero Assumptions"** and **"Document-First Iteration"** principles from the AI Collaboration Constitution.

**1.2. Secondary Goal (Specific Focus for This Session):**

- {e.g., "Complete the audit of the Model layer for `{WorkflowName}` as per Section 2.1 of its Active Audit & Refactor Cheat Sheet."}
- {e.g., "Implement the planned refactoring for the Router layer of `{WorkflowName}` based on the agreed actions in Section 2.3 of its Active Audit & Refactor Cheat Sheet."}
- {e.g., "Begin initial population of the Active Audit & Refactor Cheat Sheet for `{WorkflowName}`, starting with Section 1: Workflow Overview."}

---

## 2. CURRENT IMPLEMENTATION STATUS (As of session start for `{WorkflowName}` Audit & Refactor)

- **`{WorkflowName}` Audit & Refactor Progress:**

  - **Active Audit & Refactor Cheat Sheet:** `{Link to the specific instantiated cheat sheet for this workflow, e.g., Docs/Docs_8_Document-X/INSTANCES/Audit_And_Refactor_Page_Curation_Cheat_Sheet.md}` - _Current status of completion: {e.g., "Partially filled for Model and Schema layers." or "Newly instantiated."}_
  - **Section 1 (Overview & Initial Assessment):** {Status: To Do / In Progress / Done}
  - **Section 2.1 (Models & ENUMs Audit):** {Status: To Do / In Progress / Gap Analysis Done / Refactoring Planned / Refactoring Done}
  - **Section 2.2 (Schemas Audit):** {Status: To Do / In Progress / Gap Analysis Done / Refactoring Planned / Refactoring Done}
  - **Section 2.3 (Routers Audit):** {Status: To Do / In Progress / Gap Analysis Done / Refactoring Planned / Refactoring Done}
  - **Section 2.4 (Services & Schedulers Audit):** {Status: To Do / In Progress / Gap Analysis Done / Refactoring Planned / Refactoring Done}
  - **Section 2.5 (Config & Env Vars Audit):** {Status: To Do / In Progress / Gap Analysis Done / Refactoring Planned / Refactoring Done}
  - **Section 2.6 (UI Components Audit):** {Status: To Do / In Progress / Gap Analysis Done / Refactoring Planned / Refactoring Done}
  - **Section 2.7 (Testing Audit):** {Status: To Do / In Progress / Gap Analysis Done / Refactoring Planned / Refactoring Done}
  - **Previous Commits related to this specific workflow's refactor (if any):** {Links or SHAs}

- **Key Supporting Documents (Already Reviewed or To Be Referenced):**
  - `Docs/Docs_7_Workflow_Canon/Audit/WORKFLOW_AUDIT_JOURNAL.md` (for pre-existing notes on `{WorkflowName}`)
  - Relevant `52.X-Analysis-Layer...md` documents if applicable to `{WorkflowName}`.
  - Existing Canonical YAML for `{WorkflowName}` (if one exists).

---

## 3. IMMEDIATE NEXT ACTION FOR THIS AI SESSION

1.  **Internalize Core Guiding Documents:** AI must confirm it has processed and understands the documents listed in Section 0, especially the **AI Collaboration Constitution**, the overall **Project Work Order**, the **Golden Standard Blueprint**, and the purpose of the **Active Audit & Refactor Cheat Sheet** for `{WorkflowName}`.
2.  **Confirm Understanding of Core Principles:** Verbally confirm understanding of the Core Mandate and Fundamental Operational Directives (especially "Zero Assumptions" and "Document-First Iteration") from the Constitution.
3.  **Proceed with Task:**
    - **Current Focus:** {Reiterate the specific goal from 1.2, e.g., "Focus on auditing the Model layer: `src/models/{current_model_file_for_workflowName}.py`."}
    - **Action:** {e.g., "Review the specified model file(s) against Section 4 of the `CONVENTIONS_AND_PATTERNS_GUIDE.md` and the 'Python Backend - Models' section of `Q&A_Key_Insights.md`. Document all findings, deviations, and proposed refactoring actions in Section 2.1 of `Audit_And_Refactor_{WorkflowName}_Cheat_Sheet.md`."}
    - **Output Location:** All detailed findings and plans go into the **Active Audit & Refactor Cheat Sheet** for `{WorkflowName}`.

---

This document, along with the AI Collaboration Constitution, supersedes all prior session contexts for the audit and refactoring of the `{WorkflowName}` workflow.
