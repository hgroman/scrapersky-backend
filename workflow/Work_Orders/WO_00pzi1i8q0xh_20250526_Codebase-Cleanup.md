# Work Order: Codebase and Documentation Cleanup Initiative

**Work Order ID:** WO_00pzi1i8q0xh_20250526_Codebase-Cleanup
**Title:** Codebase and Documentation Cleanup Initiative
**Status:** Open
**Related Task ID in DART:** 00pzi1i8q0xh
**Input Documents/Prerequisites:**
- Git Status and Diff Analysis (provided by AI)
- DART Task: Document: Places Staging Error Handling Logic (ID: FVkuUV7b0zWY)
- DART Task: Document: Old Documentation Cleanup and Archiving (ID: ble1Qug5utlJ)
- DART Task: Review and Document: Untracked Files and Directories (ID: BDcNcsWGaYp2)
**Date Created:** 2025-05-26
**Created By Persona:** Cline (AI Assistant)
**Assigned Persona(s):** User, Cline (AI Assistant)
**Objective:** To systematically address and document all unaccounted-for code changes, old documentation, and untracked files/directories identified during the recent `git status` and `git diff` analysis. This initiative aims to ensure all project assets are properly tracked, documented, and aligned with DART.

**Expected Deliverables/Outputs:**
- All unaccounted code changes documented in DART tasks with associated journal entries.
- Old documentation files either removed, properly archived, or their status clarified.
- All untracked files and directories reviewed, their purpose determined, and either documented in DART, added to `.gitignore`, or removed.
- Updated `git status` showing a clean working directory (or only expected changes).

**Detailed Steps:**

1.  **Document Places Staging Error Handling Logic:**
    *   Create a DART Document Journal Entry for DART Task `FVkuUV7b0zWY`.
    *   Detail the changes made to `src/routers/places_staging.py` (added `deep_scan_status` to `Error` and `deep_scan_error`).
    *   Link the journal entry to the DART task.

2.  **Document Old Documentation Cleanup and Archiving:**
    *   Create a DART Document Journal Entry for DART Task `ble1Qug5utlJ`.
    *   Detail the deletion of old documentation files from `Docs/Docs_6_Architecture_and_Status/Archive/` and `Core_Architecture/`.
    *   Clarify the purpose of the new `_Archive/` directory.
    *   Link the journal entry to the DART task.

3.  **Review and Document Untracked Files and Directories:**
    *   For DART Task `BDcNcsWGaYp2`, systematically review each untracked item:
        *   `.envrc`
        *   `.specstory/history/2025-05-22_06-20-vector-database-architecture-discussion.md`
        *   `Docs/Docs_11_Refactor/`
        *   `Docs/Docs_12_Persona_Nursery/`
        *   `Docs/Docs_15_Master_Plan/`
        *   `Docs/Docs_6_Architecture_and_Status/ScraperSky_Architectural_Anti-patterns_and_Standards.md`
        *   `dev_environment_setup.md`
        *   `scripts/`
        *   `workflow/Journal/JE_20250526_090211_TASK_Linter_Error_Fix_Places_Staging.md`
    *   For each item, determine if it's part of an ongoing, undocumented task (create a new DART task for it), a temporary file (delete it), or a new, permanent part of the project (document its purpose and add to `.gitignore` if appropriate).
    *   Ensure the untracked journal entry `workflow/Journal/JE_20250526_090211_TASK_Linter_Error_Fix_Places_Staging.md` is committed and linked to the DART task created for the `places_staging.py` changes (FVkuUV7b0zWY).
    *   Create a DART Document Journal Entry for DART Task `BDcNcsWGaYp2` summarizing the findings and actions taken for these untracked items.

**Completion Checklist (Cross-reference to Section 4.4 of Work_Order_Process.md):**
- [ ] Primary Deliverables Met
- [ ] Journal Entry Created (Filename: N/A - DART Documents are primary)
- [ ] DART Task Updated (Task ID: 00pzi1i8q0xh set to `done`/`review`)
- [ ] Handoff Document Created (Filename: ____________________)
- [ ] WO Archived (Moved to `work_orders/completed/`)
