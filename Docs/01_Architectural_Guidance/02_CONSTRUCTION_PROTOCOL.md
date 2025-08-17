# ScraperSky Workflow Construction Protocol

**Version:** 2.1  
**Owner:** The Architect  
**Last Updated:** 2025-08-17 (WF7 Postmortem Integration)  
**Authority:** ScraperSky Development Constitution - SUPREME LAW  
**Purpose:** Unified construction guide with embedded compliance gates for V2/V3 workflow implementation

---

## EXECUTIVE MANDATE

This document merges construction phases with mandatory compliance checkpoints. **NO PHASE MAY PROCEED WITHOUT COMPLETING ITS EMBEDDED CHECKPOINT.**

Failure to obtain Layer Guardian approval at any checkpoint results in **IMMEDIATE CONSTRUCTION TERMINATION**.

---

## PHASE 0: WORKFLOW DEFINITION & CONSTITUTIONAL COMPLIANCE

### Construction Steps
1. Define workflow purpose and scope
2. Identify core data entity (source table)
3. Map initial data flow (producer-consumer relationships)
4. Establish V2/V3 naming convention: `WFx_V[N]_L[Layer]_[Seq]of[Total]_[DescriptiveName].py`

### ✓ CHECKPOINT 0: CONSTITUTIONAL VERIFICATION
**MANDATORY ACTIONS:**
- ☐ Load ScraperSky Development Constitution
- ☐ Load all 7 Layer Blueprints from `Docs/Docs_10_Final_Audit/`
- ☐ Acknowledge V2/V3 naming convention (underscores for Python)
- ☐ Confirm workflow alignment with business needs

**KILL SWITCH:** Cannot proceed without constitutional knowledge loaded  
**APPROVAL REQUIRED:** Constitutional compliance confirmed  
**PROCEED TO PHASE 1:** ☐ APPROVED

---

## PHASE 1: DATA MODEL FOUNDATION (LAYER 1)

### Construction Steps
1. Design/verify core SQLAlchemy models
2. Define columns, types, relationships
3. Ensure UUID primary keys
4. Implement proper ENUMs
5. Follow snake_case naming

### ✓ CHECKPOINT 1: L1 DATA SENTINEL APPROVAL
**MANDATORY CONSULTATION:** L1 Data Sentinel  
**BLUEPRINT:** `Docs/Docs_10_Final_Audit/v_Layer-1.1-Models_Enums_Blueprint.md`

**VERIFICATION:**
- ☐ UUID primary key implementation
- ☐ Snake_case naming compliance
- ☐ BaseModel inheritance verified
- ☐ Relationship patterns comply with standards
- ☐ ENUMs properly defined

**DELIVERABLE:** `src/models/WFx_V[N]_L1_[Seq]of[Total]_[ModelName].py`

**KILL SWITCH:** No model creation without L1 approval  
**L1 APPROVAL:** ☐ APPROVED ☐ REJECTED  
**PROCEED TO PHASE 2:** ☐ APPROVED

---

## PHASE 2: SCHEMA DEFINITION (LAYER 2)

### Construction Steps
1. Design Pydantic request/response schemas
2. Define strict validation rules
3. Ensure `from_attributes = True` for responses
4. Add field descriptions for OpenAPI
5. Extract schemas to dedicated files (NO inline)

### ✓ CHECKPOINT 2: L2 SCHEMA GUARDIAN APPROVAL
**MANDATORY CONSULTATION:** L2 Schema Guardian  
**BLUEPRINT:** `Docs/Docs_10_Final_Audit/v_Layer-2.1-Schemas_Blueprint.md`

**VERIFICATION:**
- ☐ Workflow-centric naming pattern
- ☐ Pydantic BaseModel inheritance
- ☐ ConfigDict(from_attributes=True) for responses
- ☐ NO inline schemas in routers
- ☐ Field descriptions present

**DELIVERABLE:** `src/schemas/WFx_V[N]_L2_[Seq]of[Total]_[SchemaName].py`

**KILL SWITCH:** No schema creation without L2 approval  
**L2 APPROVAL:** ☐ APPROVED ☐ REJECTED  
**PROCEED TO PHASE 3:** ☐ APPROVED

---

## PHASE 3: ROUTER IMPLEMENTATION (LAYER 3)

### Construction Steps
1. Create API endpoints with `/api/v3/` prefix
2. Implement transaction ownership: `async with session.begin():`
3. Apply Dual-Status Update Pattern
4. Integrate authentication dependencies
5. Import schemas from Layer 2 files

### ✓ CHECKPOINT 3: L3 ROUTER GUARDIAN APPROVAL
**MANDATORY CONSULTATION:** L3 Router Guardian  
**BLUEPRINT:** `Docs/Docs_10_Final_Audit/v_Layer-3.1-Routers_Blueprint.md`

**VERIFICATION:**
- ☐ `/api/v3/` prefix compliance
- ☐ Transaction ownership pattern
- ☐ Dual-Status Update Pattern
- ☐ Authentication dependency: `user: User = Depends(verify_token)`
- ☐ Schemas imported from Layer 2

**DELIVERABLE:** `src/routers/v3/WFx_V[N]_L3_[Seq]of[Total]_[RouterName].py`

**KILL SWITCH:** No router creation without L3 approval  
**L3 APPROVAL:** ☐ APPROVED ☐ REJECTED  
**PROCEED TO PHASE 4:** ☐ APPROVED

---

## PHASE 4: SERVICE & SCHEDULER IMPLEMENTATION (LAYER 4)

### Construction Steps
1. Implement stateless business logic services
2. Services accept AsyncSession parameters
3. Implement `run_job_loop` SDK pattern for schedulers
4. Configure batch processing parameters
5. Add comprehensive error handling

### ✓ CHECKPOINT 4: L4 ARBITER APPROVAL
**MANDATORY CONSULTATION:** L4 Arbiter  
**BLUEPRINT:** `Docs/Docs_10_Final_Audit/v_Layer-4.1-Services_Blueprint.md`

**VERIFICATION:**
- ☐ Services accept session (never create)
- ☐ Stateless service design
- ☐ `run_job_loop` pattern for schedulers
- ☐ Proper settings import: `from ..config.settings import settings`
- ☐ Error handling and logging

**DELIVERABLES:**
- `src/services/WFx_V[N]_L4_1of2_[ServiceName].py`
- `src/services/WFx_V[N]_L4_2of2_[SchedulerName].py`

**KILL SWITCH:** No service creation without L4 approval  
**L4 APPROVAL:** ☐ APPROVED ☐ REJECTED  
**PROCEED TO PHASE 5:** ☐ APPROVED

---

## PHASE 5: CONFIGURATION & INTEGRATION (LAYER 5)

### Construction Steps
1. Define environment variables in settings.py
2. Add router to main.py with correct prefix
3. Register scheduler in lifespan events
4. Configure intervals and batch sizes
5. Verify import paths

### ✓ CHECKPOINT 5: L5 CONFIG CONDUCTOR APPROVAL
**MANDATORY CONSULTATION:** L5 Config Conductor  
**BLUEPRINT:** `Docs/Docs_10_Final_Audit/v_Layer-5.1-Configuration_Blueprint.md`

**VERIFICATION:**
- ☐ Settings variables properly defined
- ☐ Environment variables externalized
- ☐ Router integration pattern correct
- ☐ Scheduler registered in lifespan
- ☐ Import paths verified

**DELIVERABLES:**
- Updated `src/config/settings.py`
- Updated `src/main.py`

**KILL SWITCH:** No integration without L5 approval  
**L5 APPROVAL:** ☐ APPROVED ☐ REJECTED  
**PROCEED TO PHASE 6:** ☐ APPROVED

---

## PHASE 6: UI COMPONENTS (LAYER 6)

### Construction Steps
1. Design semantic HTML structure
2. Organize external CSS/JS files
3. Integrate with V3 API endpoints
4. Ensure accessibility compliance
5. Implement responsive design

### ✓ CHECKPOINT 6: L6 UI VIRTUOSO APPROVAL
**MANDATORY CONSULTATION:** L6 UI Virtuoso  
**BLUEPRINT:** `Docs/Docs_10_Final_Audit/v_Layer-6.1-UI_Components_Blueprint.md`

**VERIFICATION:**
- ☐ Semantic HTML structure
- ☐ External file organization
- ☐ V3 API integration
- ☐ Accessibility standards
- ☐ User experience optimized

**DELIVERABLES:** UI components in `static/` directory

**KILL SWITCH:** No UI deployment without L6 approval  
**L6 APPROVAL:** ☐ APPROVED ☐ REJECTED  
**PROCEED TO PHASE 7:** ☐ APPROVED

---

## PHASE 7: TESTING & VALIDATION (LAYER 7)

### Construction Steps
1. Execute Docker-first testing
2. Perform Six-Tier Validation:
   - Server startup
   - Model imports
   - DB connection
   - Record creation
   - Service integration
   - End-to-end API proof
3. Write comprehensive test coverage
4. Document test results

### ✓ CHECKPOINT 7: L7 TEST SENTINEL APPROVAL
**MANDATORY CONSULTATION:** L7 Test Sentinel  
**BLUEPRINT:** `Docs/Docs_10_Final_Audit/v_Layer-7.1-Testing_Blueprint.md`

**VERIFICATION:**
- ☐ Docker-first approach confirmed
- ☐ Six-Tier Validation passed
- ☐ Test coverage adequate
- ☐ Environment-aware testing
- ☐ Production readiness confirmed

**DELIVERABLES:** Test files and validation reports

**KILL SWITCH:** No production deployment without L7 approval  
**L7 APPROVAL:** ☐ APPROVED ☐ REJECTED  
**PROCEED TO PHASE 8:** ☐ APPROVED

---

## PHASE 8: DOCUMENTATION & ARCHIVAL (LAYER 0)

### Construction Steps
1. Create workflow truth document
2. Archive historical records
3. Update relevant blueprints
4. Document lessons learned
5. Version control confirmation

### ✓ CHECKPOINT 8: FINAL CONSTRUCTION APPROVAL
**MANDATORY VERIFICATION:**
- ☐ ALL 7 Layer Guardian approvals obtained
- ☐ V2/V3 naming convention compliance
- ☐ End-to-end testing completed
- ☐ Zero architectural violations
- ☐ Documentation complete

**FINAL APPROVAL:** ☐ APPROVED ☐ REJECTED  
**CONSTRUCTION COMPLETE:** _______________

---

<!-- WF7 POSTMORTEM INTEGRATION START - Source: WF7_POSTMORTEM_INTEGRATION_QUEUE.md -->
## MANDATORY ENFORCEMENT GATES

### Pre-Phase Verification
Before ANY phase can begin:
1. **Load Companion:** Read Layer Pattern/AntiPattern Companion
2. **Verify Understanding:** List 3 patterns, 3 anti-patterns
3. **Check STOP Signs:** Confirm no violations pending
4. **Get Approval:** Layer Guardian must approve

### Verification Code Required
```python
# MANDATORY: Prove companion was loaded
assert "companion_loaded" in session_history
assert guardian_approval.is_valid()
assert stop_signs.check() == "CLEAR"
```

### Cannot Proceed Without:
- [ ] Companion consultation verified
- [ ] Guardian approval obtained
- [ ] STOP signs checked
- [ ] Previous phase complete
<!-- WF7 POSTMORTEM INTEGRATION END -->

## ENFORCEMENT PROTOCOLS

### AI Partner Requirements
1. **NO PHASE SKIPPING** - Must complete phases sequentially
2. **NO CODING WITHOUT APPROVAL** - Each checkpoint must pass
3. **KILL SWITCH COMPLIANCE** - Stop immediately when triggered
4. **DOCUMENTATION MANDATORY** - Record all decisions and approvals

### Violation Consequences
- **First Violation:** Construction halt, constitutional review
- **Second Violation:** Permanent construction ban
- **Critical Violation:** Immediate termination

---

## RAPID REFERENCE: V2→V3 MIGRATION

For V2 to V3 compliance updates:
1. Extract inline schemas → Layer 2 files
2. Update router prefix → `/api/v3/`
3. Add authentication dependency
4. Maintain dual existence (keep V2 active)
5. Verify via health checks

---

**THIS PROTOCOL IS SUPREME LAW FOR ALL WORKFLOW CONSTRUCTION**

**Authority:** ScraperSky Development Constitution  
**Enforcement:** The Architect with Layer Guardian consensus