# Standard Work Order Process

**Version:** 1.0
**Date:** 2025-05-15

## 1. Purpose

This document outlines the standard process for creating, managing, executing, and completing Work Orders (WOs) within the Voice Automated Email Template System project. Adherence to this process ensures clarity, traceability, consistent documentation, and effective collaboration between human and AI team members acting in various personas.

## 2. Overview

A Work Order is a formal directive to perform a specific set of tasks to achieve a defined goal. It serves as a central reference point for a unit of work. The lifecycle of a WO is tightly integrated with the project's other management tools: `tasks.yml`, the `journal/` directory (and `journal_index.yml`), and `Handoff/` documents.

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
*   **Prerequisite:** A corresponding Task **must** already exist in `tasks.yml` (see Section 6.1 for Task creation protocol, typically USER-directed). The `Task ID` from this existing task will be used in the Work Order.
*   **Action (Typically USER-directed, or by a designated planning persona):**
    1.  Create a new Work Order Markdown file in the `work_orders/active/` directory.
        *   **Filename Convention:** `WO_<TASKID>_<YYYYMMDD>_<3-5-word-label>.md` (e.g., `WO_TASK007_20250517_New-Hero-Variants.md`). `<TASKID>` is the ID from the **pre-existing Task** in `tasks.yml`, and `<YYYYMMDD>` is the WO creation date.
    2.  Populate the WO document with all mandatory contents (see Section 5).
    3.  Ensure the `tasks.yml` entry for the related Task is updated to reflect the Work Order's existence and assignment if necessary (e.g., adding the WO ID to `related_files` or updating status to `in_progress_wo`).

### 4.2. Work Order Assignment

*   The `Assigned Persona(s)` field in the WO clearly designates who is responsible for execution.
*   The corresponding task in `tasks.yml` should also reflect this assignment.

### 4.3. Work Order Execution

*   The assigned persona (often an AI assistant guided by the user) takes the WO document as the primary directive.
*   The AI assistant should confirm its understanding of the WO's objectives and scope with the guiding user/persona.
*   Work is performed as detailed in the WO, utilizing specified input documents and aiming for the defined deliverables.

### 4.4. Work Order Completion & Documentation Protocol (CRITICAL)

The completion of a Work Order is not just the creation of its primary deliverables but also the meticulous documentation of the work. **All of the following steps are mandatory for a WO to be considered complete:**

1.  **Primary Deliverables Met:** All items listed under "Expected Deliverables/Outputs" in the WO have been produced and are in their correct locations.
2.  **Journal Entry Creation:**
    *   **Responsibility:** Executing Persona.
    *   **Action:** Create a new Markdown journal file in the `journal/` directory.
        *   **Filename:** `JE_<YYYYMMDD_HHMMSS>_<TASKID>_<1-3-word-summary>.md` (e.g., `JE_20250517_103000_TASK007_Hero-Done.md`). `<YYYYMMDD_HHMMSS>` is the UTC timestamp, and `<TASKID>` is from `tasks.yml`.
        *   **Content:** Must include:
            *   Timestamp.
            *   Participants (including the executing persona).
            *   **Explicit reference to the `Work Order ID` (e.g., "This entry details the completion of WO003.").**
            *   Detailed summary of actions taken, decisions made, problems encountered (and solutions), and a list of all files created, modified, or deleted.
    *   **Index Update:** Add a corresponding entry to `journal_index.yml` as per the project's `README.md` guidelines.
3.  **Task Update in `tasks.yml`:**
    *   **Responsibility:** Executing Persona.
    *   **Action:** Update the status of the corresponding task (identified by `Task ID` in the WO) in `tasks.yml` to `done`.
        *   If a review stage is required by a different persona, the status may first be set to `review`.
        *   The task entry in `tasks.yml` should, if possible, be updated to include a reference to the `Work Order ID` and the filename of the completion `Journal Entry`.
4.  **Handoff Document Creation:**
    *   **Trigger:** A Handoff Document is created if the completion of the current Work Order (WO1) has led to the USER-directed identification and creation of new, subsequent Work Order(s) (WO2, WO3, etc., each tied to a newly created Task).
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
4.  `Related Task ID in tasks.yml:` (The `id` of the corresponding task in `tasks.yml`)
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
    *   [ ] `tasks.yml` Updated (Task ID: _________ set to `done`/`review`)
    *   [ ] Handoff Document Created (Filename: ____________________)
    *   [ ] WO Archived (Moved to `work_orders/completed/`)

## 6. Integration with Other Project Management Tools

### 6.1. `tasks.yml`

*   For every WO created, a corresponding task **must** be created in `tasks.yml`.
*   The `tasks.yml` entry should include the `Work Order ID` in its `description` or a dedicated `related_wo_id` field for easy cross-referencing.
*   The status of the task in `tasks.yml` reflects the status of the WO.

### 6.2. `journal/` and `journal_index.yml`

*   Key decisions during WO execution *may* warrant interim journal entries.
*   A comprehensive journal entry detailing the WO's completion is **mandatory** as per Section 4.4.2.
*   All journal entries related to a WO should reference the `Work Order ID`.

### 6.3. `Handoff/`

*   A Handoff document is **mandatory** upon WO completion, as per Section 4.4.4.
*   It summarizes the WO outcome and points to the detailed journal entry.

## 7. Process Adherence

Strict adherence to this Work Order Process is crucial for maintaining project clarity, ensuring comprehensive documentation ("popcorn trail"), and facilitating seamless collaboration between all team members, especially when transitioning work between sessions or AI assistants.
