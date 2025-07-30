# WORKFLOW TRUTH DOCUMENTATION PROTOCOL
**PhD-Level Code Analysis Framework for Mission-Critical Documentation**

**OXYGEN SYSTEM LEVEL IMPORTANCE - CONTEXT WINDOW SURVIVAL GUIDE**

---

## WHAT YOU JUST ACCOMPLISHED

You created WF4_Domain_Curation_Guardian_v3.md - a mission-critical truth document that provides complete operational authority based on ACTUAL CODE ANALYSIS. This is the gold standard. You must replicate this exact approach for every workflow.

---

## THE PROTOCOL (EXACT STEPS TO REPLICATE SUCCESS)

### PHASE 1: GATHER THE CANONICAL SOURCES (EVERY WORKFLOW HAS THESE 4)

For any workflow WFX, collect these EXACT files:
1. **`/Docs/Docs_7_Workflow_Canon/Dependency_Traces/WFX-[Workflow Name].md`**
2. **`/Docs/Docs_7_Workflow_Canon/Linear-Steps/WFX-[WorkflowName]_linear_steps.md`**  
3. **`/Docs/Docs_7_Workflow_Canon/workflows/v_[XX]_WFX_CANONICAL.yaml`**
4. **`/Docs/Docs_7_Workflow_Canon/Micro-Work-Orders/WFX-[Workflow Name]_micro_work_order.md`**

**CRITICAL:** These files contain the architectural foundation. Read them first to understand the intended design.

### PHASE 2: IDENTIFY THE HEART (FIND THE CORE BUSINESS LOGIC)

For WF4, the heart was lines 229-236 in `/src/routers/domains.py`:
```python
if db_curation_status == SitemapCurationStatusEnum.Selected:
    domain.sitemap_analysis_status = SitemapAnalysisStatusEnum.queued
```

**FOR ANY WORKFLOW:** Find the equivalent core business logic by:
1. **Read the router file** mentioned in the dependency trace
2. **Look for conditional logic** that transforms user actions into system state
3. **Find the dual-status pattern** or equivalent transformation logic
4. **Identify the exact lines** that create business value

### PHASE 3: VERIFY AGAINST ACTUAL CODE (REALITY CHECK)

**CRITICAL LESSON FROM WF4:** The documentation referenced `domain_to_sitemap_adapter_service.py` which didn't exist in the running code. 

**FOR EVERY WORKFLOW:**
1. **Read every file** mentioned in the dependency trace
2. **Verify imports** - ensure services are actually called
3. **Check for orphaned references** - documentation vs. reality gaps
4. **Test the actual execution path** - what code actually runs?

### PHASE 4: MAP THE COMPLETE DATA FLOW (EXACT EXECUTION SEQUENCE)

**WF4 Pattern (replicate this structure):**
```
Stage 1: User Trigger (UI files)
Stage 2: API Processing (router files with exact line numbers)
Stage 3: Background Processing (scheduler files with exact functions)
Stage 4: Actual Work (core service files)
```

**FOR ANY WORKFLOW:** Map the identical 4-stage pattern with:
- **Exact file paths and line numbers**
- **Function names and signatures**
- **Status field transitions**
- **Database operations**

### PHASE 5: DOCUMENT THE ECOSYSTEM POSITION (PRODUCER-CONSUMER)

**WF4 Pattern:**
```
WF3 → domains.sitemap_curation_status = 'New'
WF4 → User selection → sitemap_analysis_status = 'queued'  
WF5 → Consumes queued analysis jobs
```

**FOR ANY WORKFLOW:** Document:
- **What it consumes from** (previous workflow)
- **What it produces for** (next workflow)  
- **Exact table and field names**
- **Status values that trigger handoffs**

### PHASE 6: IDENTIFY CRITICAL DEPENDENCIES (FAILURE POINTS)

**WF4 Pattern:**
- Database tables with dual status fields
- APScheduler running for background processing
- Service dependencies (SitemapAnalyzer)
- Configuration (polling intervals, batch sizes)

**FOR ANY WORKFLOW:** Document:
- **Database tables owned by this workflow**
- **Background services that must be running**
- **External service dependencies**
- **Configuration values that affect behavior**

### PHASE 7: PROVIDE EMERGENCY PROCEDURES (OPERATIONAL INTELLIGENCE)

**WF4 Pattern:**
- Database queries to check stuck records
- Log commands to verify services running
- API testing procedures
- Recovery steps for common failures

**FOR ANY WORKFLOW:** Create:
- **Diagnostic database queries**
- **Log analysis commands**
- **API testing procedures**
- **Recovery procedures for each failure mode**

---

## THE CRITICAL SUCCESS FACTORS (WHAT MADE WF4 DOCUMENTATION PERFECT)

### 1. **CODE REALITY OVER DOCUMENTATION CLAIMS**
- I believed the dependency trace about adapter service
- You forced me to read the actual scheduler code
- **TRUTH:** The scheduler calls SitemapAnalyzer directly
- **LESSON:** Always verify documentation against running code

### 2. **EXACT LINE NUMBER REFERENCES**
- Every critical statement traced to specific code lines
- Router lines 229-236 for dual-status logic
- Scheduler line 117 for actual processing call
- **LESSON:** Line numbers provide surgical precision for debugging

### 3. **BUSINESS LOGIC FOCUS**
- Found the dual-status update pattern as the core value
- Explained WHY the pattern exists (user action → automation)
- Documented WHAT breaks if the pattern fails
- **LESSON:** Identify the business transformation, not just technical steps

### 4. **EMERGENCY READINESS**
- Provided database queries for troubleshooting
- Listed common failure scenarios with solutions
- Gave log commands for service verification
- **LESSON:** Documentation must enable rapid problem resolution

### 5. **ECOSYSTEM AWARENESS**
- Documented WF3 → WF4 → WF5 relationships
- Explained producer-consumer status handoffs
- Showed complete data flow chain
- **LESSON:** No workflow exists in isolation

---

## THE TEMPLATE STRUCTURE (COPY THIS EXACT FORMAT)

```markdown
# WFX_[Workflow_Name]_Guardian_v3.md - TRUTH DOCUMENT

## CRITICAL CONTEXT
[Why someone would need this document]

## WHAT WFX IS (CODE REALITY)
[Core business logic with exact line references]

## COMPLETE FILE DEPENDENCY MAP
[All files organized by layer with line references]

## WORKFLOW DATA FLOW (EXACT EXECUTION SEQUENCE)
[4-stage pattern with precise technical details]

## PRODUCER-CONSUMER CHAIN (ECOSYSTEM POSITION)
[What triggers it, what it produces, complete chain]

## STATUS FIELD TRANSITIONS (DATA STATE MACHINE)
[Exact status values and transitions with line references]

## CRITICAL DEPENDENCIES (FAILURE POINTS)
[Database, service, and configuration dependencies]

## KNOWN ARCHITECTURAL FACTS
[Key patterns and implementation details]

## WHERE TO GET MORE INFORMATION
[Authoritative sources and investigation paths]

## WHAT CAN GO WRONG (ERROR SCENARIOS)
[Common failures with specific symptoms]

## EMERGENCY PROCEDURES
[Diagnostic queries and recovery steps]

## FINAL WARNING
[Version control and maintenance requirements]
```

---

## QUALITY GATES (HOW TO VERIFY YOU'VE ACHIEVED PhD LEVEL)

### ✅ **CODE REALITY CHECK**
- Every file mentioned in dependency trace actually exists
- Every function call actually happens in the code
- Every status transition is implementable
- No orphaned services or missing implementations
- **Function signature verification:** `grep -n "function_name" source_file.py` confirms existence
- **Service call tracing:** Verify import → instantiation → invocation chain
- **Database schema validation:** Test every SQL query against actual tables

### ✅ **EMERGENCY READINESS CHECK**
- Can a future AI quickly find the core business logic?
- Are diagnostic procedures specific and actionable?
- Do database queries actually work for troubleshooting?
- Are recovery procedures testable?

### ✅ **ECOSYSTEM INTEGRATION CHECK**
- Is the producer-consumer chain clearly documented?
- Are workflow handoffs specified with exact table/field names?
- Is the position in the overall system architecture clear?
- Are dependencies on other workflows explicit?

### ✅ **OPERATIONAL INTELLIGENCE CHECK**
- Does the document enable rapid problem diagnosis?
- Are failure modes identified with specific solutions?
- Is the core business value clearly explained?
- Can someone modify the workflow safely using this guide?

---

## EXECUTION COMMAND FOR FUTURE SELF

**When your context window expires, use this exact command:**

```
Create [WFX]_[Workflow_Name]_Guardian_v3.md using the WORKFLOW_TRUTH_DOCUMENTATION_PROTOCOL. 

1. Read the 4 canonical source documents for WFX
2. Identify the core business logic in the router file  
3. Verify every file mentioned actually exists in the codebase
4. Map the complete 4-stage data flow with exact line references
5. Document the producer-consumer ecosystem position
6. Provide emergency procedures with diagnostic queries
7. Follow the exact template structure from the protocol
8. Apply all 4 quality gates before completion

The goal is mission-critical operational documentation that enables rapid problem resolution based on actual code reality, not documentation assumptions.
```

---

## COMMON ERROR PATTERNS TO VERIFY

**Based on WF3 and WF4 validation experience, every Guardian document MUST be checked for:**

### Function Reference Errors
```bash
# Test EVERY function claim with actual grep
grep -n "claimed_function_name" path/to/source_file.py
```
**WF3 Example:** Document claimed `process_single_business()` but actual function was `create_pending_domain_from_local_business()`

### Status Value Errors
```bash
# Verify status enums in model files
grep -n "status.*=" src/models/target_model.py
```
**WF3 Example:** Document claimed `sitemap_curation_status='New'` but actual value was `status="pending"`

### Service Call Validation
**For every service claim, verify this chain:**
1. **Import exists:** `from src.services.X import Y`
2. **Instantiation occurs:** `service = Y()`
3. **Method called:** `service.method_name(params)`

### Database Query Testing
**Every emergency query MUST be tested:**
```sql
-- Test this query returns actual results
SELECT COUNT(*) FROM claimed_table WHERE claimed_field = 'claimed_value';
```

### Scheduler Reference Verification
**Common error:** Claiming wrong polling intervals or batch sizes
```bash
# Verify actual configuration values
grep -n "INTERVAL\|BATCH_SIZE" src/services/scheduler_file.py
grep -n "scheduler" docker-compose.yml
```

---

## AUDITOR MANDATE: ZERO TOLERANCE

**The WF3 validation caught 2 production-breaking errors that would have caused:**
- "Method not found" errors during emergency debugging
- Database queries returning zero results during incidents

**This proves the auditor persona is MANDATORY, not optional. Every workflow Guardian MUST undergo hostile skepticism review before being considered complete.**

---

## FINAL WISDOM

**What you learned creating WF4 and WF3 documentation:**
- Documentation can lie, code tells the truth
- Business logic lives in specific lines, not general descriptions  
- Emergency readiness requires actionable procedures
- Ecosystem position is as important as internal mechanics
- **The auditor persona catches production-breaking errors that look like minor details**
- **Every workflow has unique gotchas:** WF4 had orphaned services, WF3 had wrong function names
- **Verification scripts are mandatory:** grep testing prevents "method not found" emergencies

**Apply this exact methodology to WF1, WF2, WF5, WF6, WF7. Each workflow has the same canonical documentation structure. Each deserves the same PhD-level analysis, and each WILL have errors that only the auditor persona can catch.**

**The oxygen system depends on this level of rigor for every critical component.**