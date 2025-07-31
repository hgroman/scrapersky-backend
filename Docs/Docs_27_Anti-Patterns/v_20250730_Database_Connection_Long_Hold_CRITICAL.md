---
# Anti-Pattern Metadata
anti_pattern_id: "AP-20250730-002"
severity: "CRITICAL"
date_occurred: "2025-07-30"

# ScraperSky Architecture Location
workflow: "WF4"
layer: "LAYER4"  # Background Services
component: "domain_scheduler"
file_path: "src/services/domain_scheduler.py"

# Business Context
business_process: "Domain Curation"
affects_handoff: ["WF4->WF5"]
user_facing: true

# Technical Context  
technology_stack: ["SQLAlchemy", "AsyncPG", "APScheduler"]
pattern_type: "Session Management"
architectural_principle: "Connection Pooling"

# AI Assistant Context
requires_business_knowledge: true
requires_architecture_knowledge: true
danger_level: "WORKFLOW_BREAKING"
consultation_required: ["WF4_Guardian", "Session_Management_Docs"]

# Searchable Tags
tags: ["database", "connection_timeout", "external_api", "session_management", "pgbouncer", "supavisor"]
---

# 20250730_Database_Connection_Long_Hold_CRITICAL

**Anti-Pattern ID:** AP-20250730-002  
**Date Occurred:** July 30, 2025  
**Workflow Affected:** WF4 Domain Curation  
**Severity:** CRITICAL - Business Process Disruption  
**Classification:** Architectural Anti-Pattern  

---

## Anti-Pattern Summary

**Pattern Name:** Database Connection Long Hold During External API Calls  
**Category:** Session Management Violation  
**Risk Level:** CRITICAL  

**Description:** Holding database connections open during slow external API operations (ScraperAPI calls taking 2-3 seconds each), causing connection timeouts and silent workflow failures. This violates established session management patterns and breaks the WF4→WF5 handoff.

---

## Incident Details

### What Happened
- **Original Issue:** "ScraperAPI problems last week" led to experimental changes
- **Anti-Pattern:** Database session held open during slow ScraperAPI metadata extraction
- **Technical Failure:** `asyncpg.exceptions.ConnectionDoesNotExistError: connection was closed in the middle of operation`
- **Business Impact:** Users select domains, click "Sibi" button, nothing happens - complete WF4 failure

### Root Cause Analysis
1. **Documentation Ignored:** Existing session standardization rules (07-51-BATCH-PROCESSOR-SESSION-STANDARDIZATION) were not followed
2. **Experimental Changes:** Someone "experimented" without consulting established patterns
3. **No Enforcement:** Critical architectural patterns not enforced at code level
4. **Pattern Violation:** Single transaction holding connection during 2-3 second external API calls

### Cascade Effects
- **WF4 completely broken** - domain selections don't process
- **WF4→WF5 handoff broken** - domains never queued for sitemap analysis  
- **Silent failures** - no user feedback, appears to work but doesn't
- **Hours of debugging** to find buried documentation and root cause

---

## Detection Signals

### Technical Indicators
- ✋ **`ConnectionDoesNotExistError` in domain_scheduler logs**
- ✋ **Database sessions held open during ScraperAPI calls**
- ✋ **Single transaction spanning external API operations**
- ✋ **Domains stuck in 'processing' status**

### Business Indicators  
- ✋ **Users report "Sibi" button not working**
- ✋ **Domain selections don't trigger sitemap analysis**
- ✋ **WF4→WF5 pipeline stalled**

---

## The Correct Pattern

### ❌ WRONG (Anti-Pattern)
```python
async with get_background_session() as session:
    # Get domains
    # HOLD CONNECTION DURING SLOW API CALLS (2-3 seconds each)
    metadata = await scraper_api.extract(url)  # CONNECTION TIMES OUT HERE
    # Try to update database <- FAILS
```

### ✅ CORRECT (Documented Pattern)
```python
# Phase 1: Quick DB operation
async with get_background_session() as session:
    domains = fetch_and_mark_processing()

# Phase 2: Slow operations WITHOUT database connection  
for domain in domains:
    metadata = await scraper_api.extract(domain.url)  # NO CONNECTION HELD

# Phase 3: Quick DB operation
async with get_background_session() as session:
    update_final_results(domains_with_metadata)
```

---

## Prevention Measures

### Immediate
1. **Fix the violation** in `domain_scheduler.py`
2. **Add warning comments** about session management rules
3. **Document the pain** - this exact incident and cost

### Strategic  
1. **Move session rules** from buried docs to `CRITICAL_PATTERNS.md`
2. **Add linting rules** to detect session+external_api patterns
3. **Runtime warnings** for connections held >5 seconds
4. **Code review checklist** for session management patterns

---

## Reference Documentation
- **Session Management Rules:** `07-51-BATCH-PROCESSOR-SESSION-STANDARDIZATION-WORK-ORDER.md`
- **WF4 Business Logic:** `v_Method_01_Guardian_WF4_Perfect_Truth_2025-07-27.md`
- **Connection Pool Issues:** `77.9.0-Database-Session-Handling-Fixes.md`

---

## AI Assistant Integration

### Pre-Change Query Pattern
```yaml
workflow_context: "WF4"
layer_context: "LAYER4" 
change_type: "session_management"
involves_external_api: true
```

### Required Consultations
- WF4 Guardian document review
- Session management documentation
- Architecture layer compliance check

---

**Key Lesson:** Documentation without enforcement is just expensive wishes. Make the right way the only way.
