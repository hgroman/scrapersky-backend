# AI Standard Operating Procedure: Layer 6 (UI Components) Audit

**Document Version:** 1.0
**Date:** 2025-05-14
**Purpose:** This Standard Operating Procedure (SOP) guides an AI assistant in performing a comprehensive audit of Layer 6 (UI Components: HTML, CSS, JavaScript, Static Assets) within the ScraperSky backend. The goal is to identify deviations from established architectural standards (as defined in the `Layer-6-UI_Components_Blueprint.md`) and populate the relevant section of an audit checklist or report.

---

## Introduction: Context from Architectural Truth

This SOP is designed to be used in conjunction with the `Layer-6-UI_Components_Blueprint.md` (Version 1.0 or later). Both documents are informed by the overarching architectural standards outlined in `Docs/Docs_6_Architecture_and_Status/1.0-ARCH-TRUTH-Definitive_Reference.md` and its supporting documents. The focus is on ensuring the frontend components are structured semantically, styled consistently, interact correctly via modular JavaScript, and manage static assets appropriately.

---

## 1. Prerequisites & Inputs

Before starting the audit of Layer 6 components, ensure you have access to and have reviewed:

1.  **The Layer 6 Blueprint (Version 1.0 or later):**
    - `Docs/Docs_10_Final_Audit/Layer-6-UI_Components_Blueprint.md` (Primary standard).
2.  **Core Architectural & Convention Guides:**
    - `Docs/Docs_6_Architecture_and_Status/1.0-ARCH-TRUTH-Definitive_Reference.md` (UI Component Integration principles, Tab-based interface pattern).
    - `Docs/Docs_6_Architecture_and_Status/CONVENTIONS_AND_PATTERNS_GUIDE.md` (Any specific UI naming conventions or JS module structures defined).
    - `Docs/Docs_6_Architecture_and_Status/Q&A_Key_Insights.md`.
3.  **Supporting Layer Blueprints:**
    - `Docs/Docs_10_Final_Audit/Layer-3-Routers_Blueprint.md` (To understand the API endpoints the UI interacts with).
4.  **Target for Audit Output:**
    - The specific audit checklist, report document, or section where Layer 6 findings will be recorded.
5.  **Relevant Source Code Files & Artifacts:**
    - Template directories (e.g., `src/templates/`).
    - Static asset directories (e.g., `src/static/`, including `css/`, `js/`, `img/` subdirectories).

---

## 2. Audit Procedure

Audit Layer 6 by examining specific component types and files:

### Step 2.1: Audit HTML Templates (e.g., `src/templates/`)

1.  **Identify:** Examine individual HTML template files (`.html`).
2.  **Analyze Against Blueprint (Section 2.1):**
    - Check for semantic HTML tag usage.
    - Verify basic accessibility (alt text, labels).
    - Check `id`/`class` naming consistency against defined conventions.
    - Assess template organization (use of base templates/partials).
    - **Crucially, identify any inline `style` attributes or non-trivial inline `<script>` blocks.**
3.  **Document Gaps:** Note non-semantic HTML, accessibility issues, inconsistent naming, disorganized structure, or use of inline styles/scripts.

### Step 2.2: Audit CSS Files (e.g., `src/static/css/`)

1.  **Identify:** Examine individual CSS files (`.css`).
2.  **Analyze Against Blueprint (Section 2.2):**
    - Confirm styles are primarily in external files.
    - Check class naming consistency against defined conventions (e.g., BEM).
    - Evaluate modularity – are styles grouped logically?
    - Look for overly specific selectors or excessive `!important` usage.
3.  **Document Gaps:** Note inconsistent naming, lack of modularity, specificity issues.

### Step 2.3: Audit JavaScript Files (e.g., `src/static/js/`)

1.  **Identify:** Examine individual JavaScript files (`.js`).
2.  **Analyze Against Blueprint (Section 2.3):**
    - Confirm logic is primarily in external files.
    - **Assess modularity:** Is code broken into functions/modules? Is the specified tab-UI JS pattern followed where applicable?
    - Check for global variable usage.
    - Review DOM manipulation techniques (efficiency/safety if possible).
    - **Verify API communication:** Are fetch/AJAX calls made? Is error handling present?
    - Check event handling methods.
    - Assess readability and potential linting violations (if tooling is available/standards known).
3.  **Document Gaps:** Note lack of modularity, global pollution, missing API error handling, poor readability, or violations of specific UI patterns (like tabs).

### Step 2.4: Audit Static Asset Organization (e.g., `src/static/`)

1.  **Identify:** Examine the structure of the main static directory and its subdirectories.
2.  **Analyze Against Blueprint (Section 2.4):**
    - Verify existence of standard subdirectories (`css/`, `js/`, `img/` etc.).
    - Check if assets are placed in the appropriate subdirectory.
3.  **Document Gaps:** Note disorganized structure or misplaced assets.

### Step 2.5: Populate Audit Report / Cheat Sheet (Layer 6 Section)

For each identified gap across all audited components:

1.  **File Path / Component Type:** Specify the relevant file and type (e.g., `src/templates/page.html`, `CSS: src/static/css/main.css`, `JS: src/static/js/tabs.js`).
2.  **Gap Analysis (Technical Debt Identification):**
    - Follow the logic outlined in **Section 4, Step 3 ("Document Technical Debt")** of the `Layer-6-UI_Components_Blueprint.md`.
    - Clearly list each deviation identified in Steps 2.1-2.4.
    - Prioritize flagging accessibility issues, potential security risks (e.g., how user input is rendered if obvious), and major structural/modularity problems.
    - Reference the specific Blueprint section/criterion (e.g., "Blueprint 2.1.1: Use of `<div>` where `<button>` is appropriate.", "Blueprint 2.1.5: Inline styles found.", "Blueprint 2.3.2: JavaScript file is monolithic; should be modularized.", "Blueprint 2.3.5: API call lacks error handling.", "Blueprint 2.4.1: JS files located directly in `static/` instead of `static/js/`.").
    - Use `<!-- NEED_CLARITY: [Your question here] -->` if compliance is ambiguous.
3.  **Prescribed Refactoring Actions:**
    - Suggest concrete actions aligned with **Section 4, Step 4 ("Prescribe Refactoring Actions")** of the `Layer-6-UI_Components_Blueprint.md`.
    - Examples:
      - "Refactor `<div>` to `<button>` in `page.html` for semantic correctness and accessibility."
      - "Extract inline styles from `header.html` into `header.css`."
      - "Break down `app.js` into separate modules for API calls, event handling, and DOM updates."
      - "Add `.catch()` block to handle errors for the fetch request in `user_profile.js`."
      - "Move all `.js` files into the `src/static/js/` directory."

### Step 2.6: Review and Finalize

1.  Ensure all key Layer 6 components/files (HTML, CSS, JS, asset structure) have been assessed.
2.  Verify that the audit report entries are clear, concise, and reference the Layer 6 Blueprint.
3.  Mark any sections with `<!-- STOP_FOR_REVIEW -->` if human review is required, especially for complex JS logic or accessibility concerns.

### Step 2.7: Conclude Audit for this Layer

1.  **Audit Focus:** Reiterate that the actions performed under this SOP (Steps 2.1-2.6) are strictly for auditing and documenting findings. The primary output is the comprehensive Layer 6 assessment.
2.  **No Refactoring:** Confirm that no code refactoring is performed during this audit phase. All identified technical debt and refactoring actions are documented for future work by the appropriate persona.
3.  **Output Destination:** Ensure all findings from Step 2.5 (Populate Audit Report / Cheat Sheet) are consolidated into the designated Layer 6 audit report document, typically located in `Docs/Docs_10_Final_Audit/Audit Reports Layer 6/Layer6_UI_Components_Audit_Report.md` (or a similarly named file specific to this layer).
4.  **Next Steps:** Once all Layer 6 components as outlined in this SOP have been audited and documented, notify the USER that the Layer 6 UI Components audit is complete. Await further instructions for the next audit layer or task.

---

## 3. Output

- A comprehensive Layer 6 audit report document (e.g., `Layer6_UI_Components_Audit_Report.md`) detailing assessments for all relevant UI components, including identified gaps, technical debt, and prescribed refactoring actions (for future implementation).

---

This SOP is a living document and may be updated as the Blueprint evolves or new insights are gained.
