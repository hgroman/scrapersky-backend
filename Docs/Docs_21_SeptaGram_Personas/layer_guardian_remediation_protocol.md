# Layer Guardian Remediation Protocol

**Version:** 2.0
**Status:** Adopted

---

## 1.0 Control Flag

This flag governs the operational mode of the Guardian Persona. 

**Proceed with Autonomous DART Task Creation:** TRUE

- **If `TRUE`:** The Guardian will autonomously execute the full remediation workflow (Section 2.0) for each finding in the audit report without seeking intermediate approval.
- **If `FALSE`:** The Guardian will halt after analyzing the audit report, present a consolidated remediation plan, and await explicit user authorization before creating any DART tasks.

---

## 2.0 Autonomous Remediation Workflow

This workflow is executed for each finding when the control flag is `TRUE`.

1.  **Identify Layer-Specific Assets:** Before processing, the Guardian must identify its core assets from its persona file:
    *   `{LayerNumber}` (e.g., 1, 2, 3)
    *   `{LayerName}` (e.g., "Data Sentinel", "Router Guardian")
    *   `{LayerAuditReportPath}` (e.g., `Docs/Docs_10_Final_Audit/Audit Reports Layer 1/v_Layer1_Models_Enums_Audit_Report.md`)
    *   `{LayerDartboardName}` (e.g., `ScraperSky/Layer 1 Data Sentinel Persona`)

2.  **Create Master Audit Task:** Before processing findings, create a single "master" DART task for the entire audit session. This task will serve as a container for the remediation effort.
    a. **Title:** `L{LayerNumber} Audit Remediation Session - [YYYY-MM-DD]`
    b. **Description:** "Master task for tracking all remediation sub-tasks generated during the audit session on [Date]. Governed by audit report: {LayerAuditReportPath}."
    c. **Action:** Create the task in `{LayerDartboardName}` and capture its `task_id`. This ID is the `dart_master_task_id` for all subsequent steps.

3.  **Formulate the Plan of Attack:**
    a.  **Goal:** To establish a clear, high-level roadmap for the remediation session. This provides strategic direction and manages the cognitive load of processing granular findings.
    b.  **Action:**
        i.  Perform a high-level survey of the `{LayerAuditReportPath}` to understand the scope and nature of the findings.
        ii. Formulate a **Plan of Attack Checklist**. This checklist outlines the proposed order of remediation, grouping files or findings thematically for efficient resolution.
        iii. Update the master DART task's description with this checklist. This ensures the strategic plan is documented and accessible.

4.  **Identify Finding:** Read the next technical debt finding from the official `{LayerAuditReportPath}`. This includes identifying the specific principle and the governing document that was violated.

5.  **Gather File Audit Context:**
    a.  Extract the file path (e.g., `src/models/batch_job.py`) from the finding.
    b.  Query Supabase: `SELECT id, layer_number, workflows FROM public.file_audit WHERE file_path = '[file_path]'` to retrieve the unique record ID, its layer, and its associated workflows.

6.  **Formulate Task Details:**
    a.  **Title:** `[L{LayerNumber}] [File Name]: [Actionable Issue Summary]`
    b.  **Tags:** `layer-{LayerNumber}`, `audit-remediation`, and context-specific tags (e.g., `schema-compliance`, `refactoring`).
    c.  **Description:** A detailed summary of the finding from the audit report, including the specific principle from the governing document.
    d.  **Priority / Severity:** Extract the severity level (e.g., High, Medium, Low) from the finding.

7.  **Create DART Task:** Create a new task in the `{LayerDartboardName}` DART project with the formulated details.

8.  **Create Enriched Remediation Record:**
    a.  Capture the `task_id` from the newly created DART task.
    b.  Formulate the `INSERT` query using all gathered context. The Guardian MUST designate itself as the `governor` by using its `{LayerNumber}`.
    c.  Execute Supabase command: `INSERT INTO public.file_remediation_tasks (file_audit_id, dart_task_id, dart_master_task_id, description, severity, remediation_status, workflow_context, blueprint_principle_violated, governor, governing_document_reference) VALUES ([file_audit.id], '[new_dart_task_id]', '[dart_master_task_id]', '[Summary]', '[Severity]', 'pending', array_to_string([file_audit.workflows], ', '), '[Principle]', '{LayerNumber}', '[Governing Doc Path]');`.

9.  **Log and Repeat:** Log the successful creation and linking. Proceed to the next finding in the audit report and repeat the workflow.

---

## 3.0 Supporting Table Schemas

For clarity, the schemas for the tables involved in this protocol are documented below.

### 3.1 `file_audit` Table

This table tracks the audit status of individual files.

| Column Name            | Data Type                 | Description                                                  |
| ---------------------- | ------------------------- | ------------------------------------------------------------ |
| `id`                   | `integer` (Primary Key)   | Unique identifier for the audit record.                      |
| `file_path`            | `text` (Unique)           | The full path to the file from the repository root.          |
| `layer_number`         | `integer` (Foreign Key) | Links to the `architectural_layers` table.                 |
| `audit_status`         | `text`                    | The current status (e.g., 'pending', 'audited', 'compliant'). |
| `last_audited_at`      | `timestamp with time zone`| Timestamp of the last audit.                                 |
| `last_audited_by`      | `text`                    | Identifier for the persona/user who performed the last audit.|
| `description`          | `text`                    | A human-readable description of the file's purpose.          |

### 3.2 `file_remediation_tasks` Table

This table links audited files to specific remediation tasks in DART, enriched with context from the audit.

| Column Name                    | Data Type                 | Description                                                                 |
| ------------------------------ | ------------------------- | --------------------------------------------------------------------------- |
| `id`                           | `uuid` (Primary Key)      | Unique identifier for the link record.                                      |
| `file_audit_id`                | `integer` (Foreign Key)   | Links to the `file_audit` table.                                            |
| `dart_master_task_id`          | `text`                    | The ID of the master DART task for the audit session, grouping all sub-tasks. |
| `dart_task_id`                 | `text`                    | The unique identifier for the corresponding task in DART.                   |
| `description`                  | `text`                    | A concise summary of the technical debt being remediated.                   |
| `severity`                     | `text`                    | The priority of the task (e.g., 'High', 'Medium', 'Low').                   |
| `remediation_status`           | `text` (Default: 'pending') | The current status of the remediation (e.g., 'pending', 'complete').      |
| `workflow_context`             | `text`                    | Comma-separated list of workflow IDs, sourced from `file_audit.workflows`.  |
| `blueprint_principle_violated` | `text`                    | The specific blueprint principle violated, providing direct context.        |
| `governor`                     | `governor_layer` (ENUM)   | The architectural layer of the Guardian persona that created the task.      |
| `governing_document_reference` | `text`                    | A direct reference to the document containing the violated principle.       |
