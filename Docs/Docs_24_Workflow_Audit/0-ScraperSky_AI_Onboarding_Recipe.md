# ScraperSky AI Onboarding Recipe

## Rapid Context Loading for Technical Debt Remediation

**Purpose**: This document provides a systematic way for AI instances to rapidly acquire the essential context needed to work on ScraperSky's technical debt remediation efforts, specifically the workflow pipeline fixes (WF1-WF6).

---

## Phase 1: System Architecture Foundation (5 minutes)

### 1.1 Core Identity and Mission

**Read these files immediately (in order):**

```bash
# Universal System Principles
cat "Docs/Docs_21_SeptaGram_Personas/common_knowledge_base.md"

# AI Framework Architecture
cat "Docs/Docs_21_SeptaGram_Personas/blueprint-zero-persona-framework.md"

# Architectural Truth Document
cat "Docs/Docs_6_Architecture_and_Status/archive-dont-vector/v_1.0-ARCH-TRUTH-Definitive_Reference.md"

# Guardian Remediation Protocol
cat "Docs/Docs_21_SeptaGram_Personas/layer_guardian_remediation_protocol.md"
```

### 1.2 Rapid Context Queries

**⚠️ CRITICAL: If you're reading this, you DO have terminal access and semantic search tools in your toolset! Don't hesitate - execute these vector searches immediately to internalize key concepts:**

```bash
# System Architecture Overview
python3 Docs/Docs_18_Vector_Operations/Scripts/semantic_query_cli.py "ScraperSky 7-layer architecture Guardian AI system L0-L7 BaseModel inheritance patterns"

# Current Crisis Context
python3 Docs/Docs_18_Vector_Operations/Scripts/semantic_query_cli.py "Guardian AI remediation 96 files technical debt ENUM centralization BaseModel inheritance broken workflows"

# Workflow Pipeline Overview
python3 Docs/Docs_18_Vector_Operations/Scripts/semantic_query_cli.py "WF1 WF2 WF3 WF4 WF5 WF6 workflow pipeline producer consumer data enrichment handoffs"
```

---

## Phase 2: Current Crisis Understanding (3 minutes)

### 2.1 The Big Picture Problem

**Key Insight**: A massive Guardian AI remediation effort (96 files changed) enforced architectural blueprints but left the entire data enrichment pipeline broken due to incomplete implementation.

**Read the assessment and plan:**

```bash
# Direct Feedback on Crisis Scope
cat "Docs/Docs_24_Workflow_Audit/DirectFeedBack.md"

# Strategic Remediation Plan
cat "Docs/Docs_24_Workflow_Audit/Plan.md"

# Foundation Work (Critical)
cat "Docs/Docs_24_Workflow_Audit/Remediation Work Orders/Phase0-Foundational-Remediation.md"
```

### 2.2 Current Status Check

**Execute this to see what's been changed:**

```bash
# See the scope of changes
git diff HEAD~1 --name-only | grep -v -E "(chat|transcript|conversation|\.log|debug)" > current_changes_files.txt
echo "=== FILES CHANGED ===" && cat current_changes_files.txt
echo "=== SUMMARY STATS ===" && git diff HEAD~1 --stat $(cat current_changes_files.txt | tr '\n' ' ')
```

---

## Phase 3: Technical Pattern Recognition (2 minutes)

### 3.1 Core Architectural Patterns

**Vector searches for critical patterns:**

```bash
# BaseModel Inheritance Pattern (CRITICAL)
python3 Docs/Docs_18_Vector_Operations/Scripts/semantic_query_cli.py "BaseModel inheritance Base SQLAlchemy declarative inheritance pattern models"

# ENUM Centralization Pattern (CRITICAL)
python3 Docs/Docs_18_Vector_Operations/Scripts/semantic_query_cli.py "ENUM centralization src/models/enums.py status values string hardcoded"

# Producer-Consumer Chain Pattern (CRITICAL)
python3 Docs/Docs_18_Vector_Operations/Scripts/semantic_query_cli.py "producer consumer chain workflow handoff status QUEUED SELECTED trigger"
```

### 3.2 Known Issue Patterns

**Understanding the systematic problems:**

```bash
# Circular Dependency Pattern
python3 Docs/Docs_18_Vector_Operations/Scripts/semantic_query_cli.py "circular dependency BaseModel Base inheritance SQLAlchemy mapper failed to locate name"

# Schema Migration Pattern
python3 Docs/Docs_18_Vector_Operations/Scripts/semantic_query_cli.py "api_models.py src/schemas migration pydantic request response schema centralization"

# Status Mismatch Pattern
python3 Docs/Docs_18_Vector_Operations/Scripts/semantic_query_cli.py "status ENUM mismatch hardcoded string Selected QUEUED trigger workflow handoff"
```

---

## Phase 4: Work Order Context (Specific to Current Task)

### 4.1 If Working on Phase 0 (Foundation)

```bash
# Phase 0 Deep Dive
cat "Docs/Docs_24_Workflow_Audit/Remediation Work Orders/Phase0-Foundational-Remediation.md"

# Model Inheritance Fixes
python3 Docs/Docs_18_Vector_Operations/Scripts/semantic_query_cli.py "BaseModel inheritance only Base SQLAlchemy models Domain LocalBusiness Place Page SitemapFile"

# Test Current Status
pytest tests/routers/test_google_maps_api.py::test_search_places_success -vv -s
```

### 4.2 If Working on WF1 (Single Search Discovery)

```bash
# WF1 Specific Context
cat "Docs/Docs_24_Workflow_Audit/Remediation Work Orders/WF1-Remediation-Workflow.md"

# WF1 Technical Deep Dive
python3 Docs/Docs_18_Vector_Operations/Scripts/semantic_query_cli.py "WF1 Single Search Discovery Google Maps API PlaceSearch status handling SearchStatus"
```

### 4.3 If Working on WF2-WF6 (Choose Your Workflow)

```bash
# WF2: Staging Editor
python3 Docs/Docs_18_Vector_Operations/Scripts/semantic_query_cli.py "WF2 Staging Editor PlaceStatus deep scan curation staging places"

# WF3: Local Business Curation
python3 Docs/Docs_18_Vector_Operations/Scripts/semantic_query_cli.py "WF3 Local Business Curation domain extraction PlaceStatus DomainExtractionStatus"

# WF4: Domain Curation
python3 Docs/Docs_18_Vector_Operations/Scripts/semantic_query_cli.py "WF4 Domain Curation sitemap analysis SitemapCurationStatus SitemapAnalysisStatus"

# WF5: Sitemap Curation
python3 Docs/Docs_18_Vector_Operations/Scripts/semantic_query_cli.py "WF5 Sitemap Curation sitemap import SitemapDeepCurationStatus SitemapImportProcessStatus"

# WF6: Sitemap Import
python3 Docs/Docs_18_Vector_Operations/Scripts/semantic_query_cli.py "WF6 Sitemap Import pages generation PageStatus sitemap processing"
```

---

## Phase 5: Tools and Testing Setup (1 minute)

### 5.1 Essential Tools

```bash
# Supabase Project ID (for database operations)
PROJECT_ID="ddfldwzhdhhzhxywqnyz"

# Key Testing Commands
alias test-google-api="pytest tests/routers/test_google_maps_api.py::test_search_places_success -vv -s"
alias check-models="python -c 'from src.models import *; print(\"Models imported successfully\")'"

# Vector Search Helper
alias search-context="python3 Docs/Docs_18_Vector_Operations/Scripts/semantic_query_cli.py"
```

### 5.2 Rapid Diagnostic Commands

```bash
# Check current SQLAlchemy mapper status
python -c "
from src.models import Domain, LocalBusiness, Place, Page, SitemapFile
print('✅ All models imported successfully')
print('✅ SQLAlchemy mappers working')
"

# Check ENUM centralization status
python -c "
from src.models.enums import PlaceStatus, SitemapCurationStatus, DomainExtractionStatus
print('✅ ENUMs centralized correctly')
"
```

---

## Phase 6: Success Criteria and Next Steps

### 6.1 Phase Completion Checkpoints

**Phase 0 Complete When:**

- [ ] All models inherit from `(Base, BaseModel)` correctly
- [ ] SQLAlchemy mapper errors resolved
- [ ] Google Maps API test passes: `pytest tests/routers/test_google_maps_api.py::test_search_places_success -vv -s`
- [ ] All ENUMs centralized in `src/models/enums.py`
- [ ] All schemas migrated from `api_models.py` to `src/schemas/`

**WF1-WF6 Complete When:**

- [ ] Producer-consumer chains reconnected
- [ ] Status triggers use centralized ENUMs (not hardcoded strings)
- [ ] Dedicated service/scheduler components created
- [ ] Background task processing functional
- [ ] End-to-end workflow tests passing

### 6.2 Emergency Diagnostic Playbook

**If SQLAlchemy Mapper Errors:**

```bash
# Check inheritance patterns
grep -r "class.*BaseModel.*:" src/models/
# Should show: class ModelName(Base, BaseModel):

# Check for circular imports
grep -r "from.*models.*import" src/models/ | grep -v "__init__"
```

**If ENUM Errors:**

```bash
# Check ENUM centralization
find src/ -name "*.py" -exec grep -l "class.*Enum" {} \;
# Should only show: src/models/enums.py

# Check hardcoded strings
grep -r "== ['\"]Selected['\"]" src/
grep -r "== ['\"]Queued['\"]" src/
```

**If Workflow Handoff Broken:**

```bash
# Check status trigger patterns
grep -r "\.SELECTED" src/
grep -r "\.QUEUED" src/
# Should use ENUM members, not hardcoded strings
```

---

## Phase 7: Context Retention and Handoff

### 7.1 Document Your Progress

**When completing work, always update:**

```bash
# Current progress tracking
echo "Phase X completed: $(date)" >> workflow_progress.log
echo "Key changes: [brief description]" >> workflow_progress.log

# Generate change summary for next AI
git diff HEAD~1 --name-only > recent_changes.txt
git diff HEAD~1 --stat > change_stats.txt
```

### 7.2 Handoff to Next AI Instance

**If handing off to another AI, provide:**

1. **Current Phase Status**: "Completed Phase 0, starting WF2"
2. **Key Context**: "BaseModel inheritance fixed, Google API test passing"
3. **Next Steps**: "Follow WF2 work order, focus on staging editor schema migration"
4. **Critical Files**: List the 3-5 most important files for the next phase

---

## Emergency Contact Information

**If Completely Lost:**

1. **Re-read this recipe from the beginning**
2. **Run the Phase 1 vector searches again**
3. **Check the DirectFeedBack.md for the big picture**
4. **Look at current git changes: `git status` and `git diff`**

**If Stuck on Technical Issues:**

1. **Search the knowledge base**: `search-context "your specific error message"`
2. **Check the Phase0 remediation document for systematic patterns**
3. **Look for similar patterns in completed work orders**

**Remember**: This is systematic technical debt remediation. The problems are predictable and the solutions follow consistent patterns. Trust the architectural blueprints and Guardian AI principles.

---

**Total Onboarding Time: ~15 minutes**
**Result**: Fully contextualized AI ready to execute specific work orders efficiently.
