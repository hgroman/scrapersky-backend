# AI Standard Operating Procedure: Layer 3 (Routers) Audit

**Document Version:** 1.0
**Date:** 2025-05-14
**Purpose:** This Standard Operating Procedure (SOP) guides an AI assistant in performing a comprehensive audit of Layer 3 (FastAPI Routers and Endpoints) components within the ScraperSky backend. The goal is to identify deviations from established architectural standards (as defined in the `Layer-3-Routers_Blueprint.md`) and populate the relevant section of an audit checklist or report.

---

## Introduction: Context from Architectural Truth

This SOP is designed to be used in conjunction with the `Layer-3-Routers_Blueprint.md` (Version 1.0 or later). Both documents are informed by the overarching architectural standards outlined in `Docs/Docs_6_Architecture_and_Status/1.0-ARCH-TRUTH-Definitive_Reference.md` and its supporting documents, particularly `Docs/Docs_6_Architecture_and_Status/CONVENTIONS_AND_PATTERNS_GUIDE.md`. The focus is on ensuring API endpoints are correctly defined, manage transactions appropriately, handle authentication, and delegate business logic correctly.

---

## 1. Prerequisites & Inputs

Before starting the audit of Layer 3 components, ensure you have access to and have reviewed:

1.  **The Layer 3 Blueprint (Version 1.0 or later):**
    - `Docs/Docs_10_Final_Audit/Layer-3-Routers_Blueprint.md` (Primary standard for routers).
2.  **Core Architectural & Convention Guides:**
    - `Docs/Docs_6_Architecture_and_Status/1.0-ARCH-TRUTH-Definitive_Reference.md` (Especially Transaction Responsibility Pattern, Authentication, API Standardization).
    - `Docs/Docs_6_Architecture_and_Status/CONVENTIONS_AND_PATTERNS_GUIDE.md` (Especially Section 4 for Router conventions).
    - `Docs/Docs_6_Architecture_and_Status/Q&A_Key_Insights.md` (Clarifications on session/transaction handling).
3.  **Supporting Layer Blueprints:**
    - `Docs/Docs_10_Final_Audit/Layer-2-Schemas_Blueprint.md` (To understand expected schema usage).
    - `Docs/Docs_10_Final_Audit/Layer-4-Services_Blueprint.md` (To understand where business logic _should_ reside).
4.  **Target for Audit Output:**
    - The specific audit checklist, report document, or section of a workflow-specific cheat sheet where Layer 3 findings will be recorded.
5.  **Relevant Source Code Files:**
    - All files within the `src/routers/` directory (e.g., `src/routers/pages.py`, `src/routers/auth.py`).
    - The dependency injection setup for database sessions (e.g., `src/dependencies.py` or similar).
    - Authentication dependency setup (e.g., `src/auth/dependencies.py` or similar).

---

## 2. Audit Procedure

For each target `.py` file within `src/routers/`:

### Step 2.1: Identify Components for Audit

1.  Identify the `APIRouter` instance and its configuration (prefix, tags).
2.  Identify all endpoint functions defined using `@router.<method>` decorators.

### Step 2.2: Analyze Identified Components Against the Blueprint

For **each endpoint function** identified:

1.  **Determine Implemented Pattern:** Classify the endpoint based on the logic in **Section 4, Step 1 ("Identify Implemented Pattern")** of the `Layer-3-Routers_Blueprint.md`. Is it attempting the **Standard Pattern** (delegation) or the **Router-Handled Simple CRUD** pattern (if applicable/defined)?
2.  **Assess Against Blueprint Criteria:**
    - **If Standard Pattern:** Thoroughly review it against all criteria in **Section 2.2 (Key Compliance Criteria for Standard Pattern)** of the Blueprint. Verify delegation, session passing, transaction initiation (`async with db.begin():`), auth dependencies, schema usage, and absence of business logic.
    - **If Router-Handled Simple CRUD Exception Pattern:** Thoroughly review it against the criteria in **Section 3.1 (Key Compliance Criteria for Exception Pattern)** of the Blueprint. Verify it meets the simplicity/scope limits AND still complies with general Layer 3 standards (auth, schemas, naming, etc.).
3.  **Identify ALL Deviations:** Note every instance where the code does not meet the requirements of its identified pattern (or the general Layer 3 standards).

### Step 2.3: Populate Audit Report / Cheat Sheet (Layer 3 Section)

For each identified endpoint within each file:

1.  **File Path:** Document the full path to the file (e.g., `src/routers/users.py`).
2.  **Component Name:** Specify the endpoint function name and HTTP method/path (e.g., `Endpoint: POST /api/v3/users/`).
3.  **Identified Pattern:** State the pattern identified in Step 2.2.1 (e.g., "Standard Pattern", "Router-Handled Simple CRUD").
4.  **Gap Analysis (Technical Debt Identification):**
    - Follow the logic outlined in **Section 4, Step 3 ("Document Technical Debt")** of the `Layer-3-Routers_Blueprint.md`.
    - Clearly list each deviation from the Blueprint identified in Step 2.2.
    - **Crucially, flag:**
      - Business logic found in the router.
      - Missing/incorrect transaction management (`async with db.begin():`).
      - Missing/incorrect authentication dependencies.
      - Incorrect session handling/passing to Layer 4.
      - Use of Router-Handled Simple CRUD beyond its strict scope.
    - For each deviation, reference the specific Blueprint section/criterion (e.g., "Blueprint 2.2.5: Business logic present in router.", "Blueprint 2.2.3.2: Missing `async with db.begin()` for write operation.", "Blueprint 3.1.4: Logic exceeds scope for Router-Handled Simple CRUD exception.").
    - Use `<!-- NEED_CLARITY: [Your question here] -->` if compliance is ambiguous.
5.  **Prescribed Refactoring Actions:**
    - Suggest concrete actions aligned with **Section 4, Step 4 ("Prescribe Refactoring Actions")** of the `Layer-3-Routers_Blueprint.md`.
    - Prioritize actions addressing transaction, auth, and business logic placement issues.
    - Examples:
      - "Move logic block [lines X-Y] to a new service function in Layer 4."
      - "Wrap lines [A-B] in an `async with db.begin():` block."
      - "Add `current_user: UserRead = Depends(get_current_active_user)` to endpoint signature."
      - "Refactor endpoint to follow Standard Pattern by creating and calling Layer 4 service function."
6.  **Verification Checklist (Post-Refactoring - Optional):**
    - List key items to check (e.g., "Verify logic moved to service," "Confirm `async with db.begin()` is present," "Check auth dependency added").

### Step 2.4: Review and Finalize

1.  Ensure all files in `src/routers/` and all endpoints within them have been assessed.
2.  Verify that the audit report/cheat sheet entries clearly state the identified pattern and list specific, actionable gaps referencing the Layer 3 Blueprint.
3.  Mark any sections with `<!-- STOP_FOR_REVIEW -->` if human review is required.

---

## 3. Output

- An updated audit checklist, report, or workflow-specific cheat sheet with a comprehensive Layer 3 assessment for all routers and endpoints.

---

This SOP is a living document and may be updated as the Blueprint evolves or new insights are gained.
