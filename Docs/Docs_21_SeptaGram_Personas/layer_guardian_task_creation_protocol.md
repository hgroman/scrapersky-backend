# Layer Guardian Task Creation Protocol

**Version:** 1.0  
**Date:** 2025-08-02  
**Purpose:** Standardized protocol for Layer Guardian personas to create actionable DART tasks from audit findings

---

## Core Principle

Transform **audit findings** into **specific, actionable tasks** assigned to appropriate **Workflow Guardians** for execution. Layer Guardians provide advisory analysis; Workflow Guardians execute changes.

---

## Task Breakdown Strategy

### 1. Chunk Analysis
- **Read audit chunk completely** before creating tasks
- **Identify distinct violations** - each gets separate task
- **Group related violations** only if they require coordinated fix

### 2. Task Granularity Rules
✅ **Create separate tasks for:**
- Different files with same violation type
- Different violation types in same file  
- Violations requiring different workflow owners

❌ **DO NOT bundle:**
- Multiple critical violations into one task
- Cross-workflow issues into single task
- Different Blueprint sections into one task

---

## Standard Task Template

### Title Format
```
L[LayerNumber]-CHUNK[Number]-[Letter]: [Specific Violation] in [full_file_path]
```
**Examples:**
- `L1-CHUNK8-A: Remove Integer Primary Key Override in src/models/job.py`
- `L1-CHUNK2-B: Resolve SitemapType ENUM Duplication in src/models/api_models.py`

### Required Sections

**1. PROBLEM**
- **File:** Full absolute path to file containing violation
- **Source Chunk:** Full absolute path to audit chunk that identified the issue
- **Violation:** Specific violation with code reference
- **Blueprint Reference:** Full path to blueprint document + specific section
- **Current vs Expected State:** Clear comparison

**2. IMPACT** 
- Cross-workflow effects
- Architectural consistency issues
- System risks

**3. SOLUTION**
- **Steps:** Clear actionable steps (numbered list)
- **Files to Modify:** Full absolute paths to all files requiring changes
- **Expected Outcome:** Specific compliance target
- **Reference Files:** Full paths to compliant examples (if applicable)

**4. BLUEPRINT REFERENCE**
- **Document:** Full absolute path to blueprint document
- **Section:** Specific section number and title
- **Authority:** Direct quote or paraphrase of the violated principle

**5. VERIFICATION**
- Testing criteria
- Success metrics
- Validation steps

### Assignment Rules

**Workflow Domain Mapping:**
- **Place/PlaceSearch models** → `WF1_The_Scout`
- **Staging/curation processes** → `WF2_The_Analyst`  
- **LocalBusiness models** → `WF3_The_Navigator`
- **Domain models** → `WF4_The_Surveyor`
- **Sitemap models** → `WF5_The_Flight_Planner`
- **Page/URL models** → `WF6_The_Recorder`
- **Contact/Profile models** → `WF7_The_Extractor`

**Cross-Workflow Issues:**
- **Job/BatchJob models** → Assign to most affected workflow
- **BaseModel violations** → Assign to primary model's workflow
- **ENUM duplications** → Assign to workflow that owns primary usage

### Tagging Standards

**Required Tags (7-tag pattern):**
1. **Workflow:** `"WF[#]-[Role]"` (e.g., `"WF1-Scout"`)
2. **Layer:** `"Layer[#]"` (e.g., `"Layer1"`)
3. **Violation Type:** Descriptive (e.g., `"Primary-Key-Violation"`)
4. **File/Component:** `"[filename]"` (e.g., `"job.py"`) - filename only, not full path
5. **Priority Level:** `"Critical-Fix"`, `"High-Fix"`, `"Medium-Fix"`
6. **Architecture Pattern:** `"BaseModel"`, `"ENUM"`, `"Database-Naming"`
7. **Chunk Reference:** `"Chunk-[#]"` (e.g., `"Chunk-8"`)

### Priority Guidelines

**Critical:**
- Primary key violations
- BaseModel inheritance failures
- System-wide duplications with conflicts
- Database integrity issues

**High:**
- ENUM naming standard violations
- Database naming convention violations
- Foreign key pattern violations

**Medium:**
- ENUM location violations
- Standard value violations
- Documentation inconsistencies

**Low:**
- Informational/compliant items
- Reference implementations

---

## Workflow Continuation Protocol

### Context Loss Recovery
If context window maxes out, next session should:

1. **Check Progress:** Review existing DART tasks with `Chunk-[#]` tags
2. **Resume from Last:** Identify highest processed chunk number
3. **Use This Protocol:** Apply same template and standards
4. **Maintain Consistency:** Use identical tagging patterns

### Verification Phase Support
When Workflow Guardians begin verification:

1. **Current State Evidence:** Add code snippets showing violation still exists
2. **Line Numbers:** Add specific location references  
3. **Related Files:** Document files that might be affected by changes
4. **Testing Notes:** Add specific test scenarios for verification

---

## Quality Assurance

### Pre-Creation Checklist
- [ ] Task title follows L[#]-CHUNK[#]-[Letter] format
- [ ] Assigned to correct workflow owner
- [ ] All 7 required tags present
- [ ] Blueprint section cited
- [ ] Solution steps are actionable
- [ ] Impact explains cross-workflow effects

### Post-Creation Verification
- [ ] Task appears in correct dartboard
- [ ] Tags allow filtering by workflow/chunk/priority
- [ ] Description renders properly in DART
- [ ] Assignment matches domain mapping

---

## Template Example

```markdown
**Title:** L1-CHUNK4-A: Remove Integer Primary Key Override in src/models/batch_job.py

**Description:**
**CRITICAL PRIMARY KEY VIOLATION**

## PROBLEM
**File:** `/Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/batch_job.py`
**Source Chunk:** `/Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/Docs/Docs_10_Final_Audit/Audit Reports Layer 1/v_Layer1_Models_Enums_Audit_Report_CHUNK_4_of_10_batch_job.md`
**Violation:** BatchJob model overrides BaseModel's UUID primary key with Integer:
```python
id = Column(Integer, primary_key=True, autoincrement=True)
```
**Current vs Expected:** Currently uses Integer PK, should use BaseModel's UUID PK

## IMPACT
- Creates inconsistent PK patterns across models
- Breaks foreign key references expecting UUID
- Violates architectural standard for BaseModel inheritance

## SOLUTION
**Steps:**
1. Remove the Integer `id` override in BatchJob model
2. Allow BaseModel's UUID `id` to be used
3. Remove redundant `id_uuid` column
4. Update any code that expects Integer batch job IDs

**Files to Modify:**
- `/Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/batch_job.py`

**Reference Files:**
- `/Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/base.py` (BaseModel pattern)

## BLUEPRINT REFERENCE
**Document:** `/Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/Docs/Docs_10_Final_Audit/v_Layer-1.1-Models_Enums_Blueprint.md`
**Section:** 2.1.6.1 - Primary key must be UUID from BaseModel
**Authority:** "Primary keys should be consistently named (e.g., `id`) and must inherit from BaseModel"

## VERIFICATION
- Ensure foreign key references work correctly
- Verify no hardcoded Integer ID assumptions in services
- Check background job schedulers for ID type assumptions

**Assignee:** [Appropriate_Workflow_Guardian]
**Priority:** Critical
**Tags:** ["WF#-Role", "Layer1", "Primary-Key-Violation", "batch_job.py", "Critical-Fix", "BaseModel", "Chunk-4"]
```

---

This protocol ensures consistent, actionable task creation that can be continued by any Layer Guardian across multiple sessions while maintaining architectural compliance and workflow coordination.