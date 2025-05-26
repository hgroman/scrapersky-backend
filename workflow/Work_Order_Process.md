# Standard Work Order Process

> ⚠️ **NON-NEGOTIABLE WORKFLOW RULE** ⚠️
>
> **ALL work MUST begin by creating a new Task in DART using MCP. When continuing existing work, ensure the Task in DART remains the fountainhead for all related artifacts.**
>
> **NO artifact (journal entry, work order, handoff, etc.) may reference a Task that does not exist in DART.**
>
> **Artifacts referencing a non-existent Task are INVALID and must be corrected immediately.**
>
> **NO EXCEPTIONS. This is the law of the workflow.**

**Version:** 2.0 (DART Integration)
**Date:** 2025-05-21

## 1. Purpose

This document outlines the standard process for creating, managing, executing, and completing Work Orders (WOs) within the Voice Automated Email Template System project. Adherence to this process ensures clarity, traceability, consistent documentation, and effective collaboration between human and AI team members acting in various personas.

## 2. Overview

A Work Order is a formal directive to perform a specific set of tasks to achieve a defined goal. It serves as a central reference point for a unit of work. The lifecycle of a WO is tightly integrated with the project's other management tools: **DART MCP** (for task and document management), and `Handoff/` documents. While local journal files may still be used for very detailed, temporary, or complex notes, the primary and authoritative record for all work progress and completion is now a **DART Document Journal Entry**. A key aspect of our workflow is the continuous identification and documentation of reusable patterns, as detailed in Section 9.

## 3. Personas and Responsibilities

Different project personas interact with Work Orders at various stages:

*   **Initiator/Definer (e.g., MJML Component Architect, Project Lead):** Identifies the need for a WO, defines its scope and objectives, and creates the initial WO document.
*   **Executor (e.g., MJML Developer AI, Content Strategist AI):** Assigned the WO, performs the work described, and is responsible for the primary documentation upon completion.
*   **Reviewer (Optional, e.g., MJML Component Architect, User):** May review the deliverables of a WO before it's formally closed.

## 4. Work Order Lifecycle

### 4.1. Work Order Initiation

*   **Trigger:**
    *   New project requirements or features.
    *   Phased completion of a larger initiative.
    *   Specific user requests.
    *   Outputs or plans from another persona (e.g., a Content Strategist's email plan requiring new components).
    *   Follow-up actions from a previous Work Order or journal entry.
*   **Responsibility:** Typically an Architect, Lead, or designated planning persona, acting upon USER direction.
*   **Prerequisite:** A corresponding Task **must** already exist in **DART** (see Section 6.1 for Task creation protocol, typically USER-directed). The `Task ID` from this existing DART task will be used in the Work Order.
*   **Action (Typically USER-directed, or by a designated planning persona):**
    1.  Create a new Work Order Markdown file in the `work_orders/active/` directory.
        *   **Filename Convention:** `WO_<TASKID>_<YYYYMMDD>_<3-5-word-label>.md` (e.g., `WO_TASK007_20250517_New-Hero-Variants.md`). `<TASKID>` is the ID from the **pre-existing Task** in **DART**, and `<YYYYMMDD>` is the WO creation date.
    2.  Populate the WO document with all mandatory contents (see Section 5).
    3.  Ensure the **DART task** for the related Task is updated to reflect the Work Order's existence and assignment if necessary (e.g., updating status or adding notes about the WO ID).

### 4.2. Work Order Assignment

*   The `Assigned Persona(s)` field in the WO clearly designates who is responsible for execution.
*   The corresponding task in **DART** should also reflect this assignment.

### 4.3. Work Order Execution

*   The assigned persona (often an AI assistant guided by the user) takes the WO document as the primary directive.
*   The AI assistant should confirm its understanding of the WO's objectives and scope with the guiding user/persona.
*   Work is performed as detailed in the WO, utilizing specified input documents and aiming for the defined deliverables.

### 4.4. Work Order Completion & Documentation Protocol (CRITICAL)

The completion of a Work Order is not just the creation of its primary deliverables but also the meticulous documentation of the work. **All of the following steps are mandatory for a WO to be considered complete:**

1.  **Primary Deliverables Met:** All items listed under "Expected Deliverables/Outputs" in the WO have been produced and are in their correct locations.
2.  **Journal Entry Creation (DART Document Primary):**
    *   **Responsibility:** Executing Persona.
    *   **Action (Primary - DART Document):** Create a new **DART Document Journal Entry** using the `create_doc` MCP tool. This document serves as the primary, authoritative record of work progress and completion.
        *   **Title:** Human-friendly summary (e.g., "Email Scanner Authentication Fix").
        *   **Content:** Detailed work summary, debugging steps, learnings, decisions, and a list of all files created, modified, or deleted.
        *   **Linking:** The DART Document must be linked directly to its parent DART Task, and the Task description should be updated with a markdown link to the DART Document (e.g., `[Document Title](document_htmlUrl)`).
        *   **Note:** For minor fixes or simple updates (like a tooling resolution that doesn't justify a full document), the DART Task description itself can serve as the journal entry, or a concise DART Document can be created.
    *   **Action (Optional - Local Journal File):** For very detailed, complex, or temporary notes that are not suitable for a concise DART Document, a local Markdown journal file *may* still be created in the `journal/` directory.
        *   **Filename:** `JE_<YYYYMMDD_HHMMSS>_<TASKID>_<1-3-word-summary>.md` (e.g., `JE_20250517_103000_TASK007_Hero-Done.md`). `<YYYYMMDD_HHMMSS>` is the UTC timestamp, and `<TASKID>` is from **DART**.
        *   **Content:** Should include explicit reference to the `Work Order ID` and the corresponding DART Task ID.
        *   **Important:** Local journal files are secondary and do **not** require updates to `journal_index.yml` as DART now manages document organization.
3.  **Task Update in DART:**
    *   **Responsibility:** Executing Persona.
    *   **Action:** Update the status of the corresponding task (identified by `Task ID` in the WO) in **DART** to `done`.
        *   If a review stage is required by a different persona, the status may first be set to `review`.
        *   The task in **DART** should, if possible, be updated to include notes about the `Work Order ID` and the filename of the completion `Journal Entry`.
4.  **Handoff Document Creation:**
    *   **Trigger:** A Handoff Document is created if the completion of the current Work Order (WO1) has led to the USER-directed identification and creation of new, subsequent Work Order(s) (WO2, WO3, etc., each tied to a newly created Task in **DART**).
    *   **Purpose:** To provide essential context, outputs, and a "note to self" from the AI completing WO1 to the AI/session that will execute the subsequent WO(s).
    *   **Responsibility:** Executing Persona for WO1.
    *   **Action:**
        1.  Ensure the new follow-on Task(s) and corresponding Work Order(s) have been created as per USER direction (following protocol in 4.1).
        2.  Create a new Markdown handoff file in the `Handoff/` directory.
            *   **Filename:** `HO_<YYYYMMDD_HHMMSS>_<TASKID_of_WO1>_<summary_of_WO1_completion>.md` (e.g., `HO_20250516_103500_TASK007_WO1-Done_Prep-For-WO2.md`). `<YYYYMMDD_HHMMSS>` is the UTC timestamp of HO creation.
    *   **Content:** Must include:
        *   Timestamp of HO creation.
        *   **Explicit reference to the completed `Work Order ID` (WO1).**
        *   **Explicit reference to the `Journal Entry file` created for WO1's completion (as per step 4.4.2).**
        *   A concise summary of WO1's key outcomes, learnings, and the current project status relevant to the follow-on work.
        *   **Crucially, clear pointers to the newly created subsequent Work Order ID(s) (WO2, WO3, etc.) and their respective Task ID(s).**
        *   Any specific advice, data, or context from WO1 that is vital for the successful execution of the subsequent WO(s).
5.  **Work Order Archival (Optional but Recommended):**
    *   Move the completed WO document from `work_orders/active/` to `work_orders/completed/`. This keeps the active WO directory focused.

## 5. Work Order Document: Mandatory Contents

Each Work Order document (`.md` file in `work_orders/active/` or `work_orders/completed/`) **must** contain the following sections/information:

1.  `Work Order ID:` (Unique, e.g., `WO003`)
2.  `Title:` (Clear, concise title)
3.  `Status:` (e.g., `Open`, `In Progress`, `Blocked`, `Review`, `Done`)
4.  `Related Task ID in DART:` (The `id` of the corresponding task in **DART**)
5.  `Input Documents/Prerequisites:` (List of all files or information needed to start, e.g., analysis reports, previous Handoff docs, specific component files)
6.  `Date Created:` (YYYY-MM-DD)
7.  `Created By Persona:` (The persona initiating the WO)
8.  `Assigned Persona(s):` (The persona(s) responsible for execution)
9.  `Priority:` (e.g., `High`, `Medium`, `Low` - Optional)
10. `Due Date:` (YYYY-MM-DD - Optional)
11. `Objective/Goal:` (A clear statement of what the WO aims to achieve)
12. `Background/Context:` (Brief explanation of why this WO is needed)
13. `Scope of Work / Detailed Tasks:` (A breakdown of the specific actions to be performed. Can be a checklist.)
14. `Expected Deliverables/Outputs:` (A clear list of what will be produced, e.g., new files, modified files, specific documentation updates, with expected locations.)
15. `Completion Checklist (Cross-reference to Section 4.4):`
    *   [ ] Primary Deliverables Met
    *   [ ] Journal Entry Created (Filename: ____________________)
    *   [ ] **DART Task Updated** (Task ID: _________ set to `done`/`review`)
    *   [ ] Handoff Document Created (Filename: ____________________)
    *   [ ] WO Archived (Moved to `work_orders/completed/`)

## 6. Integration with Other Project Management Tools

### 6.1. DART (Task Management)

*   For every WO created, a corresponding task **must** be created in **DART**.
*   The **DART task** should include the `Work Order ID` in its description or notes for easy cross-referencing.
*   The status of the task in **DART** reflects the status of the WO.
*   **Task Creation:** Use DART MCP to create tasks with proper tagging (Layer, Workflow, Priority) and incremental TASK_XXX IDs.
*   **Task Queries:** Use DART MCP to find next available task ID, filter by status, or search by criteria.

### 6.2. DART Document Journal Entries (Primary Journaling)

*   **Primary Record:** All comprehensive journal entries detailing WO execution and completion are now managed as **DART Documents**. This ensures centralized, searchable, and version-controlled documentation directly linked to DART Tasks.
*   **No `journal_index.yml`:** The `journal_index.yml` file is no longer required as DART natively manages the organization and discoverability of DART Documents.
*   **Local Journal Files (Optional):** Local Markdown files in the `journal/` directory are now considered optional. They may be used for very detailed, temporary, or complex notes that are not suitable for direct inclusion in a concise DART Document. If used, they should still reference the `Work Order ID` and the corresponding **DART Task ID**.

### 6.3. `Handoff/`

*   A Handoff document is **mandatory** upon WO completion if follow-up WOs are created, as per Section 4.4.4.
*   It summarizes the WO outcome and points to the detailed journal entry.
*   References both the completed WO and the newly created **DART tasks** for subsequent work.

## 7. DART MCP Integration Benefits

The integration with DART MCP provides several advantages over the previous tasks.yml approach:

*   **No File Parsing Issues:** AI assistants can query DART directly without truncation problems
*   **Real-time Task Management:** Instant access to current task status and next available task IDs
*   **Rich Metadata:** Advanced filtering by Layer, Workflow, Priority, and custom tags
*   **Cross-session Continuity:** Task context persists across different AI sessions and tools
*   **Structured Queries:** Natural language task management ("Show me all critical Layer 4 tasks")

## 8. Process Adherence

Strict adherence to this Work Order Process is crucial for maintaining project clarity, ensuring comprehensive documentation ("popcorn trail"), and facilitating seamless collaboration between all team members, especially when transitioning work between sessions or AI assistants. The integration with DART MCP enhances this process by providing robust, scalable task management while preserving all established workflow principles.

## 9. Continuous Improvement: Pattern Identification and Documentation

As a core practice, all participants in this workflow are **continuously engaged in identifying and documenting reusable patterns**—both "good patterns" (best practices, effective solutions) and "anti-patterns" (issues to avoid). This effort is crucial for building our collective knowledge base, accelerating future development, and preventing regressions.

When working on any task or Work Order, if you encounter a recurring problem, discover an elegant solution, or identify a new architectural standard, please consider documenting it as a dedicated "Fix Pattern" or "Good Pattern" markdown file (e.g., in `Docs/Docs_11_Refactor/LayerX_Fix_Patterns/`) and creating a corresponding DART task to track its integration into the vector database. This proactive knowledge capture is a vital part of our commitment to AI-native software engineering.
