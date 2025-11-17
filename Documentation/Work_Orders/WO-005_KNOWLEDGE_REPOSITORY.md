# WO-005: Build Knowledge Repository for Context Reconstruction
**Created:** November 17, 2025 2:22 AM  
**Priority:** HIGH  
**Estimated Effort:** 12-16 hours  
**Status:** NOT STARTED

---

## Objective

Build a comprehensive knowledge repository that allows any future AI or human to quickly reconstruct the full system context gained during the Nov 17, 2025 debugging session.

**Success Criteria:** A future AI with no context can read the repository in 30-60 minutes and understand the complete system.

---

## Build Order (Critical - Follow Exactly)

### Phase 1: Foundation (Build First - 4 hours)

**Build these in order. Each depends on previous:**

1. **RECONSTRUCT_CONTEXT.md** (30 min) - Master checklist
2. **QUICK_START.md** (1 hour) - 5-minute system overview
3. **GLOSSARY.md** (1 hour) - Define all terms with code examples
4. **PATTERNS.md** (1.5 hours) - Do This / Not That patterns

### Phase 2: Historical Context (Build Second - 4 hours)

5. **INCIDENTS/** directory (2 hours) - Document 4 major incidents
6. **DECISIONS/** directory (1.5 hours) - Document 3-5 key decisions
7. **ARCHAEOLOGY.md** (30 min) - Git investigation guide

### Phase 3: Operational (Build Third - 4 hours)

8. **SYSTEM_MAP.md** (2 hours) - Complete architecture map
9. **HEALTH_CHECKS.md** (1.5 hours) - Verification procedures
10. **DEPENDENCY_MAP.md** (30 min) - External services

---

## Component Specifications

### 1. RECONSTRUCT_CONTEXT.md
**File:** `Documentation/RECONSTRUCT_CONTEXT.md`  
**Purpose:** Step-by-step guide to reconstruct context

**Must Include:**
- Checklist format with time estimates
- Links to all 9 other components
- Clear "You should now know" section
- Total time: 30-60 minutes

**Template:**
```markdown
# Context Reconstruction Checklist

## Quick Start (5 min)
□ Read this file
□ Understand 10-component structure

## Essential Reading (30 min)
□ QUICK_START.md
□ SYSTEM_MAP.md
□ Last 5 INCIDENTS/
□ PATTERNS.md

## Verification (15 min)
□ Run health checks
□ Query Supabase
□ Check Render logs

## Current State (10 min)
□ Review GAPS_IMPROVEMENTS.md
□ Check recent commits

## You Should Now Know:
✓ System architecture
✓ Common failure modes
✓ How to debug
✓ Current priorities
```

---

### 2. QUICK_START.md
**File:** `Documentation/QUICK_START.md`  
**Purpose:** 5-minute system overview

**Must Include:**
- What system does (1 min)
- All 7 workflows listed (2 min)
- Key files and commands (1 min)
- Next steps (1 min)

**Critical:** Must be readable in 5 minutes, no more.

---

### 3. GLOSSARY.md
**File:** `Documentation/GLOSSARY.md`  
**Purpose:** Define all terminology

**Terms to Define:**
- Dual-Status Pattern
- Adapter Service
- Honeybee
- Job vs Task vs Workflow
- Status values (Queued/Submitted/Processing/Complete)
- Auto-Selection Rules

**Each Term Must Have:**
- Definition
- Code example (link to actual file)
- Why it matters

---

### 4. PATTERNS.md
**File:** `Documentation/PATTERNS.md`  
**Purpose:** Correct vs incorrect patterns

**Patterns to Document:**
1. Service Communication (✅ direct vs ❌ HTTP)
2. Background Tasks (✅ asyncio.create_task vs ❌ nothing)
3. Status Updates (dual-status pattern)
4. Error Handling
5. Database Transactions
6. Scheduler Setup
7. Job Creation
8. Auto-Selection Logic

**Each Pattern:**
- ✅ Correct example with code
- ❌ Wrong example with code
- Why it matters
- Real incident reference

---

### 5. INCIDENTS/ Directory
**Location:** `Documentation/INCIDENTS/`  
**Purpose:** Searchable incident history

**Initial Incidents:**
1. `2025-11-17-sitemap-jobs-not-processing.md`
2. `2025-09-09-scheduler-disabled.md`
3. `2025-11-17-authentication-failure.md`
4. `2025-11-17-http-service-calls.md`

**Each Incident Template:**
```markdown
# INCIDENT-[DATE]-[NAME]

## Metadata
Date, Severity, Duration, Workflows Affected

## Symptoms
What we saw

## Root Cause
The actual bug

## Why Hidden
What masked it

## Investigation
How we found it

## Fix
Commit + code change

## Lessons Learned
What we learned

## Related
Links to other incidents/decisions
```

---

### 6. DECISIONS/ Directory
**Location:** `Documentation/DECISIONS/`  
**Purpose:** Why things are the way they are

**Initial Decisions:**
1. `2025-09-09-disable-sitemap-job-processor.md` (FAILED)
2. `2025-11-17-use-direct-service-calls.md` (SUCCESS)
3. `2025-11-17-use-asyncio-create-task.md` (SUCCESS)

**Each Decision Template:**
```markdown
# DECISION-[DATE]-[NAME]

## Context
Why this mattered

## Decision
What was chosen

## Alternatives
Other options considered

## Rationale
Why this option

## Trade-offs
Gains and losses

## Outcome
Did it work?

## Lessons
What we learned
```

---

### 7. ARCHAEOLOGY.md
**File:** `Documentation/ARCHAEOLOGY.md`  
**Purpose:** How to investigate code history

**Must Include:**
- Essential git commands
- Investigation workflows
- Real examples from our codebase
- Common pitfalls

**Commands to Document:**
```bash
# Find when file created
git log --diff-filter=A --follow -- file.py

# Find when deleted
git log --all --full-history -- file.py

# Find function changes
git log -p -S "function_name" -- file.py

# Find by message
git log --all --grep="keyword"
```

---

### 8. SYSTEM_MAP.md
**File:** `Documentation/SYSTEM_MAP.md`  
**Purpose:** Complete architecture

**Must Include:**
- All 7 workflows with data flow
- All database tables with relationships
- All services by workflow
- All schedulers with intervals
- All API endpoints
- All status fields
- Critical paths (user action → system response)
- External dependencies

**Note:** This is the most comprehensive document. Reference existing WF4_WF5_WF7 docs and expand to cover WF1-3.

---

### 9. HEALTH_CHECKS.md
**File:** `Documentation/HEALTH_CHECKS.md`  
**Purpose:** How to verify system health

**Must Include:**
- Quick health check (5 min)
- Detailed checks per workflow
- Expected timings
- Common failures with solutions
- Monitoring queries

**Quick Check Template:**
```sql
-- Queue depths
SELECT COUNT(*) FROM domains WHERE sitemap_analysis_status = 'queued';

-- Stuck jobs
SELECT COUNT(*) FROM jobs WHERE status = 'pending' 
AND created_at < NOW() - INTERVAL '5 minutes';

-- Recent processing
SELECT COUNT(*) FROM pages WHERE page_processing_status = 'Complete' 
AND updated_at > NOW() - INTERVAL '1 hour';
```

---

### 10. DEPENDENCY_MAP.md
**File:** `Documentation/DEPENDENCY_MAP.md`  
**Purpose:** External service dependencies

**Must Include:**
- ScraperAPI (usage, cost, rate limits, failure modes)
- Supabase (database, access method, tables)
- Render.com (deployment, logs, environment)
- Honeybee (categorization, auto-selection rules)

**Each Dependency:**
- What it does
- Who uses it
- Cost implications
- Failure modes
- Mitigation strategies

---

## Implementation Notes

### For Future AI Reading This

**If context rolled over:**
1. Start with RECONSTRUCT_CONTEXT.md
2. Follow the checklist exactly
3. Read components in order (1-10)
4. Don't skip Phase 1 (foundation)
5. Reference existing WF4_WF5_WF7 docs

**Key Files Already Exist:**
- `WF4_WF5_WF7_COMPLETE_INDEX.md`
- `WF4_WF5_WF7_DATABASE_SCHEMA.md`
- `WF4_WF5_WF7_SERVICES.md`
- `WF4_WF5_WF7_GAPS_IMPROVEMENTS.md`
- `WO-004_HOTFIX_POSTMORTEM.md`

**Use these as references** - don't duplicate, link to them.

### What Needs Investigation

**WF1, WF2, WF3** are not yet documented. To complete SYSTEM_MAP.md, you must:
1. Find WF1 services/routers (Single Search)
2. Find WF2 services/routers (Deep Scan)
3. Find WF3 services/routers (Domain Extraction)
4. Document their tables, status fields, schedulers

**Search Strategy:**
```bash
# Find WF1-3 files
find src/ -name "*WF1*" -o -name "*WF2*" -o -name "*WF3*"
grep -r "Single Search" src/
grep -r "Deep Scan" src/
grep -r "Domain Extraction" src/
```

---

## Acceptance Criteria

### Overall
- [ ] All 10 components created
- [ ] All components link to each other
- [ ] RECONSTRUCT_CONTEXT.md tested (can rebuild context in 60 min)
- [ ] No duplicate information (link to existing docs)
- [ ] All code examples are real (not placeholders)

### Per Component
- [ ] Component 1: RECONSTRUCT_CONTEXT.md complete
- [ ] Component 2: QUICK_START.md readable in 5 min
- [ ] Component 3: GLOSSARY.md has all terms
- [ ] Component 4: PATTERNS.md has 8 patterns
- [ ] Component 5: INCIDENTS/ has 4 incidents
- [ ] Component 6: DECISIONS/ has 3 decisions
- [ ] Component 7: ARCHAEOLOGY.md has git commands
- [ ] Component 8: SYSTEM_MAP.md covers all 7 workflows
- [ ] Component 9: HEALTH_CHECKS.md has working queries
- [ ] Component 10: DEPENDENCY_MAP.md lists all external services

---

## Commit Strategy

**Commit after each phase:**
- Commit 1: Phase 1 complete (4 files)
- Commit 2: Phase 2 complete (3 files/dirs)
- Commit 3: Phase 3 complete (3 files)

**Commit Message Template:**
```
docs(WO-005): Phase X - [Component Names]

Created knowledge repository components:
- Component N: Purpose
- Component M: Purpose

Progress: X/10 components complete
Next: [Next phase]

Related: WO-005
```

---

## Time Estimates

**Phase 1:** 4 hours (foundation)  
**Phase 2:** 4 hours (historical)  
**Phase 3:** 4 hours (operational)  
**Total:** 12 hours

**Buffer:** +4 hours for WF1-3 investigation

**Grand Total:** 16 hours

---

## Success Metrics

**After completion, a future AI should be able to:**
1. ✅ Understand system in 30-60 minutes
2. ✅ Debug common issues independently
3. ✅ Know why code exists
4. ✅ Verify system health
5. ✅ Continue work without basic questions

---

**END OF WORK ORDER**

Start with Component 1 (RECONSTRUCT_CONTEXT.md) and work sequentially through all 10 components.
