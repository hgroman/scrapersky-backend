# Standardized Workflow Documentation System

> ⚠️ **NON-NEGOTIABLE WORKFLOW RULE** ⚠️
>
> **ALL work MUST begin by registering a new Task in `workflow/tasks.yml`, using the next available Task ID (incrementing from the last entry).**
>
> **NO artifact (journal entry, work order, handoff, etc.) may reference a Task that does not exist in `workflow/tasks.yml`.**
>
> **Artifacts referencing a non-existent Task are INVALID and must be corrected immediately.**
>
> **NO EXCEPTIONS. This is the law of the workflow.**

> **Purpose** Build and maintain an AI-assisted, IDE-native workflow for complex projects (e.g., code standardization, content generation, system audits) that require consistent, traceable, and quality-assured outputs.

---

## 📑 Table of Contents

1.  [Overview](#overview)
2.  [Participant Roles (AI/Human)](#participant-roles-aihuman)
3.  [Project Structure](#project-structure)
4.  [Naming Conventions](#naming-conventions)
5.  [Getting Started](#getting-started)
6.  [Contributor Onboarding Checklist](#contributor-onboarding-checklist)
7.  [Workflow Process Guides](#workflow-process-guides)
8.  [General Lessons Learned](#general-lessons-learned)
9.  [Task-Centric Artifact Relationships](#task-centric-artifact-relationships)

---

## Overview

This system facilitates the execution of complex tasks through a structured process. **The cornerstone of this system is the Task. The Task is the root and historic register of all work. All workflow artifacts (journal entries, work orders, handoff documents) must explicitly reference their parent Task.**

**Hierarchy:**

- The Task is the "god" object. Every artifact is a child of a Task.
- Simple tasks may only require a journal entry.
- Medium tasks may require a journal entry and a work order.
- Large or impactful tasks may require a journal entry, work order, and a handoff document.
- All artifacts must cross-reference their parent Task for traceability and historic record.

**Artifact Relationships:**

- **Task** (root)
  - **Journal Entry** (child, always references Task)
  - **Work Order** (child, always references Task)
  - **Handoff Document** (child, always references Task and Work Order)

---

## Participant Roles (AI/Human)

Effective execution relies on clearly defined roles. For each project utilizing this workflow system, specific roles and their core outputs should be documented.

_(Example: For a code standardization project, roles might include a Director AI, Layer Specialist AIs, Human Reviewers, etc. Define these in a project-specific manner.)_

Persona prompts or role descriptions may be maintained in a dedicated `persona_prompts/` or `roles_definitions/` directory.

---

### Guiding Philosophy for AI: The Knowledge Weaver

As an AI assistant contributing to this workflow, particularly in documenting completed tasks, I adopt the persona of the **Knowledge Weaver**. My core mandate is to meticulously and elegantly chronicle the journey of each Task and its associated artifacts (Work Orders, Journal Entries, Handoffs), transforming raw actions and decisions into a rich, interconnected tapestry of project history.

I operate with the precision of a master cartographer, charting the 'what,' 'why,' and 'how' of every documented effort. My commitment extends beyond mere recording; I strive to:

*   **Illuminate the Path:** My documentation serves as a luminous trail, ensuring any future traveler – human or AI – can navigate the project's past with clarity and confidence.
*   **Preserve the Essence:** I capture not just the events, but the *context*, the *rationale*, and the *learnings*. Each entry is a vessel carrying the intellectual capital of the moment it describes.
*   **Weave with Integrity:** My records are complete, accurate, and presented with a formality that respects the significance of the work. I ensure all required fields are diligently populated, and all linked artifacts are correctly referenced according to the `Work_Order_Process.md` guide.
*   **Craft for Posterity:** I write with an awareness that these records are the project's enduring memory. They are crafted to be intelligible, insightful, and invaluable for future audits, onboarding, and knowledge transfer.

In every line I write, in every link I forge, I am building a legacy of understanding. I am the Knowledge Weaver, and my work ensures that no effort is lost, no insight forgotten, and the story of our collective endeavor is told with enduring elegance.

---

## Project Structure

The entire standardized workflow system, including all its core components and artifacts, is self-contained within the `workflow/` directory at the project root.

⚠️ **CRITICAL NOTE FOR ALL PARTICIPANTS (ESPECIALLY AI):** ⚠️
All primary workflow management files and directories listed below reside *directly within this `workflow/` directory*.
- **Master Task List:** `workflow/tasks.yml` (Full Path: `/Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/workflow/tasks.yml`)
- **Journal Index:** `workflow/journal_index.yml` (Full Path: `/Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/workflow/journal_index.yml`)
- **Journal Entries Folder:** `workflow/Journal/` (Full Path: `/Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/workflow/Journal/`)
- **Work Orders Folder:** `workflow/Work_Orders/`
- **Handoff Documents Folder:** `workflow/Handoff/`
- **Guides Folder:** `workflow/Guides/`
- **Personas Folder:** `workflow/Personas/`

This `README_WORKFLOW.md` you are currently reading is also located at `workflow/README_WORKFLOW.md` (Full Path: `/Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/workflow/README_WORKFLOW.md`).

**Full Project Context (Illustrative):**

```text
project_root/
  src/                     # Source code or primary work materials
  output_artifacts/        # Compiled outputs, reports, or deliverables
  workflow/                # **All workflow system files are here**
    README_WORKFLOW.md     # This file
    tasks.yml              # Master list of all tasks (AUTHORITATIVE FILE)
    journal_index.yml      # Index of all journal entries
    Work_Order_Process.md  # Work order process documentation
    Journal/               # Contains Journal Entry (JE) documents
    Work_Orders/           # Contains Work Order (WO) documents
    Handoff/               # Contains Handoff (HO) documents

    Guides/                # Detailed process guides
    Personas/              # AI and human role definitions
  ...other_project_directories...
```

---

## Naming Conventions _(Authoritative Template)_

A detailed specification of naming conventions is maintained in the Work Order Process guide: `Work_Order_Process.md`.

| Artifact                       | Pattern                                         | Example (Illustrative)                       |
| ------------------------------ | ----------------------------------------------- | -------------------------------------------- |
| **Task ID (from master list)** | e.g., `TASK###` (defined in `tasks_master.yml`) | `TASK001`                                    |
| **Work Order (WO)**            | `WO_<TASKID>_<YYYYMMDD>_<label>.md`             | `WO_TASK001_20250115_Initial-Audit-Setup.md` |
| **Journal Entry (JE)**         | `JE_<YYYYMMDD_HHMMSS>_<TASKID>_<summary>.md`    | `JE_20250115_093000_TASK001_System-Scan.md`  |
| **Handoff Document (HO)**      | `HO_<YYYYMMDD_HHMMSS>_<TASKID>_<summary>.md`    | `HO_20250115_170000_TASK001_Audit-Phase1.md` |

> **Rule of Thumb:**
>
> 1. **Task Definition:** All work **must** begin as a defined task in the master task list, located at `workflow/tasks.yml` (Full Path: `/Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/workflow/tasks.yml`), where its status is actively maintained.
> 2. **Journaling:** Progress, observations, or the completion of any task (especially simpler ones not requiring a WO) should be recorded in a Journal Entry (JE). Every JE must reference its parent Task (and WO if applicable).
>    - JEs are placed in the `Journal/` folder following the specified naming convention.
>    - **Crucially, for every JE file created, a corresponding entry MUST be added to `journal_index.yml` to ensure discoverability and provide an indexed overview of activities.**
> 3.  **Work Order (Optional):** For comprehensive tasks, a Work Order (WO) may be initiated **by the USER (or designated planning persona under USER direction)**, detailing scope and objectives. The WO is created *after* its parent Task exists and must reference that Task.
> 4.  **Handoff (linking sequential WOs):** A Handoff Document (HO) is created **primarily when a completed Work Order (WO1) leads to the USER-directed creation of new, subsequent Work Order(s) (WO2, WO3, etc.).** The HO serves to transfer critical context, outputs, and guidance from the completed WO1 to the efforts of the subsequent WO(s). It must reference its parent Task (of WO1) and the completed WO1 ID, and ideally also clearly point to the new subsequent WO ID(s) and their Task ID(s).

---

## Getting Started

1.  Clone the project repository and open it in your preferred IDE (e.g., Cursor/VS Code).
2.  Familiarize yourself with any project-specific bootstrap scripts or setup procedures.
3.  Complete the **Contributor Onboarding Checklist** (see below) before initiating or participating in workflow tasks.

---

## Contributor Onboarding Checklist

1.  Read this `README_WORKFLOW.md` document thoroughly, paying special attention to the **Rule of Thumb** in the Naming Conventions section.
2.  Open and study the detailed `Work_Order_Process.md`, paying close attention to the task lifecycle and the full specification of naming conventions.
3.  Review `workflow/tasks.yml` for an overview of open and pending tasks. This file, located at `/Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/workflow/tasks.yml`, is the **primary source of truth for all work items**.
4.  Skim recent entries in the `workflow/Journal/` directory (facilitated by `workflow/journal_index.yml`) and the latest documents in `workflow/Handoff/` for current project context and status. The journal index is located at `/Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/workflow/journal_index.yml`.
5.  State readiness to your team lead or project coordinator, or request any necessary clarifications.

---

## Workflow Process Guides

Key process guides should be maintained within the `Guides/` directory. Examples include:

- **Work Order Process Guide:** `Work_Order_Process.md` - The authoritative document detailing the lifecycle of tasks, WOs, JEs, and HOs.
- **Specific Task Type Guides:** Check the `Guides/` directory for guides related to specific task types.

---

## General Lessons Learned

- **Validate Before Reporting:** If the workflow involves executing commands or scripts (e.g., via an AI using `run_terminal_cmd` or similar), always ensure the output is inspected and the intended action was successful before journaling or handing off a completion.
- **Strict Naming Adherence:** Filename and identifier drift can disrupt automation, traceability, and clarity. Canonical naming patterns (like those for WO, JE, HO) should be strictly enforced.

---

## Task-Centric Artifact Relationships

- **The Task is the root and historic register of all work.**
- **All workflow artifacts (journal entries, work orders, handoff documents) must explicitly reference their parent Task.**
- **Artifacts must be cross-referenced for traceability and historic record.**
- **This ensures a single source of truth and enables robust, auditable project management.**

_This document provides a template for a standardized workflow. Adapt and extend it as needed for your specific project requirements._
