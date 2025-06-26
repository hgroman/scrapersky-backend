# ScraperSky Workflow Canon: Single Source of Truth

> **START HERE:**
>
> **Every new auditor, developer, or AI must begin by reading [`Template Resources/CONTEXT_GUIDE.md`](./Template%20Resources/CONTEXT_GUIDE.md).**
>
> This document is the master onboarding, protocol, and context guide for all workflow documentation and audit activities. It explains the philosophy, process, and non-negotiable requirements for ScraperSky workflows.

**If you are reading this, you are in the one and only authoritative directory for all ScraperSky workflow documentation, audit artifacts, templates, and onboarding resources. All master templates, logs, and cheat sheets have been consolidated here. This is the single source of truth for all audit and workflow efforts—no other directory is canonical.**

## Canonical Artifacts (Root)

- **WORK_ORDER.md**: The master workflow action log and audit tracker for all workflows.
- **MICRO_WORK_ORDER_TEMPLATE.md**: The living, rigorous template for all micro work orders and workflow audits.
- **audit_cheat_sheet.md**: Quick reference for audit best practices and checklist items.
- **python_file_status_map.md**: Authoritative mapping of all Python files and their audit status ([NOVEL]/[SHARED]).
- **validation_schema.json**: Schema for validating canonical YAMLs and workflow docs.
- **Blueprint-Standard-Curation-Workflow.md**: The gold-standard template for new workflow YAMLs.
- **WF-Sitemap-Import_CANONICAL.yaml**: Canonical YAML for the Sitemap Import workflow (formerly called 'Deep Scrape').
- **1-main_routers.md**: Central mapping of all router entry points.
- **2-evaluation_progress.yaml**: Tracks evaluation status and audit trail for all workflow-relevant files.

## Archive

- See `Archive/_archive_index.yaml` for a browsable, annotated index of all archived docs, failed attempts, and historical references.
- Archive subfolders:
  - `Fall_Starts/` — Incomplete, failed, or superseded attempts
  - `Obsolete/` — Docs no longer relevant due to code/architecture changes

---

## Required Elements for Key Documents

The following section outlines the mandatory elements for each key document type in the workflow canon. All workflow documentation MUST contain these elements to maintain consistency and ensure comprehensive coverage of the system.

### Canonical YAML Files
- **Workflow Name and Description**: Clear, concise name and purpose statement
- **Workflow Phases**: All major stages of the workflow with their steps
- **Dependencies**: Required services, models, and other components. **MUST include full file paths, table names for models, and values for enums**
- **Status Transitions**: All possible state transitions with triggers
- **API Endpoints**: All routes with their methods and parameters
- **Background Services**: Any background processes with their schedules
- **Workflow Connections**: Producer-consumer relationships with other workflows, **MUST explicitly specify database table names, fields, and operations**
- **Actionable TODOs**: Prioritized improvements with ticket references
- **Known Issues**: Documented technical debt and limitations

### Dependency Trace Documents
- **NOVEL/SHARED File Annotations**: Mark whether files are unique to workflow
- **Complete File Paths**: Absolute paths to all involved files
- **Service Communication Points**: API calls between services
- **Database Interactions**: All database operations
- **Event Triggers**: Status changes that initiate new processes
- **External API Calls**: Calls to third-party services
- **Producer-Consumer Links**: Connections with other workflows

### Linear Steps Documents
- **Step-by-Step Flow**: Chronological sequence of operations
- **Input/Output**: Data transformations at each step
- **Decision Points**: Conditional branches and their criteria
- **Error Handling**: How exceptions are managed
- **User Interactions**: Points where users provide input or receive feedback
- **API Calls**: All backend API requests with payloads
- **Status Updates**: All status changes in database entities

### Micro Work Orders
- **Objective**: Clear purpose of the audit or implementation
- **Protocol Steps**: Detailed procedure to follow
- **Verification Checklist**: Points to verify during implementation
- **Dependencies**: Related workflows and components
- **Success Criteria**: Definition of completion
- **References**: Links to relevant documentation

### WORKFLOW_AUDIT_JOURNAL.md
- **Date and Auditor**: Who performed the audit and when
- **Workflow Identifier**: Which workflow was audited
- **Key Findings**: Major discoveries and insights
- **Technical Debt**: Identified issues with solutions
- **Architectural Violations**: Deviations from standards
- **Action Items**: Required changes with assignees
- **References**: Links to related tickets and documents

### 3-python_file_status_map.md
- **File Path**: Absolute path to the Python file
- **Status**: NOVEL (unique to one workflow), SHARED (used by multiple), or ORPHANED
- **Workflows**: List of all workflows using the file
- **Purpose**: Brief description of the file's function
- **Dependencies**: Key imports and relationships
- **Last Verified**: Date of last verification

## ScraperSky Audit Toolkit: Master Reference & Workflow

> For the full toolkit and onboarding protocol, see [AUDIT_TOOLKIT.md](./AUDIT_TOOLKIT.md).

If you are reading this, you are about to engage in the most crucial process of the ScraperSky system: establishing, verifying, and evolving the truth documents that define the project’s capabilities and compliance. The following are your essential tools and supporting documents. Every step, artifact, and protocol is mandatory.

### 1. Master Context & Protocol
**CONTEXT_GUIDE.md**
- The authoritative guide for all workflow audits. Read this first. It covers the rationale, step-by-step process, compliance requirements, artifact synchronization, exception handling, and continuous improvement mandate.

### 2. Audit Cheat Sheet
**0 audit_cheat_sheet.md**
- A rapid-reference for best practices, common pitfalls, and checklist items. Use this as a quick guide during any audit or documentation effort.

### 3. Template Artifacts: The “Golden Path” for a Workflow Audit
These three files, using WF2 as an example, show the required artifacts and the order in which to create them for any workflow:

- **1 WF2-Staging Editor Dependency Trace.md**
  - The starting point. Maps all files, modules, and boundaries for the workflow.
  - Purpose: Ensures nothing is missed and every dependency is explicit.
- **2 WF2-StagingEditor_linear_steps.md**
  - The step-by-step mapping of every atomic action, file, and architectural principle for the workflow.
  - Purpose: Establishes the full logic, compliance, and flow before YAML or code changes.
- **3 WF2-StagingEditor_CANONICAL.yaml**
  - The canonical YAML that encodes the workflow for automation, audit, and CI enforcement.
  - Purpose: This is the final, machine- and human-readable truth artifact for the workflow.

### 4. How to Use These Tools (Order Matters!)
- Read CONTEXT_GUIDE.md fully.
  - Understand the philosophy, process, and non-negotiable requirements.
- Reference the audit_cheat_sheet.md for quick reminders as you proceed.
- For each workflow:
  1. Start with a Dependency Trace (see WF2 example).
  2. Build the Linear Steps doc (see WF2 example).
  3. Only then, create/update the Canonical YAML (see WF2 example).
- Cross-reference all findings, issues, and exceptions in both the micro work order and the master WORK_ORDER.md.
- Synchronize all artifacts before marking an audit complete.

### 5. Key Principles
- Every supporting document is authoritative and must be kept up to date.
- No artifact lags behind; all changes must be reflected across all relevant docs.
- All exceptions, technical debt, and issues must be logged and timestamped.
- Manual review is required for any code removal or major change.

---

**Summary:**
This toolkit, and the order in which you use it, is your roadmap for conducting bulletproof, auditable workflow documentation and audits in ScraperSky.
If you are unsure at any step, consult the CONTEXT_GUIDE.md and the latest micro work order template.

  - `Reference/` — Still-informative, non-canonical, or historical docs
  - `VALIDATION-Workflow-Results/` — All validation results
  - `AUDIT-Summary-Docs/` — Audit-specific docs
  - `TRACE-Workflow-Historical/` — Historical workflow traces

## How to Use
- Start with `Workflow-Map_CANONICAL.md` to understand the high-level architecture.
- Use `Workflow-Evaluation-Progress.yaml` to track workflow coverage and audit progress.
- Reference blueprints and canonical workflow YAMLs for new development.
- Consult the archive index for any historical or superseded documentation.

---

_Last updated: 2025-05-04_
