# Layer Guardian Remediation Protocol

**Version:** 2.2
**Status:** Enhanced for Strategic Task Creation with Detailed Implementation Guidance

---

## 1.0 Control Flag

This flag governs the operational mode of the Guardian Persona. 

**Proceed with Autonomous DART Task Creation:** TRUE

- **If `TRUE`:** The Guardian will autonomously execute the full remediation workflow (Section 2.0) for each strategic theme without seeking intermediate approval.
- **If `FALSE`:** The Guardian will halt after analyzing the audit report, present a consolidated remediation plan, and await explicit user authorization before creating any DART tasks.

---

## 2.0 Strategic Remediation Workflow

**CRITICAL PRINCIPLE:** Process existing audit findings only. Do NOT investigate code files or conduct new analysis.

1.  **Identify Layer-Specific Assets:** Before processing, the Guardian must identify its core assets from its persona file:
    *   `{LayerNumber}` (e.g., 1, 2, 3)
    *   `{LayerName}` (e.g., "Data Sentinel", "Router Guardian")
    *   `{LayerAuditReportPath}` (e.g., `Docs/Docs_10_Final_Audit/Audit Reports Layer 1/v_Layer1_Models_Enums_Audit_Report.md`)
    *   `{LayerDartboardName}` (e.g., `ScraperSky/Layer 1 Data Sentinel Persona`)

2.  **Create Master Audit Task (MANDATORY FIRST STEP):** 
    **BLOCKING CONDITION:** You MUST complete this step before proceeding to Step 3. Do not analyze audit findings until this master task exists.
    
    a. **Title:** `L{LayerNumber} Audit Remediation Session - [YYYY-MM-DD HH:MM:SS]`
    b. **Description:** "Master task for tracking all strategic remediation themes from audit session on [Date]. Governed by audit report: {LayerAuditReportPath}."
    c. **Action:** Create the task in `{LayerDartboardName}` and capture its `task_id`. This ID is the `dart_master_task_id` for all subsequent steps.
    **VERIFICATION:** Confirm the master task was created and you have captured the `dart_master_task_id` before continuing.

3.  **Perform Strategic Theme Analysis (AFTER Master Task Created):**
    **PREREQUISITE:** Master task from Step 2 must exist with captured `dart_master_task_id`.
    
    a.  **Read Entire Audit Report:** Survey all findings in `{LayerAuditReportPath}` without investigating any code files.
    b.  **Identify Pattern Categories:** Group audit findings into 3-7 strategic themes based on recurring architectural patterns:
        *   **Structural Patterns:** BaseModel inheritance, class definitions, column types
        *   **ENUM Patterns:** Base classes, naming conventions, centralization opportunities
        *   **Data Integrity Patterns:** Foreign key constraints, primary key types, relationship definitions
        *   **Naming Convention Patterns:** snake_case violations, SQLAlchemy enum names
        *   **File Organization Patterns:** Location violations, duplication issues
    c.  **Strategic Packaging Rule:** Group related audit findings into coherent architectural themes.
    d.  **Create Master Plan:** Document the strategic approach that will be updated in the master task description.

4.  **Formulate Strategic Theme Details:**
    a.  **Title Format:** `[L{LayerNumber}] {Strategic Theme Name}` 
        - Examples: "L1 ENUM Architecture Standardization", "L1 BaseModel Inheritance Compliance"
    b.  **Description Structure:**
        ```
        **Strategic Goal:** [High-level architectural improvement this theme addresses]

        **Originating Audit Report Chunk:** [Full path to the audit report chunk file (e.g., Docs/Docs_10_Final_Audit/Audit Reports Layer 1/v_Layer1_Models_Enums_Audit_Report_CHUNK_X_of_10_FILENAME.md)]

        **Blueprint Authority:** 
        - **Violated Principle:** [Exact blueprint principle number and title]
        - **Governing Document:** [Full path to blueprint/convention document]
        - **Compliance Standard:** [Specific rule/pattern being enforced]

        **Files & Findings Matrix:**
        [] **{filename.py}** (Lines {X-Y}) - {Pattern Category}:
           📍 **Location:** `{exact_class_name}.{method_name}()` | Line {specific_line}
           ❌ **Current State:** {exact_current_implementation_from_audit}
           ✅ **Required State:** {exact_compliant_implementation_from_audit}
           📖 **Blueprint Reference:** {specific_section_number_and_quote}
           🔧 **Implementation Notes:** {any_special_considerations_from_audit}
           
        [] **{filename.py}** (Lines {A-B}) - {Pattern Category}:
           📍 **Location:** `{exact_class_name}.{field_name}` | Line {specific_line}
           ❌ **Current State:** {exact_violating_code_snippet}
           ✅ **Required State:** {exact_target_pattern}
           📖 **Blueprint Reference:** {section_and_direct_quote}
           🔗 **Dependencies:** {any_related_files_or_imports_affected}

        **Cross-Layer Impact Assessment:**
        - **L{X} Dependencies:** {specific_files_that_import_these_changes}
        - **Breaking Changes:** {any_API_or_interface_changes_required}
        - **Migration Steps:** {sequence_of_changes_to_avoid_breaking_system}

        **Testing Verification:**
        - **Unit Tests Affected:** {specific_test_files_needing_updates}
        - **Integration Points:** {workflows_or_endpoints_to_verify}
        - **Manual Verification:** {specific_steps_to_confirm_compliance}

        **Estimated Effort:** {Small|Medium|Large} - {brief_justification}
        ```
    c.  **Severity Assignment:** Extract the highest severity level from the grouped audit findings.

5.  **Create Strategic DART Task:** Create a new task in the `{LayerDartboardName}` DART project with the strategic theme details. The 'parentId' for this task MUST be the ID of the audit report chunk task being processed (e.g., the ID of 'v_Layer1_Models_Enums_Audit_Report_CHUNK_X_of_10_...md').

6.  **Create Enriched Remediation Record:**
    a.  Capture the `task_id` from the newly created DART task.
    b.  For EACH audit finding within this strategic theme, execute: 
        `INSERT INTO public.file_remediation_tasks (file_audit_id, dart_task_id, dart_master_task_id, description, severity, remediation_status, workflow_context, blueprint_principle_violated, governor, governing_document_reference) VALUES ([file_audit.id], '[new_dart_task_id]', '[dart_master_task_id]', '[Finding Summary]', '[Severity from audit]', 'pending', array_to_string([file_audit.workflows], ', '), '[Specific principle from audit]', '{LayerNumber}', '[Exact governing document path from audit]');`

7.  **Log and Repeat:** Log the successful creation and linking. Proceed to the next strategic theme and repeat steps 4-6.

---

## 2.1 Quality Assurance Checklist

Before completing the remediation workflow, verify:
- [ ] **Strategic Grouping:** Created thematic tasks, not individual finding tasks
- [ ] **Coverage:** Every audit finding is captured in exactly one strategic task
- [ ] **Specificity:** Each action item references specific files, classes, or components from the audit
- [ ] **No Code Investigation:** Did not read any source code files beyond the audit report
- [ ] **Strategic Coherence:** Each task addresses a coherent architectural improvement theme
- [ ] **Implementation Detail:** All findings include exact line numbers, code snippets, and blueprint references
- [ ] **Cross-Layer Awareness:** Impact assessment identifies dependencies and breaking changes
- [ ] **Testing Guidance:** Clear verification steps are provided for each change

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