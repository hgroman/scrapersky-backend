# ScraperSky Workflow Audit: Unified Context, Protocol, and Toolkit Guide

_Last updated: 2025-05-04T13:18:54-07:00_

**If you are reading this, you are about to engage in the most crucial process of the ScraperSky system: the creation, verification, and evolution of truth documents. This guide governs how we capture, audit, and maintain the real capabilities, compliance, and power of all ScraperSky workflows. Every protocol, supporting tool, and artifact referenced here is authoritative and mandatory.**

## Table of Contents
1. [Purpose & Scope](#purpose--scope)
2. [How to Use This Directory](#how-to-use-this-directory)
3. [Master Audit Protocol & Workflow](#master-audit-protocol--workflow)
4. [Key Compliance Requirements](#key-compliance-requirements)
5. [Best Practices & Documentation Guidance](#best-practices--documentation-guidance)
6. [Key Templates & Artifacts](#key-templates--artifacts)
7. [Quick Links](#quick-links)
8. [Ambiguity & Exception Protocol](#ambiguity--exception-protocol)
9. [Summary](#summary)

---

## Purpose & Scope
- **Centralize all onboarding, rationale, protocol, and compliance mandates for workflow audits.**
- **Provide ready-to-copy templates, best practices, and artifact structure/order for bulletproof, auditable documentation.**
- **Eliminate ambiguity, accelerate onboarding, and ensure all audits are traceable, consistent, and aligned with architectural mandates.**
- **This is the ONLY document you need to read to onboard or conduct a workflow audit.**

---

## How to Use This Directory
1. **Start Here:**
   - Review this guide fully before beginning any new workflow audit.
2. **Follow the Protocol:**
   - For every new workflow, follow the step-by-step process and artifact order below.
3. **Adapt the Templates:**
   - Copy and adapt the example files for your workflow, following the order and requirements in this guide.
   - Always cross-reference:
     - [../1-main_routers.md](../1-main_routers.md) — master router map
     - [../2-evaluation_progress.yaml](../2-evaluation_progress.yaml) — audit/evaluation tracker
     - [../3-python_file_status_map.md](../3-python_file_status_map.md) — Python file audit status
4. **Synchronize All Artifacts:**
   - No artifact may lag behind; all changes must be reflected across all relevant docs before marking an audit complete.
5. **Log All Exceptions:**
   - All exceptions, technical debt, and issues must be logged and timestamped in both the micro work order and the master log.

---

## Master Audit Protocol & Workflow

### 1. Master Context & Protocol
- This guide is the authoritative source for all workflow audits. Read it first. It covers the rationale, step-by-step process, compliance requirements, artifact synchronization, exception handling, and continuous improvement mandate.

### 2. Audit Cheat Sheet
- Use `0 audit_cheat_sheet.md` as a rapid-reference for best practices, common pitfalls, and checklist items during any audit or documentation effort.

### 3. Template Artifacts: The “Golden Path” for a Workflow Audit
- These three files, using WF2 as an example, show the required artifacts and the order in which to create them for any workflow:
  - `1 WF2-Staging Editor Dependency Trace.md`: The starting point. Maps all files, modules, and boundaries for the workflow.
  - `2 WF2-StagingEditor_linear_steps.md`: The step-by-step mapping of every atomic action, file, and architectural principle for the workflow.
  - `3 WF2-StagingEditor_CANONICAL.yaml`: The canonical YAML that encodes the workflow for automation, audit, and CI enforcement.

### 4. Audit Process Overview
#### A. Workflow Audit Steps
1. **Dependency Trace:**
   - Begin with a markdown file mapping all files, services, and dependencies for the workflow.
2. **Linear Steps Document:**
   - Create a step-by-step markdown, mapping each file/action to architectural principles. Let the real workflow dictate the structure.
3. **Canonical YAML:**
   - Update the workflow’s YAML to reflect the linear steps and ensure 1:1 mapping.
4. **Python File Audit:**
   - For every file referenced in the YAML:
     - Check for compliance (ORM, error handling, transaction boundaries, etc.)
     - Annotate as [NOVEL] or [SHARED] in the status map.
     - Log technical debt, exceptions, or orphan status.
5. **Cross-Reference & Logging:**
   - All findings, issues, and exceptions must be logged in both the micro work order and the master WORK_ORDER.md.
6. **Audit Traceability:**
   - Every audit action (file edit, annotation, exception, or technical debt log) must be timestamped (ISO8601, with timezone) for full traceability.
7. **Exception Handling Discipline:**
   - If any checklist item or compliance requirement is not met, a documented exception must be added to both the micro work order and the master WORK_ORDER.md, with rationale and remediation plan.
8. **Continuous Template Evolution:**
   - If new best practices, ambiguities, or audit gaps are discovered, update both the micro work order template and this context guide immediately. The process must evolve with each workflow.
9. **Artifact Synchronization:**
   - All changes to workflow documentation (dependency trace, linear steps, YAML, file status map) must be synchronized before marking an audit as complete. No artifact may lag behind.

---

## Key Compliance Requirements
- **ORM Only:** All DB access must use SQLAlchemy ORM. Raw SQL is prohibited except for documented, reviewed exceptions.
- **Separation of Concerns:** Each file/module must comply with architectural principles. Brief references to principle docs are sufficient if actual code compliance is demonstrated.
- **Source/Destination Table & Trigger Documentation:** For each workflow, explicitly document:
  - The source (input) table and destination (output) table.
  - The trigger/status field (e.g., `queued`) that initiates processing.
  - How background services monitor the trigger, process the row, and write to the destination.
  - This must be made clear in both the linear steps and the canonical YAML.
  - This clarity supports templated workflow creation and ensures all dependencies (ENUMs, fields, sample data) are defined before coding begins.
- **File Status Mapping:** Every file must be tracked as [NOVEL] or [SHARED]. New files should be annotated with the audit that added them (e.g., `# Added during WF3 audit`).
- **Orphan File Identification:** Files not referenced in any workflow after all audits are candidates for removal (excluding system files like .env, docker-compose.yml). No file may be removed solely on static analysis; manual review and explicit sign-off are mandatory for all code removal decisions.
- **Manual Review:** Required for any code removal or major change.
- **Log All Exceptions:** All exceptions, technical debt, and issues must be logged and timestamped.
- **Continuous Improvement:** If a better practice is discovered, update this document immediately.

---

## Best Practices & Documentation Guidance
- **Start with Templates:** Review the templates in this directory (dependency trace, linear steps, canonical YAML) before beginning any new workflow audit.
- **Adapt the Templates:** Copy and adapt these files for your new workflow, following the order and requirements in this guide.
- **Keep Templates Up to Date:** Always keep templates and references up to date as new best practices emerge.
- **When in Doubt:** Consult this guide, the root-level CONTEXT_GUIDE.md, and the latest micro work order template.
- **Log All Exceptions:** All exceptions, technical debt, and issues must be logged in both the micro work order and master log.
- **Timestamps:** All logs and exceptions must use ISO8601 with timezone.
- **Reviewer & Date:** Every micro work order must be signed and dated.

---

## Key Templates & Artifacts
- **0 audit_cheat_sheet.md:** Quick-reference checklist for audits
- **1 WF2-Staging Editor Dependency Trace.md:** Example dependency trace
- **2 WF2-StagingEditor_linear_steps.md:** Example linear steps doc
- **3 WF2-StagingEditor_CANONICAL.yaml:** Example canonical YAML

---

## Quick Links
- [Audit Cheat Sheet](./0%20audit_cheat_sheet.md)
- [Router Map](../1-main_routers.md)
- [Evaluation Progress](../2-evaluation_progress.yaml)
- [Python File Status Map](../3-python_file_status_map.md)
- [Example Dependency Trace](./1%20WF2-Staging%20Editor%20Dependency%20Trace.md)
- [Example Linear Steps](./2%20WF2-StagingEditor_linear_steps.md)
- [Example Canonical YAML](./3%20WF2-StagingEditor_CANONICAL.yaml)

---

## Ambiguity & Exception Protocol
- If ambiguity or missing context is encountered, pause and consult the project lead before logging exceptions.
- If any checklist item or compliance requirement is not met, a documented exception must be added to both the micro work order and the master WORK_ORDER.md, with rationale and remediation plan.

---

## Summary
This document, and the order in which you use it, is your roadmap for conducting bulletproof, auditable workflow documentation and audits in ScraperSky. If you are unsure at any step, consult this guide and the latest micro work order template. This is your single source of truth. Do not consult any other onboarding or protocol documents unless specifically referenced here.


## 2. Audit Process Overview

### A. Workflow Audit Steps
1. **Dependency Trace:**
   - Begin with a markdown file mapping all files, services, and dependencies for the workflow.
2. **Linear Steps Document:**
   - Create a step-by-step markdown, mapping each file/action to architectural principles. Let the real workflow dictate the structure.
3. **Canonical YAML:**
   - Update the workflow’s YAML to reflect the linear steps and ensure 1:1 mapping.
4. **Python File Audit:**
   - For every file referenced in the YAML:
     - Check for compliance (ORM, error handling, transaction boundaries, etc.)
     - Annotate as [NOVEL] or [SHARED] in the status map.
     - Log technical debt, exceptions, or orphan status.
5. **Cross-Reference & Logging:**
   - All findings, issues, and exceptions must be logged in both the micro work order and the master WORK_ORDER.md.
6. **Audit Traceability:**
   - Every audit action (file edit, annotation, exception, or technical debt log) must be timestamped (ISO8601, with timezone) for full traceability.
7. **Exception Handling Discipline:**
   - If any checklist item or compliance requirement is not met, a documented exception must be added to both the micro work order and the master WORK_ORDER.md, with rationale and remediation plan.
8. **Continuous Template Evolution:**
   - If new best practices, ambiguities, or audit gaps are discovered, update both the micro work order template and this context guide immediately. The process must evolve with each workflow.
9. **Artifact Synchronization:**
   - All changes to workflow documentation (dependency trace, linear steps, YAML, file status map) must be synchronized before marking an audit as complete. No artifact may lag behind.

---

### B. Key Compliance Requirements
- **ORM Only:**
  - All DB access must use SQLAlchemy ORM. Raw SQL is prohibited except for documented, reviewed exceptions.
- **Separation of Concerns:**
  - Each file/module must comply with architectural principles. Brief references to principle docs are sufficient if actual code compliance is demonstrated.
- **Source/Destination Table & Trigger Documentation:**
  - For each workflow, explicitly document:
    - The source (input) table and destination (output) table.
    - The trigger/status field (e.g., `queued`) that initiates processing.
    - How background services monitor the trigger, process the row, and write to the destination.
  - This must be made clear in both the linear steps and the canonical YAML.
  - This clarity supports templated workflow creation and ensures all dependencies (ENUMs, fields, sample data) are defined before coding begins.
- **File Status Mapping:**
  - Every file must be tracked as [NOVEL] or [SHARED]. New files should be annotated with the audit that added them (e.g., `# Added during WF3 audit`).
- **Orphan File Identification:**
  - Files not referenced in any workflow after all audits are candidates for removal (excluding system files like .env, docker-compose.yml).
  - No file may be removed solely on static analysis; manual review and explicit sign-off are mandatory for all code removal decisions.

---

### C. Workflow Documentation Clarifications
- **Linear Steps Structure:**
  - Let the actual dependency trace and workflow logic dictate the structure. Do not force a previous template—flexibility is encouraged.
- **Principle References:**
  - Brevity is fine as long as you reference the relevant architectural principle or guide. The focus is on real compliance, not just documentation.
  - Example: "Yes, this step complies with [Separation of Concerns Guide](../Docs_1_AI_GUIDES/...)."
- **File Map Annotation:**
  - Annotate new file entries in `3-python_file_status_map.md` with a comment for traceability.
- **YAML/Linear Steps Sync:**
  - You may update the YAML as you go, or after completing the linear steps, whichever best preserves context and accuracy.

---

### C. Documentation & Template Guidance
- **Micro Work Order Template:**
  - Use for every audit. Adapt structure to fit the workflow’s real logic.
- **Brevity with Compliance:**
  - Documentation should be brief but must reference the relevant architectural principle and confirm actual code compliance.
- **Continuous Improvement:**
  - If new best practices or ambiguities are found, update this context document, the template, and the cheat sheet immediately.
- **Timestamps:**
  - All logs and exceptions must use ISO8601 with timezone.
- **Reviewer & Date:**
  - Every micro work order must be signed and dated.

---

### D. Ultimate Goal
- **Impeccable YAMLs:**
  - Each workflow’s YAML should be so clear and complete that a future questionnaire could generate new workflows with all supporting provisions (ENUMs, fields, sample data) in the correct order, before coding begins.

---

### E. Ambiguity Protocol
- If ambiguity or missing context is encountered, pause and consult the project lead before logging exceptions.

---

## 3. Key References
- **Canonical Templates:** micro_work_order_template.md, audit_cheat_sheet.md
- **Example Audits:** WF1-SingleSearch, WF2-StagingEditor (linear steps, micro work order, YAML)
- **Status Mapping:** 3-python_file_status_map.md
- **Principle Docs:** Docs_1_AI_GUIDES/ (Absolute ORM Requirement, Separation of Concerns, etc.)

---

## 4. Quick-Start Checklist
- [ ] Read this context document fully.
- [ ] Review the latest micro work order template and cheat sheet.
- [ ] Begin with the dependency trace for the workflow.
- [ ] Let the real workflow dictate the linear steps structure.
- [ ] Audit every referenced file for compliance and log findings.
- [ ] Update YAML and file status map as you go.
- [ ] Log all exceptions and technical debt in both the micro work order and WORK_ORDER.md.
- [ ] Update this document if a better practice is discovered.

---

_By following this context guide, any contributor should be able to execute a workflow audit with zero ambiguity, full rigor, and maximum efficiency._
