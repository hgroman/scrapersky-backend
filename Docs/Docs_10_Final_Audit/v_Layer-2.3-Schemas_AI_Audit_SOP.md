# AI Standard Operating Procedure: Layer 2 (Schemas) Audit

**Document Version:** 1.0
**Date:** 2025-05-14
**Purpose:** This Standard Operating Procedure (SOP) guides an AI assistant in performing a comprehensive audit of Layer 2 (Pydantic Schemas) components within the ScraperSky backend. The goal is to identify deviations from established architectural standards (as defined in the `Layer-2-Schemas_Blueprint.md`) and populate the relevant section of an audit checklist or report.

---

## Introduction: Context from Architectural Truth

This SOP is designed to be used in conjunction with the `Layer-2-Schemas_Blueprint.md` (Version 1.0 or later). Both documents are informed by the overarching architectural standards outlined in `Docs/Docs_6_Architecture_and_Status/v_1.0-ARCH-TRUTH-Definitive_Reference.md` and its supporting documents. The focus is on ensuring API contracts are well-defined, consistent, and properly validated.

---

## 1. Prerequisites & Inputs

Before starting the audit of Layer 2 components, ensure you have access to and have reviewed:

1.  **The Layer 2 Blueprint (Version 1.0 or later):**
    - `Docs/Docs_10_Final_Audit/Layer-2-Schemas_Blueprint.md` (This is the primary standard defining "what good looks like" for Pydantic schemas.)
2.  **Core Architectural & Convention Guides:**
    - `Docs/Docs_6_Architecture_and_Status/1.0-ARCH-TRUTH-Definitive_Reference.md`
    - `Docs/Docs_6_Architecture_and_Status/archive-dont-vector/CONVENTIONS_AND_PATTERNS_GUIDE.md` (Especially Section 3 for Schema conventions).
    - `Docs/Docs_6_Architecture_and_Status/Q&A_Key_Insights.md` (For any general clarifications or specific Q&A related to schema design if available).
3.  **Target for Audit Output:**
    - The specific audit checklist, report document, or section of a workflow-specific cheat sheet where Layer 2 findings will be recorded.
4.  **Relevant Source Code Files:**
    - All files within the `src/schemas/` directory (e.g., `src/schemas/page.py`, `src/schemas/domain.py`, `src/schemas/common.py`).
5.  **(Context) Layer 1 Models & Enums:**
    - Familiarity with or access to `src/models/` to verify correct usage of Layer 1 Enums in Layer 2 schemas.

---

## 2. Audit Procedure

For each target `.py` file within `src/schemas/`:

### Step 2.1: Identify Components for Audit

1.  Scan the file to identify all Pydantic model class definitions (typically inheriting from `pydantic.BaseModel`).

### Step 2.2: Analyze Identified Components Against the Blueprint

For **each Pydantic Model class** identified:

1.  Thoroughly review its definition against all criteria in **Section 2.2.1 (Key Compliance Criteria for Pydantic Models)** of the `Layer-2-Schemas_Blueprint.md`.
    - Pay close attention to: Naming (file and class), Base Class (`BaseModel`), Fields (type hints, snake_case naming, `Optional`), Configuration (`orm_mode`/`from_attributes`, alias generation if applicable), Validators (scope), Schema Variations (inheritance for Base/Create/Update/Read), ENUM Usage (referencing Layer 1 Enums), and Docstrings/Descriptions.

### Step 2.3: Populate Audit Report / Cheat Sheet (Layer 2 Section)

For each identified Pydantic model within each file:

1.  **File Path:** Document the full path to the file (e.g., `src/schemas/page.py`).
2.  **Component Name:** Specify the Schema class name (e.g., `Schema: PageRead`).
3.  **Current State Summary (Optional but Recommended):** Briefly describe its purpose (e.g., "Response model for page data", "Request body for user creation").
4.  **Gap Analysis (Technical Debt Identification):**
    - Follow the logic outlined in **Section 4, Step 3 ("Document Technical Debt")** of the `Layer-2-Schemas_Blueprint.md`.
    - Clearly list each deviation from the Blueprint identified in Step 2.2.
    - For each deviation, reference the specific Blueprint section/criterion that is not being met (e.g., "Blueprint 2.2.1.2: Class name 'Page' is ambiguous; rename to 'PageRead' or similar.", "Blueprint 2.2.1.3: Field 'pageTitle' is not snake_case.", "Blueprint 2.2.1.4: Missing `orm_mode=True` in Config for response schema.").
    - Use `<!-- NEED_CLARITY: [Your question here] -->` if any aspect of the schema or its compliance is ambiguous and requires human clarification.
5.  **Prescribed Refactoring Actions:**
    - Suggest concrete actions aligned with **Section 4, Step 4 ("Prescribe Refactoring Actions")** of the `Layer-2-Schemas_Blueprint.md`.
    - Actions should guide towards full compliance with the Blueprint.
    - Examples:
      - "Rename schema file `OldName.py` to `new_name.py`."
      - "Refactor `SchemaX` class name to `EntityCreate`."
      - "Add type hints to all fields in `SchemaY`."
      - "Implement Base/Create/Update/Read pattern for `Entity` schemas using inheritance."
      - "Ensure `status` field uses `MyStatusEnum` from Layer 1."
6.  **Verification Checklist (Post-Refactoring - Optional, for major changes):**
    - List key items to check to confirm compliance after refactoring (e.g., "Verify schema class name follows convention," "Confirm fields are snake_case," "Check `orm_mode` is set correctly," "Verify inheritance pattern is used").

### Step 2.4: Review and Finalize

1.  Ensure all files in `src/schemas/` and all Pydantic models within them have been assessed.
2.  Verify that the audit report/cheat sheet entries are clear, concise, and directly reference the Layer 2 Blueprint.
3.  Mark any sections with `<!-- STOP_FOR_REVIEW -->` if human review is required for `NEED_CLARITY` items or complex assessments.

### Step 2.5: Conclude Audit for this Layer

1.  **Audit Focus:** Reiterate that the actions performed under this SOP are strictly for auditing and documenting findings. The primary output is the comprehensive Layer 2 assessment.
2.  **No Refactoring:** Confirm that no code refactoring is performed during this audit phase. All identified technical debt and refactoring actions are documented for future work by the appropriate persona.
3.  **Output Destination:** Ensure all findings from Step 2.3 (Populate Audit Report / Cheat Sheet) are consolidated into the designated Layer 2 audit report document, typically located in `Docs/Docs_10_Final_Audit/Audit Reports Layer 2/Layer2_Schemas_Audit_Report.md` (or a similarly named file specific to this layer).
4.  **Next Steps:** Once all components in `src/schemas/` have been audited and documented as per this SOP, notify the USER that the Layer 2 Schemas audit is complete. Await further instructions for the next audit layer or task.

---

## 3. Output

- A comprehensive Layer 2 audit report document (e.g., `Layer2_Schemas_Audit_Report.md`) detailing assessments for all Pydantic schemas, including identified gaps, technical debt, and prescribed refactoring actions (for future implementation).

---

This SOP is a living document and may be updated as the Blueprint evolves or new insights are gained.
