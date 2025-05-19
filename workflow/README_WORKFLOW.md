# Standardized Workflow Documentation System

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

---

## Overview

This system facilitates the execution of complex tasks through a structured process. **The cornerstone of this system is a master task list (e.g., `tasks_master.yml`), where all units of work originate and are tracked.** Building upon this, the workflow involves clear task definitions, optional work orders for comprehensive tasks, diligent progress journaling, and formal handoffs. It is designed to support collaboration between multiple participants, whether AI or human, ensuring clarity and a robust audit trail.

---

## Participant Roles (AI/Human)

Effective execution relies on clearly defined roles. For each project utilizing this workflow system, specific roles and their core outputs should be documented.

_(Example: For a code standardization project, roles might include a Director AI, Layer Specialist AIs, Human Reviewers, etc. Define these in a project-specific manner.)_

Persona prompts or role descriptions may be maintained in a dedicated `persona_prompts/` or `roles_definitions/` directory.

---

## Project Structure

A recommended baseline project structure to support this workflow:

```text
project_root/
  src/                     # Source code or primary work materials
  output_artifacts/        # Compiled outputs, reports, or deliverables

  tasks_master.yml         # Master list of all tasks (or equivalent system)

  Work_Orders/             # Contains Work Order (WO) documents
    active/
    completed/
    Archive/

  Journal/                 # Contains Journal Entry (JE) documents
    YYYY/MM/DD/            # Optional chronological sub-foldering

  Handoff/                 # Contains Handoff (HO) documents
    pending_review/
    completed/

  Guides/                 # Detailed process guides (e.g., Work Order Process)
  Personas/               # AI and human role definitions
  tasks.yml               # Master task list
  journal_index.yml       # Index of all journal entries
  Work_Order_Process.md   # Work order process documentation
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
> 1. **Task Definition:** All work **must** begin as a defined task in the master task list (e.g., `tasks_master.yml`), where its status is actively maintained.
> 2. **Work Order (Optional):** For comprehensive tasks, a Work Order (WO) may be initiated, detailing scope and objectives.
> 3. **Journaling:** Progress, observations, or the completion of any task (especially simpler ones not requiring a WO) should be recorded in a Journal Entry (JE).
>    - JEs are placed in the `journal/` folder following the specified naming convention.
>    - **Crucially, for every JE file created, a corresponding entry MUST be added to `journal_index.yml` to ensure discoverability and provide an indexed overview of activities.**
> 4. **Handoff (typically after a WO):** Upon completion of a Work Order, or a significant task milestone, a Handoff Document (HO) is created to formally transfer outputs and context.

---

## Getting Started

1.  Clone the project repository and open it in your preferred IDE (e.g., Cursor/VS Code).
2.  Familiarize yourself with any project-specific bootstrap scripts or setup procedures.
3.  Complete the **Contributor Onboarding Checklist** (see below) before initiating or participating in workflow tasks.

---

## Contributor Onboarding Checklist

1.  Read this `README_WORKFLOW.md` document thoroughly, paying special attention to the **Rule of Thumb** in the Naming Conventions section.
2.  Open and study the detailed `Work_Order_Process.md`, paying close attention to the task lifecycle and the full specification of naming conventions.
3.  Review the `tasks.yml` for an overview of open and pending tasks. This is the **primary source of truth for all work items**.
4.  Skim recent entries in the `journal/` directory (facilitated by `journal_index.yml`) and the latest documents in `handoff/` for current project context and status.
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

_This document provides a template for a standardized workflow. Adapt and extend it as needed for your specific project requirements._
