# ScraperSky Master Navigation and Diagnosis System

**Version:** 2.1
**Owner:** The Architect
**Last Updated:** 2025-08-17 (WF7 Postmortem Integration)
**Purpose:** Single entry point for all navigation and diagnostic needs. Merges wayfinding with symptom diagnosis for rapid architectural response.

---

## PART A: NAVIGATION HIERARCHY

### 🚨 EMERGENCY RESPONSE
**System is broken, tests failing, server won't start**

1. **IMMEDIATE:** Check → `01_STOP_SIGNS_CRITICAL_OPERATIONS.md`
2. **RECOVERY:** Follow → `Docs/EMERGENCY_PROCEDURES/WF7_Recovery_Playbook.md`
3. **ROLLBACK:** Execute → `Docs/EMERGENCY_PROCEDURES/Rollback_Procedures.md`
4. **DEEP DIVE:** Investigate → `Docs/Docs_35_WF7-The_Extractor/`

### 📚 LEARNING PATH
**New to system or specific layer**

1. **START HERE:** `Docs/START_HERE_AI_ASSISTANT.md`
2. **THE LAW:** `Docs/00_Constitution/`
   - ScraperSky_Development_Constitution.md (Supreme Law)
   - 0-Guardian_paradox_complete_story.md (The 'Why')
3. **THE GUARDIANS:** `Docs/Docs_10_Final_Audit/v_Layer-*.md`
   - Layer 1-8 Blueprints
4. **THE PATTERNS:** `personas_layers/L*_Pattern_AntiPattern_Companion.md`

### 🔨 BUILDING FEATURES
**Creating or modifying code**

1. **TRIGGER DISCOVERY:** Scan first → `09_BUILDING_BLOCKS_MENU.yaml` (AI-optimized pattern discovery)
2. **PATTERNS:** Review → `03_ARCHITECTURAL_PATTERNS_LIBRARY.md`
   - **Deep Dive:** `07_PATTERN_CATALOG_WF7_SYNTHESIS.md` (47 patterns)
   - **Avoid:** `08_ANTIPATTERN_CATALOG_WF7_SYNTHESIS.md` (47 anti-patterns)
   - **Implementations:** `09_BUILDING_BLOCKS_CATALOG.md` (battle-tested code patterns)
3. **CONSTRUCTION:** Follow → `02_CONSTRUCTION_PROTOCOL.md` 
4. **OPERATIONS:** Execute → `04_GOLDEN_THREAD_OPERATIONAL_PLAYBOOK.md`
5. **TESTING:** Validate → `Docs/Docs_10_Final_Audit/v_Layer-7.1-Testing_Blueprint.md`

### 🛑 VERIFICATION GATES
**Before critical operations**

1. **STOP SIGNS:** `01_STOP_SIGNS_CRITICAL_OPERATIONS.md`
2. **SYMPTOM DIAGNOSIS:** See Part B below
3. **QUICK COMMANDS:** See Part C below

---

## PART B: SYMPTOM-TO-SOLUTION DIAGNOSIS

| Symptom | Root Cause | Primary Resource | Secondary Resource |
|---------|------------|------------------|-------------------|
| **`ModuleNotFoundError` / `ImportError`** | Circular dependencies, path violations, layer boundary breach. **THE WF7 CRISIS** | `Docs/Docs_35_WF7-The_Extractor/21_WF7_Anti_Patterns_Catalog.md` | `personas_layers/L3_Router_Guardian_Pattern_AntiPattern_Companion_v2.0.md` |
| **Database startup error** | Code/DB schema mismatch. Model changed without migration. **GUARDIAN'S PARADOX** | `Docs/00_Constitution/0-Guardian_paradox_complete_story.md` | `01_STOP_SIGNS_CRITICAL_OPERATIONS.md` |
| **"Docs perfect but not working"** | Documentation idealism vs reality. **THE GREAT REVISION LIE** | `Docs/Docs_35_WF7-The_Extractor/20_The_Great_Revision_Lie.md` | This document |
| **Tests: `401 Unauthorized`** | Missing auth dependency or test client misconfiguration | `personas_layers/L7_Test_Sentinel_Pattern_AntiPattern_Companion.md` | `personas_layers/L3_Router_Guardian_Pattern_AntiPattern_Companion_v2.0.md` |
| **`pydantic.ValidationError`** | Request/schema mismatch | `personas_layers/L2_Schema_Guardian_Pattern_AntiPattern_Companion_v2.0.md` | `Docs/Docs_10_Final_Audit/v_Layer-2.1-Schemas_Blueprint.md` |
| **`AttributeError` on model/service** | Missing property or layer violation | `personas_layers/L4_Service_Guardian_Pattern_AntiPattern_Companion.md` | `Docs/Docs_10_Final_Audit/v_Layer-4.1-Services_Blueprint.md` |
| **File naming confusion** | V7 naming convention violation | `03_ARCHITECTURAL_PATTERNS_LIBRARY.md` | `Docs/02_State_of_the_Nation/WO_004_V7_Migration_Readiness.md` |
| **Task feels risky** | Scope creep danger. **PARADOX TRIGGER** | `01_STOP_SIGNS_CRITICAL_OPERATIONS.md` | `Docs/00_Constitution/0-Guardian_paradox_complete_story.md` |
| **Config values `None`** | Environment variable loading failure | `personas_layers/L5_Config_Conductor_Pattern_AntiPattern_Companion.md` | `Docs/Docs_10_Final_Audit/v_Layer-5.1-Configuration_Blueprint.md` |
| **UI components not rendering** | Static path or component structure violation | `personas_layers/L6_UI_Virtuoso_Pattern_AntiPattern_Companion.md` | `Docs/Docs_10_Final_Audit/v_Layer-6.1-UI_Components_Blueprint.md` |
| **Server starts but endpoints 404** | Router inclusion pattern violation | `02_CONSTRUCTION_PROTOCOL.md` | `personas_layers/L3_Router_Guardian_Pattern_AntiPattern_Companion_v2.0.md` |
| **Async session errors** | Transaction ownership violation | `03_ARCHITECTURAL_PATTERNS_LIBRARY.md` | `personas_layers/L4_Service_Guardian_Pattern_AntiPattern_Companion.md` |
| **Scheduler won't start** | Missing scheduler instance or config | `personas_layers/L5_Config_Conductor_Pattern_AntiPattern_Companion.md` | `CLAUDE.md` |
<!-- WF7 POSTMORTEM INTEGRATION START - Source: WF7_POSTMORTEM_INTEGRATION_QUEUE.md -->
| **"Perfect docs but ignored"** | 96% pattern coverage with 15% effectiveness. **ENFORCEMENT GAP** | `START_HERE_ARCHITECT_PROTOCOL.md` | `02_CONSTRUCTION_PROTOCOL.md` |
| **88+ uncommitted files** | Analysis paralysis from over-documentation | Commit immediately | `04_GOLDEN_THREAD_OPERATIONAL_PLAYBOOK.md` |
| **"Compliance claimed"** | Compliance theater without verification | Require evidence | `01_STOP_SIGNS_CRITICAL_OPERATIONS.md` #7 |
<!-- WF7 POSTMORTEM INTEGRATION END -->

---

<!-- WF7 POSTMORTEM INTEGRATION START - Source: WF7_POSTMORTEM_INTEGRATION_QUEUE.md -->
## ⚠️ CRITICAL SYSTEM METRICS

**Pattern Coverage vs Effectiveness Gap:**
- Documentation Coverage: 96%
- Actual Effectiveness: 15%  
- **Gap: 81% (ENFORCEMENT MISSING)**

**V7 Migration Reality:**
- Files needing rename: 87
- Current compliance: 0%
- Framework readiness: 30%
<!-- WF7 POSTMORTEM INTEGRATION END -->

## PART C: QUICK COMMAND REFERENCE

### Health Verification
```bash
# Basic health check
curl -f http://localhost:8000/health

# Database health
curl http://localhost:8000/health/database

# Debug routes (requires FASTAPI_DEBUG_MODE=true)
curl http://localhost:8000/debug/routes | jq .
curl http://localhost:8000/debug/loaded-src-files | jq .
```

### Docker Operations
```bash
# Start with build
docker compose up --build

# View logs
docker compose logs -f app

# Restart service
docker compose restart app

# Full teardown
docker compose down
```

### Import Verification
```bash
# Test specific import
python -c "from src.models.domain import Domain"

# Test schema import
python -c "from src.schemas.WF7_V3_L2_1of1_PageCurationSchemas import PageCurationBatchStatusUpdateRequest"

# Check V3 endpoints
curl http://localhost:8000/openapi.json | jq '.paths | keys[] | select(startswith("/api/v3/"))'
```

### File System Audit
```bash
# Check for orphaned files
python tools/file_discovery.py

# Verify naming convention
ls src/**/*.py | grep -v "WF[0-9]_V[0-9]_L[0-9]_"
```

---

## CRITICAL DECISION FLOWCHARTS

### Flowchart 1: Starting Any Task

```
[START]
  ↓
Is this code modification? → [NO] → Follow literally → [END]
  ↓ [YES]
Which layer (L1-L7)?
  ↓
Read Layer Blueprint
  ↓
Check 01_STOP_SIGNS → [STOP SIGN?] → Get approval → [END]
  ↓ [NO]
Follow 02_CONSTRUCTION_PROTOCOL
  ↓
Apply 03_PATTERNS_LIBRARY
  ↓
Test via L7 Blueprint
  ↓
[END]
```

### Flowchart 2: Import Error Response

```
[START]
  ↓
STOP ALL MODIFICATIONS
  ↓
Read WF7 Anti-Patterns Catalog
  ↓
Circular import? → [YES] → Check L3/L5 Companions
  ↓ [NO]
Simple path fix? → [YES] → Fix → Test ALL → [END]
  ↓ [NO]
ESCALATE to L3 Router Guardian
  ↓
[END]
```

---

**Authority:** Second only to the Constitution. This document supersedes all previous navigation and symptom mapping documentation.