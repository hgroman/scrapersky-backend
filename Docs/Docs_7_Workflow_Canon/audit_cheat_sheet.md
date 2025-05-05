# Workflow Audit Cheat Sheet

_Last updated: 2025-05-04T10:06:33-07:00_

Use this bulletproof checklist for every workflow. This protocol ensures full auditability, consistency, and Supabase compatibility. **Follow these steps for each workflow:**

---

**Workflow Name:**  
**YAML File:**  
**Date/Time:**  
**Reviewer:**  

---

## 1. Dependency Trace
- [ ] Review and update dependency trace document
- [ ] Ensure all files are referenced
- [ ] Annotate each file as [NOVEL] or [SHARED]

## 2. Linear Steps Document
- [ ] Create or update linear steps doc
- [ ] Map all steps from UI to DB
- [ ] Reference all files, actions, principles, and guides
- [ ] Annotate each file as [NOVEL] or [SHARED]

## 3. Canonical YAML
- [ ] Create or update canonical YAML for workflow
- [ ] Ensure all steps, files, and principles match linear steps
- [ ] Explicitly annotate ORM enforcement and architectural mandates
- [ ] Reference all relevant guides
- [ ] Validate YAML against schema

## 4. Cross-Reference Artifacts
- [ ] Ensure dependency trace, linear steps, and YAML are in sync
- [ ] Confirm all files and principles are mirrored across docs
- [ ] No orphaned or ambiguous files

## 5. Update python_file_status_map.md
- [ ] Add or confirm each file’s status and references
- [ ] Flag any orphaned files for review/removal

## 6. Update Workflow Artifact Completion Tracker
- [ ] Mark checkboxes for completed artifacts in WORK_ORDER.md

## 7. Log Progress
- [ ] Add a timestamped progress log in WORK_ORDER.md

---

## General Audit Tips & Common Pitfalls
- Always use the [NOVEL]/[SHARED] designation from 1-main_routers.md as the authoritative source
- Pause and update python_file_status_map.md in parallel as you work
- Watch for raw SQL or non-ORM DB usage (must be flagged and remediated)
- Ensure all principles and guides are referenced in both linear steps and YAML
- Validate YAMLs before marking as complete
- Regularly audit for orphaned files and update mapping
- Document every audit step with timestamps for traceability

---

**Notes/Exceptions:**
- 

---

**Signoff:**
- [ ] All boxes checked, or exceptions documented
- [ ] Signed by reviewer

## 2. Step Actions & Code Mapping
- [ ] Each step action references a real service method or file
- [ ] Steps follow a linear, phase-by-phase structure
- [ ] Naming conventions match project standards
- [ ] All referenced models/enums exist and are used
- [ ] Dependency trace is up to date and matches codebase

## 3. Architectural Principles Alignment
- [ ] Router phase: transaction boundaries, auth boundary, thin router
- [ ] Service phase: transaction-awareness, no session creation, no auth logic
- [ ] Model phase: schema alignment, enum source of truth
- [ ] Background task phase: session management, ORM usage only
- [ ] Each phase mapped to a principle from 07-17-ARCHITECTURAL_PRINCIPLES.md

## 4. Documentation & Traceability
- [ ] Canonical YAML cross-referenced with dependency trace
- [ ] Blueprint/cheat sheet updated if new lessons learned
- [ ] Progress log updated with timestamp and summary

---

**Notes/Exceptions:**

- 

---

**Signoff:**

- [ ] All boxes checked, or exceptions documented
- [ ] Signed by reviewer

---

_Last updated: 2025-05-04 08:39 PDT_
