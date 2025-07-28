# WORKFLOW TRUTH DOCUMENTATION PROTOCOL

**Mission-Critical Code Analysis Framework for Workflow Documentation**

**VERSION:** 1.0
**PURPOSE:** Create truth-based operational documentation for ScraperSky workflows
**CRITICAL:** This protocol ensures documentation matches code reality, not assumptions

---

## OVERVIEW

This protocol guides you through creating mission-critical documentation for ScraperSky workflows. You will analyze actual code to produce documentation that enables rapid debugging and maintenance. Every claim must be traceable to specific code lines.

**Expected Output:** A v3 Guardian document following the exact format of `WF4_Domain_Curation_Guardian_v3.md`

---

## THE 7-PHASE PROTOCOL

### PHASE 1: GATHER CANONICAL SOURCES

For workflow WFX, locate these four mandatory files:

1. **`/Docs/Docs_7_Workflow_Canon/Dependency_Traces/WFX-[Workflow Name].md`**

   - Contains all files involved in the workflow
   - Shows producer-consumer relationships
   - Maps architectural layers

2. **`/Docs/Docs_7_Workflow_Canon/Linear-Steps/WFX-[WorkflowName]_linear_steps.md`**

   - Lists atomic execution steps
   - Identifies NOVEL vs SHARED components
   - Provides functional overview

3. **`/Docs/Docs_7_Workflow_Canon/workflows/v_[XX]_WFX_CANONICAL.yaml`**

   - Defines business workflow structure
   - Contains compliance requirements
   - Shows cross-workflow connections

4. **`/Docs/Docs_7_Workflow_Canon/Micro-Work-Orders/WFX-[Workflow Name]_micro_work_order.md`**
   - Details implementation requirements
   - Lists specific acceptance criteria
   - Contains testing guidelines

**ACTION:** Read all four files completely before proceeding.

### PHASE 2: IDENTIFY THE CORE BUSINESS LOGIC

**Objective:** Find the exact code that creates business value.

1. **Open the main router file** identified in the dependency trace
2. **Search for conditional logic** that transforms user input into system state
3. **Look for status updates** or state transitions
4. **Identify the exact lines** containing the business transformation

**Example from WF4:**

```python
# Lines 229-236 in /src/routers/domains.py
if db_curation_status == SitemapCurationStatusEnum.Selected:
    domain.sitemap_analysis_status = SitemapAnalysisStatusEnum.queued
    domain.sitemap_analysis_error = None
    queued_count += 1
```

**CRITICAL:** The business logic must be quoted directly from code, not paraphrased.

### PHASE 3: VERIFY CODE REALITY

**Objective:** Ensure documentation matches what actually runs in production.

For every file in the dependency trace:

1. **Verify the file exists** at the specified path
2. **Check all imports** - trace them to actual usage
3. **Follow function calls** - ensure services are actually invoked
4. **Test execution paths** - verify the code runs as documented

**Common Issues to Check:**

- Orphaned services referenced but never called
- Adapter layers that have been bypassed
- Legacy code that's no longer in the execution path
- Documentation describing intended vs. actual behavior

**Example Discovery:** In WF4, documentation referenced `domain_to_sitemap_adapter_service.py`, but the scheduler actually calls `SitemapAnalyzer` directly.

### PHASE 4: MAP THE COMPLETE DATA FLOW

**Objective:** Document the exact execution sequence with line-level precision.

Structure your flow in these four stages:

#### Stage 1: User Trigger

- UI file paths and line numbers
- Form fields and button actions
- API endpoints called
- Request payload structure

#### Stage 2: API Processing

- Router file and function (with line numbers)
- Request validation logic
- Business logic execution (core from Phase 2)
- Database transaction boundaries
- Response structure

#### Stage 3: Background Processing

- Scheduler configuration (polling interval, batch size)
- Query logic for finding work (exact SQL/ORM calls)
- Service invocation (with line numbers)
- Status update logic
- Error handling paths

#### Stage 4: Actual Work

- Core service class and methods
- Input parameters and types
- Processing logic
- Output structure
- Side effects (files created, APIs called, etc.)

### PHASE 5: DOCUMENT ECOSYSTEM POSITION

**Objective:** Show how this workflow connects to others.

Document the producer-consumer relationships:

```
Previous Workflow → Table.field = 'value'
Current Workflow → Consumes 'value' → Produces Table.field = 'new_value'
Next Workflow → Consumes 'new_value'
```

Include:

- Exact table and column names
- Status values that trigger handoffs
- Expected data volumes
- Timing dependencies

### PHASE 6: IDENTIFY FAILURE POINTS

**Objective:** Document what can break and how to detect it.

For each component, document:

#### Database Dependencies

- Required tables and columns
- Indexes needed for performance
- Transaction isolation requirements
- Connection pool settings

#### Service Dependencies

- Background schedulers that must run
- External services called
- API rate limits
- Timeout configurations

#### Configuration Dependencies

- Environment variables required
- Default values and valid ranges
- Feature flags that affect behavior
- Deployment-specific settings

### PHASE 7: CREATE EMERGENCY PROCEDURES

**Objective:** Enable rapid diagnosis and recovery during incidents.

Provide specific, runnable commands:

#### Diagnostic Queries

```sql
-- Example: Find stuck records
SELECT id, status, updated_at
FROM table_name
WHERE status = 'processing'
AND updated_at < NOW() - INTERVAL '10 minutes';
```

#### Log Analysis Commands

```bash
# Example: Check if scheduler is running
docker-compose logs service_name | grep "scheduler_started"
```

#### Recovery Procedures

1. Specific steps to unstick records
2. Commands to restart services safely
3. Rollback procedures if needed
4. Verification steps after recovery

---

## ANTI-EMBELLISHMENT ENFORCEMENT

**CRITICAL:** Every iteration will require multiple rounds of revision to achieve truth.

### Expected Iterations: 3-6 minimum

### Common Embellishments to Remove:

- "Best practices" not found in code
- "Business value" without line references
- Architectural descriptions without concrete examples
- Any claim lacking a file path and line number
- Generalizations using "typically" or "usually"

### The Verification Test:

For every sentence, ask: "Where is that in the code? What line number?"
If you cannot answer with a specific file and line, delete the sentence.

---

## REQUIRED DOCUMENT STRUCTURE

Your final document must follow this exact structure:

```markdown
# WFX\_[Workflow_Name]\_Guardian_v3.md - TRUTH DOCUMENT

**MISSION CRITICAL REFERENCE - OXYGEN SYSTEM LEVEL IMPORTANCE**

**Version:** 3.0 (Code Truth Authority)
**Created:** [Date]
**Purpose:** Complete operational authority for WFX [Workflow Name]
**Audience:** Future AI partners who need to understand and fix WFX quickly

## CRITICAL CONTEXT

[Why someone would need this document - 2-3 sentences max]

## WHAT WFX IS (CODE REALITY)

[Core business logic with exact code snippet and line references]

## COMPLETE FILE DEPENDENCY MAP

[Organized by architectural layer with line references for key logic]

## WORKFLOW DATA FLOW (EXACT EXECUTION SEQUENCE)

[4-stage pattern with specific line numbers and function calls]

## PRODUCER-CONSUMER CHAIN (ECOSYSTEM POSITION)

[Input sources, output destinations, complete chain]

## STATUS FIELD TRANSITIONS (DATA STATE MACHINE)

[Exact status values and transitions with line references]

## CRITICAL DEPENDENCIES (FAILURE POINTS)

[Database, service, and configuration requirements]

## KNOWN ARCHITECTURAL FACTS

[Key patterns, implementation details, design decisions]

## WHERE TO GET MORE INFORMATION

[Canonical sources, investigation paths, key files]

## WHAT CAN GO WRONG (ERROR SCENARIOS)

[Common failures with specific symptoms]

## EMERGENCY PROCEDURES

[Diagnostic queries, recovery steps, verification commands]

## FINAL WARNING

[Maintenance requirements and critical notes]
```

---

## QUALITY GATES

Before considering your document complete, verify:

### ✅ Code Reality Check

- Every referenced file exists at the specified path
- Every function call is traced to actual invocation
- Every status transition exists in the code
- No orphaned services or unused adapters referenced

### ✅ Emergency Readiness Check

- Core business logic can be found in under 30 seconds
- Diagnostic queries run successfully
- Recovery procedures are specific and actionable
- A stressed engineer at 3 AM can follow the procedures

### ✅ Ecosystem Integration Check

- Producer-consumer relationships are explicit
- Table and field names are exact
- Workflow dependencies are traceable
- Integration points are verified in code

### ✅ Line Number Verification

- Every technical claim has a line number reference
- Code snippets are copied exactly from source
- File paths use absolute project paths
- Version/commit references are included where critical

---

## FINAL PHASE: MISSION-CRITICAL AUDIT

**MANDATORY:** After completing your document, you must switch to the Mission-Critical Documentation Auditor persona to review your work.

1. Save your completed v3 Guardian document
2. Switch to the auditor persona (see `MISSION-CRITICAL DOCUMENTATION AUDITOR PERSONA.md`)
3. Review your document with hostile skepticism
4. Mark every unverified claim
5. Revise based on audit findings
6. Repeat until zero unverified claims remain

**The document is not complete until it passes mission-critical audit.**

---

## REMEMBER

You are creating documentation for engineers debugging critical systems under extreme pressure. Every word must be verifiable. Every procedure must be executable. Every claim must trace to its source in the code.

Documentation can lie. Code tells the truth. Stick to the code.
