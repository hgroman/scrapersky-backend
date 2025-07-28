# WORKFLOW CANONICAL DOCUMENTATION META
**The Source of Truth Architecture for ScraperSky Workflows**

**Created:** 2025-01-28  
**Purpose:** Define the canonical documentation structure that enables mission-critical workflow analysis  

---

## THE FOUR PILLARS OF WORKFLOW TRUTH

Every ScraperSky workflow (WF1-WF7) has exactly four canonical documents that form the complete architectural foundation:

### 1. DEPENDENCY TRACE
**Location:** `/Docs/Docs_7_Workflow_Canon/Dependency_Traces/WFX-[Workflow Name].md`  
**Purpose:** Complete file inventory organized by architectural layer  
**Contains:**
- All files involved in the workflow (typically 15-20 files)
- Layer-by-layer organization (L1-L7)
- Producer-consumer relationships
- File novelty annotations (NOVEL/SHARED)

### 2. LINEAR STEPS
**Location:** `/Docs/Docs_7_Workflow_Canon/Linear-Steps/WFX-[WorkflowName]_linear_steps.md`  
**Purpose:** Step-by-step execution sequence  
**Contains:**
- Atomic workflow steps in execution order
- File references for each step
- Architectural principles per step
- Implementation notes and warnings

### 3. CANONICAL YAML
**Location:** `/Docs/Docs_7_Workflow_Canon/workflows/v_[XX]_WFX_CANONICAL.yaml`  
**Purpose:** Business workflow definition  
**Contains:**
- Workflow metadata and purpose
- Compliance requirements
- Cross-workflow connections
- Vectorized for semantic search (v_ prefix)

### 4. MICRO WORK ORDER
**Location:** `/Docs/Docs_7_Workflow_Canon/Micro-Work-Orders/WFX-[Workflow Name]_micro_work_order.md`  
**Purpose:** Implementation requirements and acceptance criteria  
**Contains:**
- Specific development tasks
- Testing requirements
- Edge cases and error handling
- Success criteria

---

## HOW THEY WORK TOGETHER

```
DEPENDENCY TRACE (What files?)
    ↓
LINEAR STEPS (What order?)
    ↓
CANONICAL YAML (What business purpose?)
    ↓
MICRO WORK ORDER (What requirements?)
    ↓
GUARDIAN V3 DOCUMENT (Truth synthesis)
```

### THE SYNTHESIS PROCESS

1. **Start with Dependency Trace** - Identifies all files and their relationships
2. **Cross-reference with Linear Steps** - Understand execution flow
3. **Validate against Canonical YAML** - Ensure business alignment
4. **Check Micro Work Order** - Verify implementation details
5. **Read Actual Code** - Confirm documentation matches reality
6. **Create Guardian V3** - Synthesize operational truth

---

## CRITICAL PATTERNS TO IDENTIFY

### 1. THE HEART (Core Business Logic)
- Usually in router file (Layer 3)
- Look for conditional logic that transforms state
- Often involves dual-status updates
- Example: `if status == Selected: domain_extraction_status = Queued`

### 2. THE TRIGGER (Producer Signal)
- Status field that initiates workflow
- Set by previous workflow or user action
- Example: `sitemap_curation_status = 'New'`

### 3. THE HANDOFF (Consumer Signal)
- Status field that next workflow reads
- Set by current workflow completion
- Example: `sitemap_analysis_status = 'queued'`

### 4. THE ENGINE (Background Processor)
- Usually in `sitemap_scheduler.py` or similar
- Polls for specific status values
- Calls service to do actual work
- Example: Query for `status = 'queued'`

---

## LAYER ARCHITECTURE REFERENCE

### Layer 1: Models & ENUMs
- Database models (`/src/models/`)
- Status enumerations
- Table definitions

### Layer 2: Schemas
- API request/response models (`/src/schemas/`)
- Pydantic models

### Layer 3: Routers
- API endpoints (`/src/routers/`)
- **Contains core business logic**
- Transaction boundaries

### Layer 4: Services
- Business logic services (`/src/services/`)
- Background processors
- External integrations

### Layer 5: Configuration
- Settings and environment (`/src/config/`)
- Docker configurations

### Layer 6: UI Components
- Frontend files (`/static/`)
- JavaScript controllers
- HTML interfaces

### Layer 7: Testing
- Test coverage (`/tests/`)
- Unit and integration tests

---

## WORKFLOW INVENTORY

| Workflow | Name | Dependency Trace | Status |
|----------|------|------------------|---------|
| WF1 | Google Places Search | ✅ Exists | Needs Guardian |
| WF2 | Staging Editor | ✅ Exists | Needs Guardian |
| WF3 | Local Business Curation | ✅ Exists | **Ready for Guardian** |
| WF4 | Domain Curation | ✅ Exists | **✅ Guardian v3 Complete** |
| WF5 | Sitemap Curation | ✅ Exists | Needs Guardian |
| WF6 | Page Curation | ✅ Exists | Needs Guardian |
| WF7 | Resource Model Creation | ✅ Exists | Needs Guardian |

---

## COMMON PITFALLS

### 1. Documentation vs Reality
- **Always verify files exist** at claimed paths
- **Check imports** match actual usage
- **Trace function calls** to ensure services are invoked

### 2. Orphaned Services
- Example: `domain_to_sitemap_adapter_service.py` referenced but not used
- Scheduler may bypass adapters and call services directly
- Trust code execution path, not documentation claims

### 3. Naming Confusion
- `sitemap_scheduler.py` handles multiple workflow types
- Status enums may be shared across models
- Layer assignments may be approximate

---

## GUARDIAN CREATION CHECKLIST

For each workflow:
- [ ] Locate all 4 canonical documents
- [ ] Read dependency trace completely
- [ ] Identify router file with business logic
- [ ] Find the conditional status update code
- [ ] Verify background processor query
- [ ] Map producer-consumer relationships
- [ ] Check for orphaned services
- [ ] Create Guardian v3 following template

---

## THE GOAL

Each Guardian v3 document enables:
- **30-second problem diagnosis** during incidents
- **Surgical code navigation** with line numbers
- **Complete operational understanding** without guesswork
- **Emergency recovery procedures** that actually work

**Remember:** Documentation can lie. Code tells the truth. Always verify.