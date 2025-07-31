# 🚁 WORK ORDER: WF4 Database Connection Timeout Fix

**Flight Classification:** 🚁 Medical/Emergency Aircraft  
**Priority:** CRITICAL - Workflow Breaking  
**Flight Number:** [DART Task ID Required - https://app.dartai.com/d/R7iF0839HTgV-WF4-Domain-Curation-Guardian]  
**Filed Date:** 2025-07-30  
**Air Traffic Controller:** The Fifth Beatle  
**Assigned Pilot:** WF4 Domain Curation Guardian  

---

## 🎯 FLIGHT PLAN SUMMARY

**Departure Status:** WF4 Domain Curation completely broken - users select domains, click "Sibi" button, nothing happens  
**Destination:** Fully functional WF4 with proper session management following documented patterns  
**Aircraft Type:** Emergency repair of critical business workflow  
**Fuel Requirements:** 4-6 hours (analysis, implementation, testing, documentation)  

---

## 🚨 EMERGENCY SITUATION

### Critical Business Impact
- **User-Facing Failure:** Domain selection UI appears to work but silently fails
- **Workflow Handoff Broken:** WF4→WF5 pipeline completely stalled  
- **Silent Failures:** No error feedback to users, appears functional but isn't
- **Production Impact:** Core business process down

### Technical Root Cause
**Anti-Pattern Violation:** Database connections held open during slow external API calls (ScraperAPI 2-3 seconds each), causing `asyncpg.exceptions.ConnectionDoesNotExistError`

**File:** `src/services/domain_scheduler.py`  
**Function:** `process_pending_domains`  
**Pattern Violated:** Session management best practices documented in `07-51-BATCH-PROCESSOR-SESSION-STANDARDIZATION-WORK-ORDER.md`

---

## 📋 FLIGHT MANIFEST (DELIVERABLES)

### 1. **Code Fix Implementation**
- [ ] Refactor `process_pending_domains` to use 3-phase pattern:
  - Phase 1: Quick DB transaction to fetch and mark domains as 'processing'
  - Phase 2: Release connection, perform metadata extraction without DB connections
  - Phase 3: New quick transaction to update final results
- [ ] Follow documented session management patterns from Layer 5 audit

### 2. **Anti-Pattern Prevention**
- [ ] Add warning comments to `domain_scheduler.py` referencing AP-20250730-002
- [ ] Update WF4 Guardian document with session management constraints
- [ ] Create code review checklist item for session+external_api patterns

### 3. **Testing & Validation**
- [ ] Test domain selection → processing → completion flow
- [ ] Verify WF4→WF5 handoff works (domains get queued for sitemap analysis)
- [ ] Confirm no connection timeout errors in logs
- [ ] Validate user feedback shows processing status

### 4. **Documentation Updates**
- [ ] Update WF4 Guardian with session management lessons learned
- [ ] Document the specific fix pattern for future reference
- [ ] Add to critical patterns documentation

---

## 🛠️ TECHNICAL SPECIFICATIONS

### Current Broken Pattern
```python
async with get_background_session() as session:
    # Get domains
    # HOLD CONNECTION DURING SLOW API CALLS (2-3 seconds each)
    metadata = await scraper_api.extract(url)  # CONNECTION TIMES OUT HERE
    # Try to update database <- FAILS
```

### Required Fixed Pattern  
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

## 📚 REFERENCE DOCUMENTATION

### External Documentation Consulted
- **SQLAlchemy Docs:** `Docs_Context7/Core_Framework/SQLAlchemy_Documentation.md`
  - Line 11: "connection pooling, and query optimization"
  - Line 178: "Use connection pooling"
- **Supabase Docs:** `Docs_Context7/Core_Framework/Supabase_Documentation.md`  
  - Line 414: "Use Supavisor for connection pooling in production"

### Internal Documentation Authority
- **Session Management Rules:** `07-51-BATCH-PROCESSOR-SESSION-STANDARDIZATION-WORK-ORDER.md`
- **WF4 Business Logic:** `v_Method_01_Guardian_WF4_Perfect_Truth_2025-07-27.md`
- **Anti-Pattern Registry:** `AP-20250730-002` - Database Connection Long Hold

### Key Finding
External docs emphasize connection pooling efficiency but don't warn against holding connections during long operations. Our homegrown documentation identified this critical gap.

---

## 🎭 CONTROL TOWER NOTES

### Air Traffic Control Decision
**Classification Rationale:** Emergency aircraft due to complete workflow failure affecting user-facing operations. This is not routine maintenance but critical system repair.

### Weather Conditions
- **Business Priority:** HIGH - Core domain curation workflow down
- **Technical Complexity:** MEDIUM - Well-documented pattern to follow
- **Risk Level:** LOW - Fix follows established patterns with clear precedent

### Flight Crew Assignment
**Primary Pilot:** WF4 Domain Curation Guardian (owns this workflow)  
**Required Consultation:** Session Management Documentation, Layer 5 Audit Team  
**Backup Support:** Architecture team for pattern validation

---

## 🛬 LANDING PROCEDURES

### Success Criteria
1. Users can select domains and see them process successfully
2. WF4→WF5 handoff works (domains appear in sitemap analysis queue)
3. No connection timeout errors in domain_scheduler logs
4. Anti-pattern prevention measures in place

### Post-Flight Report Requirements
- [ ] Confirmation of fix implementation
- [ ] Test results showing successful domain processing
- [ ] Updated documentation reflecting lessons learned
- [ ] Prevention measures documented for future AI partners

---

**Emergency Clearance:** GRANTED - Proceed immediately to implementation phase  
**Control Tower Signature:** The Fifth Beatle - Air Traffic Controller  
**Flight Plan Status:** FILED AND APPROVED
