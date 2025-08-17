# 11_WF7_Component_Renaming_Work_Order.md

**Work Order ID:** WF7-RENAME-20250802-001
**Date:** 2025-08-02
**Responsible Persona:** V2 WF7 Workflow Agent
**Status:** Pending Execution

---

## 1. Purpose

To rename all components *created* specifically for the V2 WF7 "Extractor" workflow, ensuring strict adherence to the new V2 Component Naming Convention as defined in the ScraperSky Development Constitution (Article III, Section 1, Point 7).

This renaming introduces mandatory thoroughness, forces awareness of impact, and facilitates ripple effect detection for any future changes.

## 2. Guiding Principle

**ScraperSky Development Constitution - Article III, Section 1, Point 7: V2 Component Naming Convention**

*   **Format:** `WFx-V2-L[Layer#]-[Seq#ofTotal#]-[DescriptiveName].py`
*   **Rationale:** Introduces mandatory thoroughness, forces awareness of impact, and enables immediate ripple effect detection for any changes. It ensures absolute clarity, traceability, and auditability.

## 3. Scope of Work

This work order covers the renaming of files that were *newly created* as part of the V2 WF7 implementation. Existing V1 files that were modified (e.g., `src/models/page.py`, `src/config/settings.py`, `src/main.py`) are considered integration points and will retain their original names to avoid breaking V1 functionality, aligning with the "Strict Parallelism for V2" non-negotiable.

## 4. Files to be Renamed

Below is the list of files to be renamed, categorized by their architectural layer. The `[Seq#ofTotal#]` will be determined based on the count of files within that specific layer for WF7.

### Layer 1: Data Models
*   **Current Name:** `src/models/contact.py`
*   **Proposed New Name:** `src/models/WF7-V2-L1-1of1-ContactModel.py`
    *   *(Rationale: This is the only new L1 file created for WF7.)*

### Layer 3: Routers
*   **Current Name:** `src/routers/v2/pages.py`
*   **Proposed New Name:** `src/routers/v2/WF7-V2-L3-1of1-PagesRouter.py`
    *   *(Rationale: This is the only new L3 file created for WF7.)*

### Layer 4: Services & Schedulers
*   **Current Name:** `src/services/page_curation_service.py`
*   **Proposed New Name:** `src/services/WF7-V2-L4-1of2-PageCurationService.py`
    *   *(Rationale: This is the first of two new L4 files created for WF7.)*

*   **Current Name:** `src/services/page_curation_scheduler.py`
*   **Proposed New Name:** `src/services/WF7-V2-L4-2of2-PageCurationScheduler.py`
    *   *(Rationale: This is the second of two new L4 files created for WF7.)*

## 5. Execution Steps

1.  **Rename Files:** Execute the necessary file system commands to rename each file to its proposed new name.
2.  **Update Import Paths:** For each renamed file, update all corresponding import statements in other files that reference it (e.g., `src/main.py`, `src/services/WF7-V2-L4-2of2-PageCurationScheduler.py` will need to import `src/services/WF7-V2-L4-1of2-PageCurationService.py`).
3.  **Verify Server Startup:** After all renames and import updates, perform a full server startup test (`python -m uvicorn src.main:app --reload`) to ensure no import errors or runtime issues were introduced.
4.  **Verify WF7 Functionality:** Re-run the WF7 end-to-end test protocol to confirm the workflow remains fully operational.

## 6. Verification & Sign-off

*   **Verification:**
    *   All specified files have been renamed according to the new convention.
    *   All import paths referencing these files have been correctly updated.
    *   The ScraperSky backend starts without errors.
    *   The WF7 "Extractor" workflow functions correctly end-to-end.

*   **Sign-off:**
    *   [V2 WF7 Workflow Agent Signature/Confirmation]

---

This work order is a non-negotiable step towards enforcing the V2 Component Naming Convention. Its successful execution will demonstrate the mandatory thoroughness required for all future V2 development.