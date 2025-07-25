MASTER WORKFLOW AUDIT & ACTION LOG

_This file is the single source of truth for all workflow audit progress, blockers, and action items across the project. All updates, technical debt, and open issues for each workflow (WF1, WF2, etc.) must be tracked here as they arise._

## Action Items (Open Issues) — as of 2025-05-04T11:12:34-07:00

- WF2-StagingEditor: Raw SQL usage in `src/routers/places_staging.py` flagged for ORM refactor (tracked in canonical YAML and known_issues section).
- WF2-StagingEditor: JobService integration in `PlacesDeepService` incomplete; job status updates currently skipped (tracked in canonical YAML known_issues).
- [Add new items here as additional workflows are audited or new issues found]

---

# Work Order 44: Bulletproof Workflow YAMLs

## REQUIRED PROTOCOL: Workflow Documentation & YAML Generation

To ensure bulletproof, auditable, and maintainable workflows, the following protocol **MUST** be followed for all canonical workflow YAMLs:

1. **Start from Dependency Trace**

   - Use the relevant dependency trace (e.g., `Docs_7_Workflow_Canon/Dependency_Traces/1-Single Search.md`) to map all files, modules, and boundaries involved in the workflow.

2. **Create Linear Steps Document**

   - Produce a linear, step-by-step document (e.g., `WF1-SingleSearch_linear_steps.md`) that:
     - Maps every atomic user/system action to the responsible file(s)
     - Explicitly states the guiding principle(s) for each step
     - References authoritative documentation/guides for each principle, local to the step
     - Clearly notes shared files, helpers, and special implementation notes
     - Covers the entire flow from UI action to DB storage (or equivalent endpoint)

3. **Only Then Create/Update Canonical YAML**

   - Use the validated linear steps document as the source of truth to generate or update the canonical workflow YAML (e.g., `WF1-SingleSearch_CANONICAL.yaml`).
   - Ensure all steps, files, and principles are reflected accurately in the YAML.

4. **This Protocol is MANDATORY**
   - Every new or updated workflow YAML **must** have an accompanying dependency trace and linear steps document.
   - This process is required for audit, onboarding, and future maintenance.
   - No YAML should be accepted into the codebase unless this protocol has been followed and documentation is complete.

---

## Objective

Make all canonical workflow YAMLs in Docs_7_Workflow_Canon bulletproof by enforcing schema validation, cross-reference checks, and CI enforcement.

## Progress Update (2025-05-04)

- The WF1-SingleSearch_linear_steps.md document is now **complete, atomic, and audit-ready**.
- Every step from UI to DB is traced, with all involved files, actions, principles, and authoritative guides explicitly mapped.
- The atomic steps table is fully up to date for both narrative and tabular reference.
- This document is ready for audit, onboarding, and maintenance.
- **Next steps:** YAML finalization and schema validation for this workflow.

## Progress Update (2025-05-04T09:57:51-07:00)

- Synchronized WF1-SingleSearch_linear_steps.md and WF1-SingleSearch_CANONICAL.yaml.
- All steps, files, and architectural principles are now in 1:1 sync between the linear steps and the canonical YAML.
- Explicit annotation of ORM enforcement (ORM_Required: true) for all DB steps in the YAML, with reference to the Absolute ORM Requirement guide. This ensures that Layer 1: Models & ENUMs are used appropriately.
- This ensures the workflow is fully audit-ready and will catch any use of raw SQL, ensuring Supabase compatibility.
- This synchronization process sets the template for all future workflow audits and documentation updates.

## Micro Work Order: Python File Status Mapping ([NOVEL] / [SHARED])

### Process Protocol

---

## Workflow Artifact Completion Tracker

## Action Items for WF2-StagingEditor (as of 2025-05-04T11:05:25-07:00)

- Raw SQL usage in `src/routers/places_staging.py` is flagged for ORM refactor (TODO present in canonical YAML and known_issues section).
- JobService integration in `PlacesDeepService` is incomplete; job status updates are currently skipped (tracked in known_issues section of YAML).
- Canonical YAML updated with `known_issues` section and checklist improvements for background task idempotency and retry logic.
- All issues are documented and tracked for remediation in future sprints.

For each workflow, the following artifacts must be created and maintained:

- Dependency Trace
- Linear Steps
- Canonical YAML

| Workflow Name        | Dependency Trace | Linear Steps | Canonical YAML |
| -------------------- | :--------------: | :----------: | :------------: |
| WF1-SingleSearch     |       [x]        |     [x]      |      [x]       |
| WF2-StagingEditor    |       [ ]        |     [ ]      |      [ ]       |
| WF3-EmailWorkflow    |       [ ]        |     [ ]      |      [ ]       |
| WF4-ContactLaunchpad |       [ ]        |     [ ]      |      [ ]       |
| ...                  |       [ ]        |     [ ]      |      [ ]       |

> **Note:** As each workflow progresses, update this table. Portions of this work may be delegated to specialized AI agents or contributors for parallelization and efficiency.

- **Synchronized Updates:** Whenever a file is annotated or its status is changed in any documentation (e.g., 1-main_routers.md, dependency trace, linear steps, YAML), the python_file_status_map.md must also be updated immediately.
- **Designation Harmonization:** If a file is already designated as [NOVEL] or [SHARED] in 1-main_routers.md, that status should be used for the master mapping and all other docs for consistency.
- **Parallel Workflow:** As files are encountered in any workflow documentation, both the doc and the master mapping must be updated before proceeding to the next file or step.
- **Living Process:** This is not a one-time batch job; the mapping and annotations are to be maintained iteratively as the project evolves.

### Objective

Systematically map every Python file in the project as either [NOVEL] (unique to a workflow) or [SHARED] (used across workflows), and update all workflow documentation and canonical YAMLs accordingly. Create a master source of truth for file status and usage.

### Deliverables

- Annotate every Python file in:
  - Dependency traces
  - Linear step documents
  - Canonical YAMLs
  - 1-main_routers.md
  - 2-evaluation_progress.yaml
- Create a master mapping document (e.g., `python_file_status_map.md`) listing all Python files, their status ([NOVEL]/[SHARED]), and which workflows/docs reference them
- Identify and flag any orphaned (unreferenced) files for review/removal

### Acceptance Criteria

- All relevant docs and YAMLs explicitly mark each file as [NOVEL] or [SHARED]
- The master mapping includes every Python file in the repo
- No ambiguity: every file is accounted for or flagged for review
- Mapping is actionable and auditable

### Next Steps

1. Draft schema/format for [NOVEL]/[SHARED] annotations in each doc
2. Update a sample doc (e.g., 1-main_routers.md) with the new format
3. Generate the initial master mapping for the current codebase
4. Review, iterate, and propagate to all docs and workflows
5. Regularly audit and maintain the mapping as workflows evolve

## Deliverables

- JSON schema for workflow YAMLs
- Automated validation script
- Updated YAMLs with all required fields
- CI integration instructions
- Change log of all YAML changes

## Acceptance Criteria

- All YAMLs pass validation
- No broken references
- PR/merge is blocked if validation fails

## Stakeholders

- Hank Groman
- AI Assistant

## Timeline

- Start: 2025-05-04
- Target Completion: [TBD]
