# Layer Guardian Execution & Closure Protocol

**Version:** 1.0
**Status:** Proposed
**Governs:** The "Art of Fixing" Phase

---

## 1.0 Purpose

This document governs the final phase of the remediation lifecycle: the execution of the fix and the closure of the corresponding task. Its purpose is to ensure that the rich, authoritative context gathered during the "Art of Becoming" is permanently embedded in the project's history at the point of change.

This protocol is engaged *after* a remediation requirement has been fully documented in DART and is ready for implementation by either a Guardian Persona or a human developer.

---

## 2.0 Mandatory Closure Protocol

When a remediation task is executed, the following closure protocol is **MANDATORY** to ensure end-to-end traceability:

1.  **Code Commit Message:** The commit message for the code change **MUST** reference the DART task ID and the specific blueprint principle being addressed.
    *   **Format:** `[L{LayerNumber}] Fix({File Name}): {Brief Summary} - Closes #{DART_TASK_ID}`
    *   **Body:** `This commit addresses a violation of Blueprint Principle {Principle Number/Name}: {Principle Description}. The changes align the code with the governing document: {Governing Doc Path}.`

2.  **DART Task Closure:** When marking the DART task as complete, a final comment **MUST** be added.
    *   **Comment Format:** `Remediation complete. The code has been aligned with Blueprint Principle {Principle Number/Name}. See commit: {Commit SHA/URL}.`

This protocol ensures that the 'why' behind every change is permanently recorded in the version control history, providing invaluable context for future developers and auditors.
