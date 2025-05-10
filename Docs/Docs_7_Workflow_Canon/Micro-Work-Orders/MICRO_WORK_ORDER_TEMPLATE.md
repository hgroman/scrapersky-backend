# Micro Work Order Template: Workflow Audit

_Last updated: 2025-05-04T10:22:01-07:00_

## Objective

To perform a bulletproof, fully auditable documentation and artifact audit for a workflow, using Workflow 1 as the template and ensuring all steps are explicit, repeatable, and context-free for any future AI or human auditor.

---

## Step-by-Step Protocol

### 1. Reference Templates

- Use this template for every workflow audit.
- Reference completed examples for structure and rigor.
- All timestamps must use ISO8601 format with timezone for audit traceability.
- If any checklist item is not completed, a documented exception must be added to the Known Issues / Exception Log.
- If new best practices or ambiguities are discovered during any workflow audit, update this template and the cheat sheet immediately for future clarity.
- All issues, technical debt, and exceptions must be referenced in both the micro work order and the master WORK_ORDER.md audit log for traceability.
  - Dependency Trace: `Docs_7_Workflow_Canon/Dependency_Traces/1-SingleSearch.md`
  - Linear Steps: `Docs_5_Project_Working_Docs/44-Bulletproof-Workflow-YAMLs/WF1-SingleSearch_linear_steps.md`
  - Canonical YAML: `Docs_7_Workflow_Canon/workflows/WF1-SingleSearch_CANONICAL.yaml`

### 2. Dependency Trace Audit

- [ ] Open: `Docs_7_Workflow_Canon/Dependency_Traces/{WORKFLOW_DEPENDENCY_TRACE}`
- [ ] Confirm all files, functions, and components are listed and described (Layer 6: UI Components, Layer 3: Routers, Layer 4: Services, Layer 1: Models & ENUMs, background jobs, etc.)
- [ ] Annotate each referenced file as [NOVEL] or [SHARED] (see 3-python_file_status_map.md for authoritative status)
- [ ] Ensure the dependency trace covers the workflow from UI to DB and background jobs
- [ ] If any files are missing, update the dependency trace to match the template structure

### 3. Create or Update Linear Steps Document

- [ ] If not present, create: `Docs_5_Project_Working_Docs/44-Bulletproof-Workflow-YAMLs/{WORKFLOW_LINEAR_STEPS}` using the WF1 linear steps doc as a template
- [ ] Map each step in the workflow from UI to DB, referencing all files and actions
- [ ] Annotate each file as [NOVEL] or [SHARED]
- [ ] Reference all architectural principles and guides as in WF1
- [ ] Ensure the atomic steps table is up to date and complete

### 4. Canonical YAML Audit

- [ ] Open: `Docs_7_Workflow_Canon/workflows/{WORKFLOW_CANONICAL_YAML}`
- [ ] Ensure all steps, files, and principles are in 1:1 sync with the linear steps doc
- [ ] Explicitly annotate ORM enforcement and architectural mandates for all DB steps
- [ ] Reference all relevant architectural guides
- [ ] Validate the YAML against the established schema (see CI enforcement work order)
- [ ] Checklist for background task compliance:
  - [ ] Idempotency
  - [ ] Retry Logic
  - [ ] Explicit transaction boundaries
  - [ ] Logging and error handling

### 5. Cross-Reference and Sync

- [ ] Confirm all files and principles are mirrored across dependency trace, linear steps, and YAML
- [ ] Ensure there are no orphaned or ambiguous files
- [ ] Update `Docs_7_Workflow_Canon/3-python_file_status_map.md` with any new or changed files, annotating [NOVEL]/[SHARED] as appropriate

### 6. Artifact Tracker and Progress Log

- [ ] Mark artifact completion for this workflow in `WORK_ORDER.md`
- [ ] Add a timestamped progress entry summarizing the audit in `WORK_ORDER.md`

### 7. Signoff

- [ ] All steps above are checked/completed, or exceptions are documented
- [ ] Reviewer signs and dates the micro work order

---

## Known Issues / Exception Log (as of 2025-05-04T11:21:49-07:00)

- [ ] Document any technical debt, non-blocking issues, or TODOs discovered during the audit here.
- [ ] Reference corresponding TODOs in canonical YAML or other artifacts.

---

## Notes for Future Auditors

- **No context is assumed**—all instructions are explicit and reference authoritative templates and mapping files
- Reference the CI Enforcement Work Order for schema validation and automated checks
- If any ambiguity arises, update this micro work order and the cheat sheet for future clarity
- **Reminder:** All timestamps must use ISO8601 format with timezone for audit traceability.

---

**Reviewer:** ********\_\_\_\_********
**Date:** **********\_\_\_\_**********
