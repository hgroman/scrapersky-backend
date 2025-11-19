# Extraction Plan: Docs/01_Architectural_Guidance/

**Purpose:** Systematic audit of Docs/01_Architectural_Guidance/ against working code
**Method:** Apply AUDIT_METHODOLOGY.md - verify claims against WF7 production code
**Date:** Nov 16, 2025

---

## Executive Summary

**Directory Contents:** 23 files across 6 subdirectories
**Assessment Status:** Audited against WF7 production code (most modern workflow)
**Recommendation:** PARTIAL EXTRACTION - extract battle-tested patterns, archive governance framework

**Key Finding:** This directory contains a MIX of:
1. **✅ EXTRACT:** War stories documenting real production failures/fixes
2. **✅ EXTRACT:** Proven anti-patterns from actual code (Enum bug, Placeholder pattern)
3. **⚠️ REFERENCE:** Guardian/Architect governance framework (aspirational, not enforced in current code)
4. **📋 REFERENCE:** Operational commands and diagnostics (useful but duplicates CLAUDE.md)

---

## War Stories Directory - EXTRACTION REQUIRED

### File: war_stories/WAR_STORY__Enum_Implementation_Train_Wreck__2025-09-12.md

**Code Claims:**
1. SQLAlchemy needs `values_callable` parameter for proper enum serialization
2. Default behavior serializes enum by NAME not VALUE
3. PostgreSQL expects lowercase values, gets uppercase names → fails
4. Must use `SQLAlchemyEnum` with all mandatory parameters

**Verification Against WF7 Code:**
```bash
# Check current enum usage in production WF7:
grep -r "Enum\|PageProcessingStatus" src/models/enums.py src/models/page.py
```

**Status:** ✅ Accurate - Documents historical problem
**Current Reality:** WF7 uses proper enum configuration
**Value:** Explains WHY enum configuration matters

**Extraction Plan:**
- [ ] Add to CONTRIBUTING.md Anti-Patterns section:
  - Title: "SQLAlchemy Enum Serialization Bug"
  - Content: The .value requirement for SQLAlchemy queries
  - Example code from war story
  - Reference: `Docs/01_Architectural_Guidance/war_stories/WAR_STORY__Enum_Implementation_Train_Wreck__2025-09-12.md`

---

### File: war_stories/WAR_STORY__Placeholder_Driven_Development__2025-08-26.md

**Code Claims:**
1. WF7 was creating placeholder contacts for months (445 pages → 4 contacts)
2. Used fake emails: `placeholder@example.com`
3. Caused unique constraint violations
4. False success logging created illusion of functionality

**Verification Against Current WF7 Code:**
```python
# src/services/WF7_V2_L4_1of2_PageCurationService.py:74-95
real_emails = [email for email in emails if not any(fake in email.lower()
    for fake in ['noreply', 'donotreply', 'no-reply', 'example.com', 'test.com', 'dummy'])]

if contact_email:
    # Only create contacts with REAL emails
    contact = Contact(...)
else:
    page.contact_scrape_status = 'NoContactFound'
    # Skip contact creation entirely
```

**Status:** ✅ Accurate - Documents past failure, FIXED in current code
**Current Reality:** WF7 NOW filters fake emails, skips contact creation when none found
**Value:** Explains WHY current code has fake email filtering

**Extraction Plan:**
- [ ] Add to CONTRIBUTING.md Anti-Patterns section:
  - Title: "Placeholder Driven Development"
  - Rule: "NO placeholders in production code - fail fast instead"
  - Current WF7 pattern as CORRECT example (fake email filtering)
  - Reference: `Docs/01_Architectural_Guidance/war_stories/WAR_STORY__Placeholder_Driven_Development__2025-08-26.md`

---

### File: war_stories/WAR_STORY__WF7_Crawl4ai_Attribute_Fix__2025-08-25.md

**Code Claims:**
1. crawl4ai returns `.markdown` attribute (NOT `.content`)
2. WF7 PageCurationService was broken using `.content`
3. Single-line fix: `.content` → `.markdown`
4. Docker + Playwright + crawl4ai fully operational

**Verification Against Current WF7 Code:**
```python
# src/services/WF7_V2_L4_1of2_PageCurationService.py:52
html_content = await scrape_page_simple_async(page_url)

# src/utils/simple_scraper.py (37 lines)
async def scrape_page_simple_async(url: str) -> str:
    # Uses aiohttp, NOT crawl4ai
```

**Status:** ⚠️ Outdated - WF7 NO LONGER uses crawl4ai
**Evolution:** Aug 25 → crawl4ai (.markdown) → Sept → simple_scraper.py ($0 cost, 100% success)
**Current Reality:** Production uses simple_scraper.py (37 lines, aiohttp)
**Value:** Historical - explains evolution from expensive to free solution

**Extraction Plan:**
- [ ] Add to Documentation/Workflows/README.md WF7 section:
  - Evolution note: "Originally used crawl4ai ($50/domain), evolved to simple_scraper.py ($0/domain, 100% success)"
  - Reference simple_scraper.py as the production pattern
  - Archive war story as historical context (link only)

---

### File: war_stories/WAR_STORY__Dual_Sitemap_Pipeline_Conflict_RCA__2025-09-09.md

**Code Claims:**
1. Two parallel sitemap systems running simultaneously (Legacy + Honeybee)
2. Race conditions from dual processing
3. Fragile status checks causing perpetual skips

**Verification Against Current Code:**
```bash
# Check current sitemap schedulers:
ls -la src/services/ | grep sitemap
# domain_sitemap_submission_scheduler.py
# sitemap_import_scheduler.py
# sitemap_scheduler.py
```

**Status:** ⚠️ Historical incident - may or may not be resolved
**Current Reality:** Multiple sitemap services still exist (needs verification)
**Value:** Explains risks of parallel processing systems

**Extraction Plan:**
- [ ] Verify current sitemap architecture first
- [ ] If still dual-system: Document as known architecture complexity
- [ ] If resolved: Archive as historical lesson
- [ ] Add pattern to CONTRIBUTING.md: "Disable legacy systems before launching modern replacements"

---

### Files: WAR_STORY__WF7_Pattern_Catalog_Synthesis.md + WAR_STORY__WF7_Anti-Pattern_Catalog_Synthesis.md

**Content:** 47 patterns + 47 anti-patterns from WF7 crisis analysis

**Code Claims:**
- Enforcement patterns (The Architect, mandatory checkpoints)
- Guardian approval protocols
- Constitutional framework
- STOP sign enforcement
- Awakening sequences

**Verification Against Current Code:**
```python
# WF7 production code has NO references to:
grep -r "Architect\|Guardian.*approval\|Constitutional" src/
# No matches in working code
```

**Status:** 🔮 Aspirational governance framework
**Current Reality:** WF7 works WITHOUT this governance system
**Value:** Documents aspirational persona/governance model NOT currently enforced

**Extraction Decision:** ❌ DO NOT EXTRACT
**Reason:** These are theoretical governance patterns not reflected in working code
**Action:** ARCHIVE - keep in Docs/ as historical context for persona system experiments

---

## Core Guidance Files - REFERENCE ONLY

### File: 00_MASTER_NAVIGATION_AND_DIAGNOSIS.md

**Content:**
- Emergency response procedures
- Learning paths
- Symptom-to-solution diagnosis table
- Quick command reference
- Guardian/persona navigation

**Code Verification:**
- Quick commands: ✅ Valid (health checks, Docker commands, import tests)
- Symptom diagnosis: ✅ Useful (maps errors to Layer Guardians)
- Guardian references: 🔮 Aspirational (persona system not in code)

**Extraction Plan:**
- [ ] Extract: Symptom-to-solution table → Documentation/Operations/Troubleshooting.md
- [ ] Extract: Quick commands → CLAUDE.md (if not already there)
- [ ] Archive: Guardian/persona navigation (theoretical framework)

---

### File: 01_STOP_SIGNS_CRITICAL_OPERATIONS.md

**Content:**
- 9 STOP signs requiring human review
- Database schema modifications
- Mass file renaming (5+ files)
- Configuration changes
- Auth/security logic
- Documentation deception, compliance theater, analysis paralysis

**Code Verification:**
```bash
# Check if STOP signs are enforced in code:
grep -r "STOP_SIGN\|stop.*sign" src/
# No enforcement in working code
```

**Status:** ⚠️ Advisory guidance NOT enforced in code
**Current Reality:** These are good rules but not automated/enforced
**Value:** Documents dangerous operations that SHOULD require review

**Extraction Plan:**
- [ ] Extract to Documentation/Operations/Dangerous-Operations.md:
  - Database schema modifications (ADR-001 already covers this)
  - Mass file renaming threshold (5+ files)
  - Configuration/auth changes requiring review
- [ ] Note: Currently advisory only, not enforced
- [ ] Remove: Aspirational STOP signs (doc deception, compliance theater) - not relevant to current code-first approach

---

### File: 03_ARCHITECTURAL_PATTERNS_LIBRARY.md

**Content:**
- V7 naming convention (WF[X]_V[N]_L[Layer]_...)
- Blessed patterns by layer
- Anti-patterns 1-17

**Code Verification:**
```python
# Check V7 naming in WF7:
ls src/models/WF7* src/routers/v3/WF7* src/services/WF7*
# WF7_V2_L1_1of1_ContactModel.py ✅
# WF7_V3_L3_1of1_PagesRouter.py ✅
# WF7_V2_L4_1of2_PageCurationService.py ✅
```

**Status:** ✅ Accurate - WF7 follows V7 naming in production
**Critical Finding:** Anti-Pattern #17 (SQLAlchemy Enum bug) is IN this file but NOT in CONTRIBUTING.md

**Extraction Plan:**
- [ ] V7 naming convention → CONTRIBUTING.md (if not already there)
- [ ] Anti-Pattern #17 (Enum .value bug) → CONTRIBUTING.md Anti-Patterns
- [ ] Blessed patterns → Verify against WF7, extract proven ones to CONTRIBUTING.md
- [ ] Archive: Guardian references, persona protocols

---

## Extraction Summary

### ✅ HIGH VALUE - Extract to Documentation/

**To CONTRIBUTING.md Anti-Patterns:**
1. SQLAlchemy Enum .value bug (war story + anti-pattern #17)
2. Placeholder Driven Development pattern
3. Mass file renaming threshold (5+ files = STOP)
4. Database schema changes require review (reinforces ADR-001)

**To Documentation/Operations/:**
1. Troubleshooting.md - Symptom-to-solution diagnosis table (from Master Navigation)
2. Dangerous-Operations.md - Critical operations requiring review (from STOP Signs)

**To Documentation/Workflows/README.md WF7:**
1. Evolution note: crawl4ai → simple_scraper.py
2. Reference to simple_scraper.py as production pattern

**To CLAUDE.md or Documentation/Operations/:**
1. Quick command reference (health checks, Docker ops, import verification)

### ⚠️ REFERENCE - Link from Documentation/, Keep in Docs/

**Historical Context:**
1. War stories directory - Battle-tested lessons explaining working code
2. Guardian's Paradox reference (Docs/00_Constitution/) - Explains why simplicity matters
3. Pattern/Anti-Pattern catalogs - Comprehensive crisis analysis (aspirational governance)

**Rationale:** These provide valuable historical context explaining WHY current code works the way it does, but are too detailed for daily use. Link from Documentation/ with "For historical context, see..."

### ❌ ARCHIVE - No Extraction Needed

**Aspirational Governance:**
1. The Architect persona protocols
2. Guardian approval workflows
3. Constitutional framework
4. Awakening sequences
5. Enforcement patterns

**Rationale:** These describe a persona/governance system that is NOT enforced in current working code. The lessons learned (ENUM bug, placeholder pattern) have been extracted. The governance framework itself is theoretical.

**Action:** Keep in Docs/01_Architectural_Guidance/ for historical reference but do not migrate to Documentation/

---

## Implementation Plan

**Phase 1: Extract Critical Anti-Patterns (30 min)**
1. Add Enum .value bug to CONTRIBUTING.md
2. Add Placeholder pattern to CONTRIBUTING.md
3. Verify against WF7 production code

**Phase 2: Extract Operational Guidance (30 min)**
1. Create Documentation/Operations/Troubleshooting.md
2. Create Documentation/Operations/Dangerous-Operations.md
3. Update CLAUDE.md with quick commands (if not present)

**Phase 3: Update WF7 Documentation (15 min)**
1. Add evolution note to Workflows/README.md
2. Reference simple_scraper.py pattern

**Phase 4: Create Reference Links (15 min)**
1. Add "For historical context" section to relevant Documentation/ files
2. Link to war stories, Guardian's Paradox, pattern catalogs

**Total Time:** ~90 minutes

**Success Criteria:**
- ✅ All battle-tested anti-patterns from war stories in CONTRIBUTING.md
- ✅ Operational guidance accessible in Documentation/
- ✅ Historical context preserved via links
- ✅ No duplication of content
- ✅ Working code patterns (WF7) accurately documented

---

## Decision: DO NOT Extract Aspirational Governance

**Reasoning:**
The Guardian/Architect/persona system represents months of experimental governance work, but:

1. **Not enforced in working code** - WF7 works WITHOUT these patterns
2. **Lessons already extracted** - ADRs, CONTRIBUTING.md have the actual learnings
3. **Guardian's Paradox warning** - "Do exactly what is asked, nothing more"
4. **Code-first philosophy** - Documentation describes working code, not ideal governance

**What we keep:**
- ✅ Battle-tested anti-patterns (Enum bug, Placeholder pattern)
- ✅ Historical war stories explaining WHY code works this way
- ✅ STOP sign concepts as advisory guidance

**What we archive:**
- ❌ Mandatory checkpoint enforcement (not in code)
- ❌ The Architect constitutional authority (aspirational)
- ❌ Guardian approval workflows (theoretical)
- ❌ Awakening sequences (persona framework)

**This honors the Guardian's Paradox:** Document what IS, not what should be. Extract battle-tested lessons, archive experimental governance.

---

**Next Step:** Get user approval before executing extraction plan.
