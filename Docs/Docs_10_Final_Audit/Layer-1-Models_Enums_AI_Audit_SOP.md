# AI Standard Operating Procedure: Layer 1 (Models & ENUMs) Audit

**Document Version:** 1.0
**Date:** 2025-05-14
**Purpose:** This Standard Operating Procedure (SOP) guides an AI assistant in performing a comprehensive audit of Layer 1 (SQLAlchemy Models and Python ENUMs) components within the ScraperSky backend. The goal is to identify deviations from established architectural standards (as defined in the `Layer-1-Models_Enums_Blueprint.md`) and populate the relevant section of an audit checklist or report.

---

## Introduction: Context from Architectural Truth

This SOP is designed to be used in conjunction with the `Layer-1-Models_Enums_Blueprint.md` (Version 1.0 or later). Both documents are informed by the overarching architectural standards outlined in `Docs/Docs_6_Architecture_and_Status/1.0-ARCH-TRUTH-Definitive_Reference.md` and its supporting documents, particularly `Docs/Docs_6_Architecture_and_Status/CONVENTIONS_AND_PATTERNS_GUIDE.md`.

---

## 1. Prerequisites & Inputs

Before starting the audit of Layer 1 components, ensure you have access to and have reviewed:

1.  **The Layer 1 Blueprint (Version 1.0 or later):**
    - `Docs/Docs_10_Final_Audit/Layer-1-Models_Enums_Blueprint.md` (This is the primary standard defining "what good looks like" for models and ENUMs.)
2.  **Core Architectural & Convention Guides:**
    - `Docs/Docs_6_Architecture_and_Status/1.0-ARCH-TRUTH-Definitive_Reference.md`
    - `Docs/Docs_6_Architecture_and_Status/CONVENTIONS_AND_PATTERNS_GUIDE.md` (Especially Section 2 for Model and ENUM conventions).
    - `Docs/Docs_6_Architecture_and_Status/Q&A_Key_Insights.md` (For any general clarifications or specific Q&A related to data modeling if available).
3.  **Target for Audit Output:**
    - The specific audit checklist, report document, or section of a workflow-specific cheat sheet where Layer 1 findings will be recorded.
4.  **Relevant Source Code Files:**
    - All files within `src/models/` directory, including `base.py`, `enums.py` (if it exists as a shared file), and individual model files (e.g., `src/models/page.py`, `src/models/domain.py`).

---

## 2. Audit Procedure

For each target `.py` file within `src/models/`:

### Step 2.1: Identify Components for Audit

1.  Scan the file to identify all SQLAlchemy model class definitions (typically inheriting from a common `Base` or `BaseModel`).
2.  Scan the file to identify all Python `Enum` class definitions.

### Step 2.2: Analyze Identified Components Against the Blueprint

For **each SQLAlchemy Model class** identified:

1.  Thoroughly review its definition against all criteria in **Section 2.2.1 (Key Compliance Criteria for SQLAlchemy Models)** of the `Layer-1-Models_Enums_Blueprint.md`.
    - Pay close attention to: Naming (file and class), Base Class, Table Definition, Column types and naming, Foreign Keys, Relationships, ORM Exclusivity, absence of Tenant ID/prohibited legacy fields, and Docstrings.

For **each Python ENUM class** identified:

1.  Thoroughly review its definition against all criteria in **Section 2.2.2 (Key Compliance Criteria for Python ENUMs)** of the `Layer-1-Models_Enums_Blueprint.md`.
    - Pay close attention to: Naming (especially for `CurationStatus` and `ProcessingStatus` ENUMs), Base Class (`str, Enum`), Standard Values (for status ENUMs), Model Column Association (correct `PgEnum` usage and naming), and rules for general ENUMs or justified non-standard user states.

For **ALL Files Analyzed:**

1.  Identify every deviation from the applicable Blueprint criteria.
2.  Note any use of deprecated patterns or anti-patterns (e.g., raw SQL in model helper methods, incorrect ENUM inheritance, non-standard status values without justification).

### Step 2.3: Populate Audit Report / Cheat Sheet (Layer 1 Section)

For each identified model or ENUM within each file:

1.  **File Path:** Document the full path to the file (e.g., `src/models/page.py`).
2.  **Component Name:** Specify the Model class name or ENUM class name (e.g., `Model: Page`, `ENUM: PageCurationStatus`).
3.  **Current State Summary (Optional but Recommended):** Briefly describe its purpose if not obvious from the name or context.
4.  **Gap Analysis (Technical Debt Identification):**
    - Follow the logic outlined in **Section 4, Step 3 ("Document Technical Debt")** of the `Layer-1-Models_Enums_Blueprint.md`.
    - Clearly list each deviation from the Blueprint identified in Step 2.2.
    - For each deviation, reference the specific Blueprint section/criterion that is not being met (e.g., "Blueprint 2.2.1.1: File name does not follow `{source_table_name}.py` convention.", "Blueprint 2.2.2.2: ENUM `XYZStatus` does not inherit from `(str, Enum)`.").
    - Use `<!-- NEED_CLARITY: [Your question here] -->` if any aspect of the component or its compliance is ambiguous and requires human clarification.
5.  **Prescribed Refactoring Actions:**
    - Suggest concrete actions aligned with **Section 4, Step 4 ("Prescribe Refactoring Actions")** of the `Layer-1-Models_Enums_Blueprint.md`.
    - Actions should guide towards full compliance with the Blueprint.
    - Examples:
      - "Rename model file `OldName.py` to `new_name.py`."
      - "Refactor `ModelX` class to inherit from `BaseModel`."
      - "Update `status_enum` to include all standard values from Blueprint 2.2.2."
      - "Add `ondelete="CASCADE"` to ForeignKey `user_id` in `Post` model."
6.  **Verification Checklist (Post-Refactoring - Optional, for major changes):**
    - List key items to check to confirm compliance after refactoring (e.g., "Verify model class name is `CorrectName`," "Confirm `NewStatus` ENUM inherits `(str, Enum)` and has all required members").

### Step 2.4: Review and Finalize

1.  Ensure all files in `src/models/` and all components within them have been assessed.
2.  Verify that the audit report/cheat sheet entries are clear, concise, and directly reference the Layer 1 Blueprint.
3.  Mark any sections with `<!-- STOP_FOR_REVIEW -->` if human review is required for `NEED_CLARITY` items or complex assessments.

---

## 3. Output

- An updated audit checklist, report, or workflow-specific cheat sheet with a comprehensive Layer 1 assessment for all models and ENUMs.

---

This SOP is a living document and may be updated as the Blueprint evolves or new insights are gained.
