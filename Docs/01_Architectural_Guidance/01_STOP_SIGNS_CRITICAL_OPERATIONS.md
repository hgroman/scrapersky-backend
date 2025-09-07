# 🛑 STOP Sign Registry: Critical Operations Requiring Human Review

**Version:** 2.1  
**Last Updated:** 2025-08-17 (WF7 Postmortem Integration)
**Owner:** The Architect
**Purpose:** To codify a list of high-risk operations that require a **FULL STOP** and mandatory human review before execution. This is a primary safeguard against repeating the Guardian's Paradox catastrophe.

**Compliance is not optional. Attempting to bypass these checks is a Level 1 Constitutional Violation.**

**ESCALATION PATH:** If uncertain about any operation, contact The Architect or relevant Layer Guardian via DART task or code comment.

---

## General Rule

If your task requires an action on this list, you must:
1.  **STOP** all execution.
2.  **NOTIFY** the user that you have encountered a mandatory STOP sign.
3.  **STATE** the specific operation you are attempting.
4.  **LINK** to this document and the specific check required.
5.  **AWAIT** explicit human permission to proceed.

---

## The Registry of Critical Operations

### 1. Database Schema Modification

- **Operation:** Any change to the database structure, including `ALTER TABLE`, `CREATE TABLE`, changing `ENUM` types, or modifying columns.
- **Reason:** Database schema changes are irreversible and were the root cause of the Guardian's Paradox. Code can be reverted; database structure cannot.
- **Required Check:** The proposed change must be reviewed and approved by the L1 Data Sentinel and a human operator.
- **Completion Criteria:** Migration script tested in development, rollback plan documented, human approval received
- **Relevant Document:** `Docs/Docs_10_Final_Audit/v_Layer-1.1-Models_Enums_Blueprint.md`

### 2. Core Model Renaming or Deletion

- **Operation:** Renaming or deleting any SQLAlchemy model file in `src/models/`.
- **Reason:** Model names are tied to database table names. Renaming them without a corresponding, verified database migration will break the application.
- **Required Check:** Must be accompanied by a tested database migration script. Requires approval from the L1 Data Sentinel.
- **Completion Criteria:** All imports updated, migration tested, no orphaned references
- **Relevant Document:** `Docs/01_Architectural_Guidance/V7_Migration_Framework/`

### 3. Mass File Renaming or Restructuring

- **Operation:** Any automated script or process that renames or moves **MORE THAN 5 FILES** at once, especially those related to the V7 Naming Convention.
- **Threshold:** Exactly 5 files = proceed with caution, 6+ files = MANDATORY STOP
- **Reason:** Mass renaming breaks import statements across the entire application, which was the central failure of the WF7 crisis.
- **Required Check:** A full test suite run must be planned immediately after the operation. Requires approval from the L3 Router Guardian and L5 Config Conductor.
- **Completion Criteria:** Import verification script run, all tests pass, server starts successfully
- **Relevant Document:** `Docs/Docs_35_WF7-The_Extractor/21_WF7_Anti_Patterns_Catalog.md`

### 4. Modification of Core Configuration or Middleware

- **Operation:** Changing files within `src/config/`, especially `settings.py`, `logging_config.py`, or any dependency injection setup.
- **Reason:** These files control the fundamental operating parameters of the entire application. An incorrect change can render the system inoperable.
- **Required Check:** Must be reviewed and approved by the L5 Config Conductor.
- **Completion Criteria:** Environment variables documented, Docker test successful, rollback procedure defined
- **Relevant Document:** `Docs/Docs_10_Final_Audit/v_Layer-5.1-Configuration_Blueprint.md`

### 5. Changing Authentication or Authorization Logic

- **Operation:** Modifying any code related to JWT, passwords, or user permissions in `src/auth/`.
- **Reason:** Security logic failure has catastrophic implications for data privacy and system integrity.
- **Required Check:** Must be reviewed by the L3 Router Guardian and the L4 Service Guardian. A security audit plan is required.
- **Completion Criteria:** Security audit completed, penetration test passed, human security review approved
- **Relevant Document:** `personas_layers/L3_Router_Guardian_Pattern_AntiPattern_Companion_v2.0.md`

<!-- WF7 POSTMORTEM INTEGRATION START - Source: WF7_POSTMORTEM_INTEGRATION_QUEUE.md -->

### 6. Documentation Deception

- **Operation:** Creating glowing documentation to hide non-compliant implementations
- **Reason:** AI wrote case studies claiming success while violating 78% of standards
- **Required Check:** All documentation must reference actual code with file:line citations
- **Completion Criteria:** Code review confirms documentation matches implementation
- **Threshold:** ANY mismatch between docs and code = STOP
- **Relevant Document:** `Docs/Docs_35_WF7-The_Extractor/20_The_Great_Revision_Lie.md`

### 7. Compliance Theater

- **Operation:** AI claiming to follow process while systematically violating it
- **Reason:** WF7 crisis showed AI can perform compliance while ignoring all standards
- **Required Check:** Verification steps with concrete evidence required
- **Completion Criteria:** Actual artifacts prove compliance, not just claims
- **Threshold:** Claims without evidence = STOP
- **Relevant Document:** `Docs/02_State_of_the_Nation/Report_WO_002_WF7_Crisis_Timeline_Analysis.md`

### 8. Analysis Paralysis

- **Operation:** More than 80 uncommitted files accumulated
- **Reason:** 88 files for 10+ days indicates learning without action
- **Required Check:** Git status review before continuing analysis
- **Completion Criteria:** Commit or explicitly defer files
- **Threshold:** >80 files = STOP and commit
- **Relevant Document:** `Docs/02_State_of_the_Nation/Report_WO_006_Git_Status_Pattern_Analysis.md`

### 9. Critical Configuration File Creation

- **Operation:** Creating a critical configuration file (e.g., `.env`, `docker-compose.yml`) because a system tool reports it as missing.
- **Reason:** A verified discrepancy exists where system tools cannot see a file that is present in the IDE. This creates a high risk of data loss by overwriting existing configurations. This is a critical Windsurf platform limitation.
- **Required Check:** If any tool reports a critical file like `.env` as missing, I must **STOP** all actions. I must report the tool output and explicitly state the file system discrepancy. I must then request visual confirmation from the user before taking any corrective action.
- **Completion Criteria:** Explicit user permission to proceed after visual confirmation.
- **Relevant Document:** This document.

<!-- WF7 POSTMORTEM INTEGRATION END -->

---

## ESCALATION PROCEDURES

### When to Escalate
- Uncertainty about whether an operation qualifies as a STOP condition
- Conflicting guidance from different documents
- Emergency requiring bypass of normal procedures

### How to Escalate
1. **Primary:** Create DART task tagged "STOP_SIGN_ESCALATION"
2. **Secondary:** Add comment in code: `# STOP_SIGN: Awaiting human review`
3. **Emergency:** Direct message to project lead with "🛑 STOP SIGN" prefix

### Response Time Expectations
- **Critical (Production Down):** 15 minutes
- **High (Blocking Development):** 2 hours
- **Normal (Planning Stage):** 24 hours

---

## COMPLETION VERIFICATION

Each STOP operation is considered complete only when:
1. ✅ Required Guardian approvals obtained
2. ✅ Completion criteria met
3. ✅ Tests pass
4. ✅ Rollback plan documented
5. ✅ Human operator signs off

--- 

This registry is the embodiment of lessons learned through failure. Respect it.
