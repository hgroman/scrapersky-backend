# Micro Work Order: WF3 Local Business Curation

(Created: 2025-05-04T11:39:35-07:00)
(Completed: 2025-05-05T00:15:10-07:00)

---

<!--
This file is a copy of MICRO_WORK_ORDER_TEMPLATE.md, customized for the WF3 Local Business Curation workflow.
All audit steps, checklist items, and documentation standards apply.
-->

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
  - Dependency Trace: `Docs_7_Workflow_Canon/Dependency_Traces/3-Local Business Curation.md`
  - Linear Steps: `Docs_5_Project_Working_Docs/44-Bulletproof-Workflow-YAMLs/WF3-LocalBusinessCuration_linear_steps.md`
  - Canonical YAML: `Docs_7_Workflow_Canon/workflows/WF3-LocalBusinessCuration_CANONICAL.yaml`

### 2. Dependency Trace Audit
- [x] Open: `Docs_7_Workflow_Canon/Dependency_Traces/3-Local Business Curation.md`
- [x] Confirm all files, functions, and components are listed and described (UI, routers, services, models, background jobs, etc.)
- [x] Annotate each referenced file as [NOVEL] or [SHARED] (see python_file_status_map.md for authoritative status)
- [x] Ensure the dependency trace covers the workflow from UI to DB and background jobs
- [x] If any files are missing, update the dependency trace to match the template structure

### 3. Create or Update Linear Steps Document
- [x] If not present, create: `Docs_5_Project_Working_Docs/44-Bulletproof-Workflow-YAMLs/WF3-LocalBusinessCuration_linear_steps.md` using the WF1 linear steps doc as a template
- [x] Map each step in the workflow from UI to DB, referencing all files and actions
- [x] Annotate each file as [NOVEL] or [SHARED]
- [x] Reference all architectural principles and guides as in WF1
- [x] Ensure the atomic steps table is up to date and complete

### 4. Canonical YAML Audit
- [x] Open: `Docs_7_Workflow_Canon/workflows/WF3-LocalBusinessCuration_CANONICAL.yaml`
- [x] Ensure all steps, files, and principles are in 1:1 sync with the linear steps doc
- [x] Verify producer-consumer relationship documentation in the workflow_connections section
- [x] Explicitly annotate ORM enforcement and architectural mandates for all DB steps
- [x] Reference all relevant architectural guides
- [x] Validate the YAML against the established schema (see CI enforcement work order)
- [x] Checklist for background task compliance:
    - [x] Idempotency
    - [x] Retry Logic
    - [x] Explicit transaction boundaries
    - [x] Logging and error handling

### 5. Producer-Consumer Pattern Verification
- [x] Verify that WF3 follows the producer-consumer pattern documented in PRODUCER_CONSUMER_WORKFLOW_PATTERN.md
- [x] Validate that WF3 acts as a producer for WF4-DomainCuration
  - Production signal: Setting domain_extraction_status = "Queued" in local_businesses table
  - Connection point: src/routers/local_businesses.py::update_local_businesses_status_batch → src/services/sitemap_scheduler.py::process_pending_jobs
- [x] Validate that WF3 acts as a consumer of WF2-StagingEditor
  - Consumption signal: Reading place records with status = "Selected"
  - Connection point: src/routers/places_staging.py::update_places_status_batch → src/routers/local_businesses.py::get_local_businesses
- [x] Ensure connection points are explicitly documented in both canonical YAML and dependency trace

### 6. Cross-Reference and Sync
- [x] Confirm all files and principles are mirrored across dependency trace, linear steps, and YAML
- [x] Ensure there are no orphaned or ambiguous files
- [x] Update `Docs_7_Workflow_Canon/python_file_status_map.md` with any new or changed files, annotating [NOVEL]/[SHARED] as appropriate

### 6. Artifact Tracker and Progress Log
- [x] Mark artifact completion for this workflow in `WORK_ORDER.md`
- [x] Add a timestamped progress entry summarizing the audit in `WORK_ORDER.md`

### 7. Signoff
- [x] All steps above are checked/completed, or exceptions are documented
- [x] Reviewer signs and dates the micro work order

---

## Known Issues / Exception Log (as of 2025-05-05T00:15:30-07:00)

### 1. No eligibility check before queueing domain extraction (MEDIUM)
- **Description**: Currently, all local businesses with status="Selected" are automatically queued for domain extraction, regardless of whether they have a valid website_url. This could lead to unnecessary processing and errors.
- **Remediation Plan**: 
  1. Add preliminary validation in the router to check if website_url exists
  2. Only queue items with a non-empty website_url
  3. Add appropriate error message for items without website URLs
- **JIRA Ticket**: SCRSKY-230
- **Target Date**: 2025-05-20

### 2. Naming confusion in sitemap_scheduler.py (LOW)
- **Description**: Despite being named "sitemap_scheduler.py", this file handles multiple types of background processing, including domain extraction. This naming can be confusing for new developers.
- **Remediation Plan**:
  1. Consider renaming to "background_scheduler.py" or similar
  2. Alternatively, split into domain-specific schedulers
  3. Update documentation to clarify multi-purpose nature
- **JIRA Ticket**: SCRSKY-231
- **Target Date**: 2025-05-30

### 3. Architectural Pattern Observation: Dual-Status Update Pattern
- **Description**: This workflow uses the same Dual-Status Update pattern identified in WF2 (where setting a primary status field automatically triggers an update to a secondary status field for background processing). This appears to be a standardized pattern in the codebase.
- **Recommendation**: Consider formalizing this pattern in the architectural guides or creating a helper function to standardize implementation across different routers.

---

## DB/ORM Audit Findings (2025-05-05T00:16:00-07:00)

| File                               | ORM Only | Raw SQL Present | Notes                |
|-------------------------------------|----------|-----------------|----------------------|
| src/routers/local_businesses.py     | ✅        | ❌              | Router compliant     |
| src/services/business_to_domain_service.py | ✅        | ❌              | Service compliant    |
| src/services/sitemap_scheduler.py   | ✅        | ❌              | Scheduler compliant  |
| src/models/local_business.py        | ✅        | ❌              | Models only          |
| src/models/domain.py                | ✅        | ❌              | Models only          |

- **Finding**: Unlike WF2, all database operations in this workflow use SQLAlchemy ORM properly. No raw SQL was detected in any of the files.
- **Pattern**: This workflow uses the same "Dual-Status Update" pattern as WF2 but with proper ORM implementation.
- **Issues**: The main issues identified are related to business logic (lack of eligibility checks) and naming consistency (sitemap_scheduler.py handling multiple types of jobs), not ORM compliance.
- **Next**: Add automated test to verify that only local businesses with valid website_url are queued for domain extraction.
- **Timestamp**: 2025-05-05T00:16:00-07:00

## Notes for Future Auditors
- **No context is assumed**—all instructions are explicit and reference authoritative templates and mapping files
- The Dual-Status Update pattern is a key architectural pattern that appears in both WF2 and WF3 workflows
- Unlike WF2, this workflow is fully ORM-compliant with no raw SQL present
- Reference the CI Enforcement Work Order for schema validation and automated checks
- If any ambiguity arises, update this micro work order and the cheat sheet for future clarity
- **Reminder:** All timestamps must use ISO8601 format with timezone for audit traceability.

---

**Reviewer:** Cascade AI  
**Date:** 2025-05-05T00:17:00-07:00
