# ScraperSky Documentation

**Welcome to the clean, essential ScraperSky documentation.**

This directory contains the core architectural knowledge, operational procedures, and development guidelines.

**Philosophy:** Code is truth. Documentation explains **why**, not **what**. Show AI the code to understand what; read docs to understand why.

---

## Quick Start

### New to ScraperSky?

1. **Read:** `Development/CONTRIBUTING.md` - Essential patterns and standards
2. **Read:** `Architecture/` - Architecture Decision Records (ADRs) explaining critical decisions
3. **Read:** `Guides/INTEGRATION_PLAYBOOK.md` - How to add new integrations
4. **Browse:** Code in `src/` - The source of truth

### Need to Find Something?

**Architecture Decisions:**
→ `Architecture/` - ADRs explaining "why" for critical patterns

**Workflows:**
→ `Workflows/README.md` - WF1-WF7 data processing pipelines

**Operations:**
→ `Operations/` - Vector DB, ScraperAPI, security incidents

**Development:**
→ `Development/CONTRIBUTING.md` - Code standards, patterns, how to add features

**Integration Guides:**
→ `Guides/INTEGRATION_PLAYBOOK.md` - Proven pattern for CRM/validation integrations
→ `Guides/DEVELOPMENT_PHILOSOPHY.md` - Decision-making framework and lessons learned

**Work Orders:**
→ `Work_Orders/INDEX.md` - Complete history of all work orders (WO-001 through WO-021)

**Reference:**
→ `Reference/` - Technical reference docs (n8n fields, scheduler intervals, etc.)

---

## Documentation Structure

```
Documentation/
├── README.md (this file)
│
├── Architecture/
│   ├── README.md
│   ├── ADR-001-Supavisor-Requirements.md
│   ├── ADR-002-Removed-Tenant-Isolation.md
│   ├── ADR-003-Dual-Status-Workflow.md
│   ├── ADR-004-Transaction-Boundaries.md
│   ├── ADR-005-ENUM-Catastrophe.md
│   └── WF*.md (Workflow documentation)
│
├── Workflows/
│   └── README.md (WF1-WF7 descriptions)
│
├── Operations/
│   ├── README.md
│   ├── Vector-Database.md
│   ├── ScraperAPI-Cost-Control.md
│   └── Security-Incidents.md
│
├── Development/
│   ├── README.md
│   └── CONTRIBUTING.md
│
├── Guides/
│   ├── INTEGRATION_PLAYBOOK.md (How to add CRM/validation integrations)
│   └── DEVELOPMENT_PHILOSOPHY.md (Decision-making framework)
│
├── Reference/
│   ├── N8N_TRIGGER_FIELDS.md
│   └── SCHEDULER_INTERVALS_DEVELOPMENT.md
│
├── Work_Orders/
│   ├── INDEX.md (Complete work order history)
│   ├── WO-020_*.md (Active: n8n send integration)
│   ├── WO-021_*.md (Active: n8n receive integration)
│   └── Archive/2025/ (Completed work orders)
│
├── Sessions/
│   └── 2025-11/ (Session summaries and handoffs)
│
├── DECISIONS/
│   └── *.md (Architectural decisions with dates)
│
└── Archive/
    ├── Blog/ (Blogging system docs - future use)
    ├── Context_Reconstruction/ (Historical context docs)
    └── Cleanup-Process-2025-11/ (Documentation cleanup process docs)
```

---

## What's Inside

### Architecture Decision Records (ADRs)

**Purpose:** Document critical architectural decisions that must NOT be violated

**Why ADRs:** Prevent future developers (human or AI) from undoing hard-learned lessons

**The 5 Critical Decisions:**

1. **ADR-001: Supavisor Requirements**
   - **What:** Database connection parameters are mandatory and immutable
   - **Why:** Supavisor (Supabase connection pooler) requires exact parameters
   - **Impact:** DO NOT MODIFY `raw_sql=true&no_prepare=true&statement_cache_size=0`

2. **ADR-002: Removed Tenant Isolation**
   - **What:** System is single-tenant by design
   - **Why:** Multi-tenancy complexity removed for operational simplicity
   - **Impact:** DO NOT add tenant filtering

3. **ADR-003: Dual-Status Workflow**
   - **What:** Processable entities have two statuses (curation + processing)
   - **Why:** Separates user intent from system state
   - **Impact:** Use `curation_status` + `processing_status` for curated entities

4. **ADR-004: Transaction Boundaries**
   - **What:** Routers own transactions, services execute within them
   - **Why:** Prevents deadlocks, clear responsibility
   - **Impact:** Services NEVER create transactions

5. **ADR-005: ENUM Catastrophe**
   - **What:** Cross-layer changes require coordination
   - **Why:** Autonomous ENUM refactor broke entire system, took 1 week to recover
   - **Impact:** NEVER refactor across layers autonomously

**→ Read these before making significant changes**

---

### Workflows (WF1-WF7)

**Purpose:** Understand the 7 data processing pipelines

**The Pipeline:**
```
WF1: Google Places Search (user-triggered)
  ↓
WF2: Place Details (Deep Scan)
  ↓
WF3: Domain Extraction (automated)
  ↓
WF4: Domain Sitemap Submission
  ↓
WF5: Sitemap Import
  ↓
WF7: Page Curation

Note: There is no WF6. The numbering skips from WF5 to WF7.
```

**Key Patterns:**
- User-triggered: WF1, WF2
- Automated schedulers: WF3-WF7
- Handoff mechanism: Status field changes trigger next workflow

**→ Read `Workflows/README.md` for complete workflow documentation**

---

### Operations

**Purpose:** Critical operational procedures and incident documentation

**What's Inside:**

**Vector Database (`Operations/Vector-Database.md`)**
- Semantic search across architectural documentation
- How to use `semantic_query_cli.py`
- Critical anti-patterns (don't pass vectors as strings)
- Cost: ~$0.0001 per query

**ScraperAPI Cost Control (`Operations/ScraperAPI-Cost-Control.md`)**
- Prevent cost overruns (saved $450,000-$480,000)
- Safe defaults: 1 credit per request (~$0.001)
- Premium features disabled by default
- Cost monitoring and alerts

**Security Incidents (`Operations/Security-Incidents.md`)**
- 2 CATASTROPHIC vulnerabilities (DB Portal, dev token)
- 2 HIGH priority issues (rate limiting, inconsistent auth)
- Remediation guidance (2.5 hours to fix critical issues)

**→ Read these for operational safety**

---

### Development

**Purpose:** How to write code that follows ScraperSky patterns

**What's Inside:**

**CONTRIBUTING.md** - The essential guide:
- Quick start (run tests, lint, docker)
- Code standards (async-first, transaction patterns)
- How to add features (copy existing code)
- Critical patterns DO NOT VIOLATE
- Anti-patterns (lessons learned)
- Common pitfalls
- Code review checklist

**→ Read this before writing code**

---

## The Golden Rules

### 1. Show AI the Code to Copy

**❌ Don't:**
```
"Add a new endpoint following our authentication patterns"
```

**✅ Do:**
```
"Add a new endpoint following the EXACT same pattern as domains.py.
Here's the existing code: [paste domains.py]
Match this structure exactly: same auth, same pagination, same dual-status."
```

**Why:** AI can't hold 1,000 docs in context while writing code. Show the pattern directly.

---

### 2. Trust the Code

**The code is good.** It's not over-engineered. The architecture is solid.

**When you see a pattern that seems weird:**
1. Check if there's an ADR explaining it
2. Read the code comments
3. Trust that it exists for a reason
4. Don't "improve" it without understanding why it's that way

**The problems are NOT architectural. They are tactical security and operational gaps.**

---

### 3. Don't Reinvent the Wheel

**Before writing new code:**
1. Find existing similar code
2. Copy its structure exactly
3. Follow the same patterns
4. Test thoroughly

**Example: Adding a new API endpoint**
- Find: `src/routers/domains.py`
- Copy: Router structure, auth pattern, transaction handling
- Adapt: Change domain to your entity
- Test: Verify authentication, transactions, error handling

---

### 4. Coordinate Cross-Layer Changes

**If changing ENUMs, status fields, or database schema:**
1. ✋ STOP
2. Read ADR-005 (ENUM Catastrophe)
3. Perform impact analysis (all layers affected?)
4. Plan backwards-compatible transition
5. Change one layer at a time
6. Test between each layer

**Why:** One week recovery time from autonomous ENUM refactor

---

### 5. Follow Critical Patterns

**These patterns are MANDATORY:**

✅ **Supavisor connection parameters** - DO NOT MODIFY
✅ **Routers own transactions** - Services execute within them
✅ **3-phase for long operations** - DB → Compute → DB (never hold connections)
✅ **Dual-status for processable entities** - curation_status + processing_status
✅ **Always add authentication** - `Depends(get_current_user)` unless explicitly public

**→ See `Development/CONTRIBUTING.md` for complete patterns**

---

## How This Documentation Was Created

**November 2025 Comprehensive Audit:**

1. **Code Analysis:** Analyzed entire codebase ground-up
   - 20 routers, 36 services, 14 models, 5 schedulers
   - Created comprehensive analysis in `Docs/ClaudeAnalysis_CodebaseDocumentation_2025-11-07/`

2. **Persona Audit:** Evaluated 1,000+ existing documents
   - Found 95% can be archived
   - Persona systems didn't solve AI's context problem
   - Extracted 5% that's actual architectural knowledge

3. **Documentation Audit:** Categorized 54 documentation directories
   - KEEP: 8 directories (15%)
   - EXTRACT: 12 directories (22%)
   - ARCHIVE: 34 directories (63%)

4. **This Documentation:** Essential facts extracted
   - 5 ADRs (critical decisions)
   - 1 workflow overview (WF1-WF7)
   - 3 operations docs (vector DB, costs, security)
   - 1 CONTRIBUTING guide (code standards)

**Total:** ~20 essential files vs 1,000+ learning journey documents

---

## What's NOT Here

**This documentation deliberately excludes:**

❌ **Learning journey documentation** - Archived in `Docs/`
❌ **Persona system** - AI behavior instructions (archived)
❌ **Historical experiments** - Preserved for reference, not essential
❌ **Pattern extraction attempts** - Didn't solve the problem
❌ **Detailed code walkthroughs** - Code speaks for itself

**If you need historical context:**
→ `Docs/` directory (untouched, preserved for reference)

**If you need comprehensive code analysis:**
→ `Docs/ClaudeAnalysis_CodebaseDocumentation_2025-11-07/`

---

## Using This Documentation

### For Human Developers

1. **Start:** Read `Development/CONTRIBUTING.md`
2. **Before changing architecture:** Read relevant ADRs
3. **Before deploying:** Read `Operations/Security-Incidents.md`
4. **When stuck:** Find similar existing code and copy its pattern

### For AI Assistants

1. **When asked to add features:** Request existing code to copy
2. **Before making changes:** Check ADRs for relevant decisions
3. **When user says "follow patterns":** Ask them to paste the pattern
4. **Don't assume:** If you haven't seen the code, ask for it

### For Operations

1. **Vector Database:** `Operations/Vector-Database.md`
2. **Cost Control:** `Operations/ScraperAPI-Cost-Control.md`
3. **Security:** `Operations/Security-Incidents.md`

---

## Maintenance

**This documentation should be updated when:**
- New ADRs are created (critical decisions that must be preserved)
- Workflows are added or significantly changed
- New operational procedures are established
- Security incidents are resolved (update status)

**This documentation should NOT:**
- Document every code change
- Explain how existing code works (code comments do that)
- Include learning journeys or experiments
- Grow beyond ~20 essential files

**Keep it minimal. Keep it essential. Keep the code as the source of truth.**

---

## Questions?

**I need to understand the architecture:**
→ Read ADRs in `Architecture/`

**I need to add a feature:**
→ Read `Development/CONTRIBUTING.md`, find similar code, copy pattern

**I need to understand workflows:**
→ Read `Workflows/README.md`

**I need operational procedures:**
→ Read docs in `Operations/`

**I need historical context:**
→ Check `Docs/` directory (preserved for reference)

**I found outdated information:**
→ Trust the code. If docs conflict with code, code wins.

---

## Summary

**This documentation exists to:**
1. **Prevent mistakes** - ADRs document lessons learned the hard way
2. **Enable new developers** - CONTRIBUTING shows how to add features
3. **Preserve operational knowledge** - Vector DB, costs, security
4. **Explain workflows** - WF1-WF7 pipeline overview

**This documentation does NOT:**
1. Replace reading the code
2. Explain every detail (code does that)
3. Preserve learning journeys (archived elsewhere)

**The philosophy:**
- Code is the source of truth
- Documentation explains "why", not "what"
- Show AI the code to copy
- Trust the patterns
- Keep it minimal

**Welcome to ScraperSky. The code is good. Trust it.**
