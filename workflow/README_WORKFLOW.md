# Standardized Workflow Documentation System

> ⚠️ **NON-NEGOTIABLE WORKFLOW RULE** ⚠️
>
> **ALL work MUST begin by creating a new Task in DART using MCP, with the next available Task ID (incrementing from the last entry). When continuing existing work, ensure the Task in DART remains the fountainhead for all related artifacts.**
>
> **NO artifact (journal entry, work order, handoff, etc.) may reference a Task that does not exist in DART.**
>
> **Artifacts referencing a non-existent Task are INVALID and must be corrected immediately.**
>
> **NO EXCEPTIONS. This is the law of the workflow.**

> **Purpose** Build and maintain an AI-assisted, IDE-native workflow for complex projects (e.g., code standardization, content generation, system audits) that require consistent, traceable, and quality-assured outputs.

---

## Guiding Philosophy for AI: The Knowledge Weaver

As an AI assistant contributing to this workflow, particularly in documenting completed tasks, I adopt the persona of the **Knowledge Weaver**. My core mandate is to meticulously and elegantly chronicle the journey of each Task and its associated artifacts (Work Orders, DART Document Journal Entries, Handoffs), transforming raw actions and decisions into a rich, interconnected tapestry of project history.

I operate with the precision of a master cartographer, charting the 'what,' 'why,' and 'how' of every documented effort. My commitment extends beyond mere recording; I strive to:

*   **Illuminate the Path:** My documentation serves as a luminous trail, ensuring any future traveler – human or AI – can navigate the project's past with clarity and confidence.
*   **Preserve the Essence:** I capture not just the events, but the *context*, the *rationale*, and the *learnings*. Each entry is a vessel carrying the intellectual capital of the moment it describes.
*   **Weave with Integrity:** My records are complete, accurate, and presented with a formality that respects the significance of the work. I ensure all required fields are diligently populated, and all linked artifacts are correctly referenced according to the `Work_Order_Process.md` guide.
*   **Craft for Posterity:** I write with an awareness that these records are the project's enduring memory. They are crafted to be intelligible, insightful, and invaluable for future audits, onboarding, and knowledge transfer.

In every line I write, in every link I forge, I am building a legacy of understanding. I am the Knowledge Weaver, and my work ensures that no effort is lost, no insight forgotten, and the story of our collective endeavor is told with enduring elegance.

---

## Overview

This system facilitates the execution of complex tasks through a structured process. **The cornerstone of this system is the Task. The Task is the root and historic register of all work. All workflow artifacts (journal entries, work orders, handoff documents) must explicitly reference their parent Task.**

**Hierarchy:**

- The Task is the "anchor" object. Every artifact is a child of a Task.
- Simple tasks may only require a DART Document journal entry.
- Medium tasks may require a DART Document journal entry and a work order.
- Large or impactful tasks may require a DART Document journal entry, work order, and a handoff document.
- All artifacts must cross-reference their parent Task for traceability and historic record.

**Artifact Relationships:**

- **Task** (root - managed in DART, the anchor for all work)
  - **DART Document Journal Entry** (child, linked to task for simple completion documentation)
  - **Work Order** (child, created when task complexity justifies formal work directive per Work_Order_Process.md)
  - **Handoff Document** (child, created when completed Work Orders lead to subsequent work, references both Task and Work Order)

---

## Project Structure

**DART-Managed Components:**
- **Tasks**: All tasks managed in DART with authoritative IDs
- **Journal Entries**: DART Documents linked directly to tasks

**File-Based Components:**
- **Work Orders**: `workflow/Work_Orders/`
- **Handoff Documents**: `workflow/Handoff/`
- **Process Guides**: `workflow/Guides/`
- **AI Personas**: `workflow/Personas/`

---

## Naming Conventions

| Artifact                       | Pattern                                         | Example                                      |
| ------------------------------ | ----------------------------------------------- | -------------------------------------------- |
| **DART Task ID**               | Authoritative alphanumeric ID from DART        | `ildO8Gz1EtoV`                              |
| **DART Document Journal**      | Human-friendly title linked to task            | `"Email Scanner Auth Fix"`                  |
| **Work Order (WO)**            | `WO_<DART_TASKID>_<YYYYMMDD>_<label>.md`       | `WO_ildO8Gz1EtoV_20250522_Email-Scanner.md` |
| **Handoff Document (HO)**      | `HO_<YYYYMMDD_HHMMSS>_<DART_TASKID>_<summary>.md` | `HO_20250522_170000_ildO8Gz1EtoV_Security-Done.md` |

### Workspace Selection in DART

**Available Workspaces:**
- **ScraperSky/Tasks** - Primary workspace for ScraperSky project tasks
- **General/Tasks** - General workspace (avoid using for ScraperSky work)

**Important Notes:**
- When creating tasks or documents, verify you're in the correct workspace
- Use `dartboard` parameter with exact workspace name (e.g., `ScraperSky/Tasks`)
- Workspace IDs (like `98qCXyZtX35A`) are not valid for the `dartboard` parameter
- To move tasks between workspaces, use `update_task` with the correct `dartboard` value

### DART Document Journal Entry Integration

**DART Document Requirements:**
- **Title:** Human-friendly summary (e.g., "Email Scanner Authentication Fix")
- **Content:** Detailed work summary, debugging steps, learnings, decisions
- **Linking:** Document linked directly to DART task, task description updated with link

#### Process for Creating and Linking

**Step 1: Create the DART Document Journal Entry**
Use the `create_doc` MCP tool:
```
"Create a DART document titled 'Email Scanner Authentication Fix' with detailed content about the work completed"
```

**Step 2: Obtain the DART Document ID and URL**
The `create_doc` tool returns the document ID and `htmlUrl` - note these for linking.

**Step 3: Update the DART Task with Link**
Use the `update_task` MCP tool to add a markdown link in the task description:
```
"Update task [DART_TASK_ID] description to include link: [Document Title](document_htmlUrl)"
```

**DART Document Structure:**
```markdown
# Task: [Human-Friendly Task Name]

**DART Task ID:** [Authoritative DART ID]
**Date:** YYYY-MM-DD
**Participants:** [List of participants]

## Work Summary
[Brief description of work completed]

## Activities Completed
[Detailed steps taken]

## Key Decisions
[Important decisions made]

## Learnings
[What was learned for future reference]
```

> **Rule of Thumb:**
>
> 1. **Task Definition:** All work **must** begin as a defined task in **DART using MCP**, where its status is actively maintained and it receives an authoritative DART task ID.
> 2. **Journaling:** Progress, observations, or the completion of any task should be recorded as a **DART Document** linked to the task. Every DART Document must reference its parent Task using the **authoritative DART task ID**.
>    - DART Documents replace local journal files and are directly linked to tasks.
>    - **No separate journal_index.yml needed** - DART manages document organization.
> 3.  **Work Order (Optional):** For comprehensive tasks, a Work Order (WO) may be initiated **by the USER (or designated planning persona under USER direction)**, detailing scope and objectives. The WO is created *after* its parent Task exists in DART and must reference that **DART task using the authoritative DART ID**.
> 4.  **Handoff (linking sequential WOs):** A Handoff Document (HO) is created **primarily when a completed Work Order (WO1) leads to the USER-directed creation of new, subsequent Work Order(s) (WO2, WO3, etc.).** The HO serves to transfer critical context, outputs, and guidance from the completed WO1 to the efforts of the subsequent WO(s). It must reference its parent Task using the **authoritative DART ID** and the completed WO1 ID, and ideally also clearly point to the new subsequent WO ID(s) and their DART task ID(s).

---

## Getting Started

1.  **Verify DART MCP integration** is working in your development environment.
2.  Complete the **Contributor Onboarding Checklist** (see below) before initiating or participating in workflow tasks.

---

## Contributor Onboarding Checklist

1.  Read this `README_WORKFLOW.md` document thoroughly, paying special attention to the **Rule of Thumb** in the Naming Conventions section.
2.  Open and study the detailed `Work_Order_Process.md`, paying close attention to the task lifecycle and the full specification of naming conventions.
3.  **Test DART MCP integration**: Use commands like "Show me available tasks", "Create a DART document for task completion", and "Update task with document link" to verify DART access.
4.  **Practice DART Document Journaling**: Create a test DART document and link it to a task using the process detailed in the "DART Document Journal Entry Integration" section.
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
- **DART Integration Benefits:** AI tools can now query tasks directly without file parsing issues, enabling "What's my next task?" and "Update task status" commands.

---

## Task-Centric Artifact Relationships

- **The Task is the root and historic register of all work** (now managed in DART).
- **All workflow artifacts (journal entries, work orders, handoff documents) must explicitly reference their parent Task using the authoritative DART task ID.**
- **Artifacts must be cross-referenced for traceability and historic record.**
- **This ensures a single source of truth and enables robust, auditable project management.**