# Documentation 2025 (The Fresh Start)

**Established:** 2025-11-22
**Status:** The Only Source of Truth

## Welcome to the Clean Room

This directory contains **only** documentation that has been verified against the codebase as of November 2025.

If a document is here, it is **true**.
If a document is in the old `Documentation/` folder, it is **suspect** until proven otherwise.

## Directory Structure

*   **`00_STATE_OF_THE_NATION.md`**: The high-level executive summary of the project status.
*   **`MANIFEST.md`**: The automated list of actual code files (Routers, Services, Models).
*   **`Core/`**: Fundamental philosophies and architectural pillars.
*   **`Guides/`**: "How-to" playbooks for developers (e.g., Integration Playbook).
*   **`Reports/`**: Formal audit reports and investigation findings.
*   **`Architecture/`**: Deep dives into system design (currently empty, awaiting migration).

## The Migration Rule

To move a document from `Documentation/` to here, you must:
1.  **Read it.**
2.  **Verify it** against `MANIFEST.md`.
3.  **Update it** if it references dead code (e.g., `v2/` paths).
4.  **Move it.**

**Do not pollute this directory with fiction.**
