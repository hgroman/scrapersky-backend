# Work Order: Workflow Artifact Audit and Correction

**Task ID:** TASK_SS_010
**Date Issued:** 2025-05-19
**Status:** Completed
**Assigned To:** AI Assistant (Workflow Specialist)
**Overseen By:** David (Shepherd), AI Director

---

## 1. Objective

To systematically audit all existing workflow artifacts, including `tasks.yml`, all journal entries (`workflow/Journal/`), work orders (`workflow/Work_Orders/`), handoff documents (`workflow/Handoff/`), and `workflow/journal_index.yml`. The goal is to identify and correct any inconsistencies in naming conventions, linking to parent Tasks, internal cross-referencing, and overall adherence to the "Task is god" principle.

All corrections must align with the standards and procedures documented in `workflow/README_WORKFLOW.md` and `workflow/Work_Order_Process.md`.

## 2. Scope

This Work Order covers the following:

- **Master Task List:** `workflow/tasks.yml`
- **Journal Entries:** All files within the `workflow/Journal/` directory and its subdirectories.
- **Work Orders:** All files within the `workflow/Work_Orders/` directory (excluding this document itself initially, but it should be conformed once its own task is registered if any deviations are noted during its creation).
- **Handoff Documents:** All files within the `workflow/Handoff/` directory.
- **Journal Index:** `workflow/journal_index.yml`

The audit applies to all artifacts existing as of the date of this Work Order.

## 3. Authoritative References

The following documents provide the definitive standards for this audit and correction process:

- **`workflow/README_WORKFLOW.md`**: Contains the non-negotiable workflow rules, "Task is god" principle, artifact hierarchy, naming conventions, and the "Rule of Thumb" for artifact creation and linking.
- **`workflow/Work_Order_Process.md`**: Provides detailed specifications for naming conventions and task lifecycle management.

## 4. Specific Tasks to be Performed

The executor will perform the following actions:

1.  **Review `tasks.yml`:**

    - Verify that all Task IDs are unique and follow a sequential or otherwise logical pattern (e.g., `TASK_SS_XXX`).
    - Ensure all essential fields for each task are present.
    - Note any tasks that appear to be duplicates or obsolete for potential archival (to be decided separately).

2.  **Scan and Audit Journal Entries (`workflow/Journal/`):**

    - For each file:
      - Verify the filename strictly adheres to the `JE_<YYYYMMDD_HHMMSS>_<TASKID>_<summary>.md` convention.
      - Confirm that the `<TASKID>` in the filename corresponds to a valid Task ID present in `workflow/tasks.yml`.
      - (Optional but Recommended) Check if the content of the JE internally references its parent Task ID.
      - Correct filenames as needed. If a Task ID is missing or invalid but can be reliably inferred from the content or context, update the filename and internal references.
      - Document any JEs where the Task ID cannot be reliably determined.

3.  **Scan and Audit Work Orders (`workflow/Work_Orders/`):**

    - For each file (excluding this WO initially):
      - Verify the filename strictly adheres to the `WO_<TASKID>_<YYYYMMDD>_<label>.md` convention.
      - Confirm that the `<TASKID>` in the filename corresponds to a valid Task ID present in `workflow/tasks.yml`.
      - Verify that the content _within_ the Work Order explicitly references its parent Task ID.
      - Correct filenames and internal references as needed. If a Task ID is missing or invalid but can be reliably inferred, update accordingly.
      - Document any WOs where the Task ID cannot be reliably determined or corrected.

4.  **Scan and Audit Handoff Documents (`workflow/Handoff/`):**

    - For each file:
      - Verify the filename strictly adheres to the `HO_<YYYYMMDD_HHMMSS>_<TASKID>_<summary>.md` convention.
      - Confirm that the `<TASKID>` in the filename corresponds to a valid Task ID present in `workflow/tasks.yml`.
      - Verify that the content _within_ the Handoff Document explicitly references its parent Task ID (and ideally the associated Work Order ID, if applicable).
      - Correct filenames and internal references as needed. If a Task ID is missing or invalid but can be reliably inferred, update accordingly.
      - Document any HOs where the Task ID cannot be reliably determined or corrected.

5.  **Update `workflow/journal_index.yml`:**
    - Ensure that for every Journal Entry file in `workflow/Journal/`, there is a corresponding and accurate entry in `workflow/journal_index.yml`.
    - Reflect any filename changes made to Journal Entries in their respective `journal_index.yml` entries.
    - Add entries for any JEs found that were not indexed. Remove entries for JEs that no longer exist (if any).

## 5. Handling Unresolvable Inconsistencies

- If an artifact's correct Task ID cannot be confidently determined after reasonable investigation, or if other ambiguities prevent full correction:
  - The artifact should be renamed to include a `NEEDS_REVIEW_` prefix in its filename (e.g., `NEEDS_REVIEW_JE_...`).
  - A specific section in the completion report (see below) should list these items with a brief explanation of the issue.
- No artifacts should be deleted without explicit approval.

## 6. Reporting and Success Criteria

- **Completion Report:** Upon completion of the audit and correction tasks, the executor will produce a brief report summarizing:
  - Number of files scanned per category (JE, WO, HO).
  - Number of files corrected per category.
  - A list of any files marked with `NEEDS_REVIEW_` and the reason.
  - Confirmation that `workflow/journal_index.yml` is up-to-date.
- **Success Criteria:**
  - All files in `workflow/Journal/`, `workflow/Work_Orders/`, and `workflow/Handoff/` (excluding those marked `NEEDS_REVIEW_`) conform to the documented naming conventions.
  - Every JE, WO, and HO filename and its internal content (where applicable) correctly references a valid Task ID listed in `workflow/tasks.yml`.
  - `workflow/journal_index.yml` is an accurate and complete index of all journal entries in `workflow/Journal/`.
  - `workflow/tasks.yml` has been reviewed for basic integrity.

---

**Director's Note:** This is a foundational cleanup task. Precision and adherence to the referenced standards are paramount. The goal is to establish a clean baseline for all workflow artifacts, ensuring system-wide consistency and traceability. - David (Shepherd)
