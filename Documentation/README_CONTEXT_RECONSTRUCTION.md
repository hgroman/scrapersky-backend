# Context Reconstruction System - Master Guide
**Purpose:** Navigate all documentation and rebuild system understanding  
**Last Updated:** November 17, 2025  
**Related:** WO-005 Knowledge Repository

---

## What Is This?

This documentation system allows **any future AI or human** to quickly reconstruct complete understanding of the ScraperSky backend system, even after complete context loss.

**Time to full context:** 30-60 minutes following the checklist

---

## Quick Navigation

### 🚀 Start Here (Pick Your Path)

**Path 1: I'm a Future AI (Context Rolled Over)**
→ Start with [`Context_Reconstruction/RECONSTRUCT_CONTEXT.md`](./Context_Reconstruction/RECONSTRUCT_CONTEXT.md)

**Path 2: I'm New to This Codebase**
→ Start with [`Context_Reconstruction/QUICK_START.md`](./Context_Reconstruction/QUICK_START.md)

**Path 3: I'm Debugging an Issue**
→ Start with [`Context_Reconstruction/HEALTH_CHECKS.md`](./Context_Reconstruction/HEALTH_CHECKS.md)

**Path 4: I Need to Understand a Term**
→ Start with [`Context_Reconstruction/GLOSSARY.md`](./Context_Reconstruction/GLOSSARY.md)

---

## Documentation Structure

### 📁 Context_Reconstruction/ (The Core System)

**Foundation Documents:**
- **[RECONSTRUCT_CONTEXT.md](./Context_Reconstruction/RECONSTRUCT_CONTEXT.md)** - Master checklist (30-60 min)
  - Step-by-step context rebuild
  - Time estimates for each step
  - Verification queries
  - Links to all other docs

- **[QUICK_START.md](./Context_Reconstruction/QUICK_START.md)** - 5-minute overview
  - What the system does
  - The 7 workflows (WF1-WF7)
  - Key files and commands
  - Critical concepts

- **[GLOSSARY.md](./Context_Reconstruction/GLOSSARY.md)** - Terminology with code examples
  - All terms defined
  - Real code examples
  - File locations
  - Cross-references

- **[PATTERNS.md](./Context_Reconstruction/PATTERNS.md)** - Do This / Not That
  - 8 documented patterns
  - ✅ Correct vs ❌ Wrong examples
  - Real incidents referenced
  - Commit hashes included

**Investigation & Operations:**
- **[ARCHAEOLOGY.md](./Context_Reconstruction/ARCHAEOLOGY.md)** - Git investigation guide
  - Essential git commands
  - Investigation workflows
  - Real examples from codebase
  - Tips and pitfalls

- **[SYSTEM_MAP.md](./Context_Reconstruction/SYSTEM_MAP.md)** - Complete architecture
  - All 7 workflows mapped
  - Database tables and relationships
  - Services, schedulers, API endpoints
  - Critical paths

- **[HEALTH_CHECKS.md](./Context_Reconstruction/HEALTH_CHECKS.md)** - Verification procedures
  - Quick 5-minute health check
  - End-to-end testing
  - Common failures and solutions
  - Monitoring queries

- **[DEPENDENCY_MAP.md](./Context_Reconstruction/DEPENDENCY_MAP.md)** - External services
  - ScraperAPI, Supabase, Render.com
  - Honeybee, Google Maps API
  - Cost, limits, failure modes
  - Mitigation strategies

---

### 📁 INCIDENTS/ (Historical Failures)

**Purpose:** Learn from past incidents to prevent recurrence

**Index:** [`INCIDENTS/README.md`](./INCIDENTS/README.md)

**Major Incidents:**
- **[2025-11-17-sitemap-jobs-not-processing](./INCIDENTS/2025-11-17-sitemap-jobs-not-processing.md)** (CRITICAL)
  - Jobs created but never processed
  - 2+ months of silent failure
  - Fixed: Commit 9f091f6

- **[2025-09-09-scheduler-disabled](./INCIDENTS/2025-09-09-scheduler-disabled.md)** (CRITICAL)
  - Scheduler disabled without replacement
  - Exposed adapter bug

- **[2025-11-17-authentication-failure](./INCIDENTS/2025-11-17-authentication-failure.md)** (HIGH)
  - Dev token restricted to development
  - Fixed: Commits 8604a37, d9e4fc2, 1ffa371

- **[2025-11-17-http-service-calls](./INCIDENTS/2025-11-17-http-service-calls.md)** (MEDIUM)
  - Anti-pattern: HTTP between services
  - Fixed: Commit 1ffa371

**Each incident includes:**
- Symptoms (what we saw)
- Root cause (the actual bug)
- Why it was hidden
- Investigation process
- The fix (with commit reference)
- Lessons learned
- Prevention measures

---

### 📁 DECISIONS/ (Architectural Choices)

**Purpose:** Understand why things are the way they are

**Index:** [`DECISIONS/README.md`](./DECISIONS/README.md)

**Key Decisions:**
- **[2025-11-17-use-direct-service-calls](./DECISIONS/2025-11-17-use-direct-service-calls.md)** (SUCCESS)
  - Direct calls instead of HTTP
  - Status: Active pattern

- **[2025-11-17-use-asyncio-create-task](./DECISIONS/2025-11-17-use-asyncio-create-task.md)** (SUCCESS)
  - Trigger background processing immediately
  - Status: Active pattern

- **[2025-09-09-disable-sitemap-job-processor](./DECISIONS/2025-09-09-disable-sitemap-job-processor.md)** (FAILED)
  - Disabled without replacement
  - Status: Superseded

**Each decision includes:**
- Context (why it mattered)
- What was chosen
- Alternatives considered
- Rationale and trade-offs
- Outcome (success/failure)

---

### 📁 Architecture/ (Detailed Technical Docs)

**WF4→WF5→WF7 Pipeline (Fully Documented):**
- **[WF4_WF5_WF7_COMPLETE_INDEX.md](./Architecture/WF4_WF5_WF7_COMPLETE_INDEX.md)** - Master index
- **[WF4_WF5_WF7_PIPELINE_OVERVIEW.md](./Architecture/WF4_WF5_WF7_PIPELINE_OVERVIEW.md)** - End-to-end flow
- **[WF4_WF5_WF7_DATABASE_SCHEMA.md](./Architecture/WF4_WF5_WF7_DATABASE_SCHEMA.md)** - Tables, fields, relationships
- **[WF4_WF5_WF7_SERVICES.md](./Architecture/WF4_WF5_WF7_SERVICES.md)** - Service layer architecture
- **[WF4_WF5_WF7_GAPS_IMPROVEMENTS.md](./Architecture/WF4_WF5_WF7_GAPS_IMPROVEMENTS.md)** - Known gaps and priorities

**Other Architecture Docs:**
- ADR-001 through ADR-005 (Architecture Decision Records)
- Various workflow documentation

---

### 📁 Work_Orders/ (Task Management)

**Recent Work Orders:**
- **[WO-004_HOTFIX_POSTMORTEM.md](./Work_Orders/WO-004_HOTFIX_POSTMORTEM.md)** - Nov 17 debugging session
- **[WO-005_KNOWLEDGE_REPOSITORY.md](./Work_Orders/WO-005_KNOWLEDGE_REPOSITORY.md)** - This documentation system

---

## How to Use This System

### Scenario 1: Context Rollover (AI)
1. Read [`RECONSTRUCT_CONTEXT.md`](./Context_Reconstruction/RECONSTRUCT_CONTEXT.md)
2. Follow the 30-60 minute checklist
3. Verify understanding with queries
4. Continue work

### Scenario 2: New Team Member (Human)
1. Read [`QUICK_START.md`](./Context_Reconstruction/QUICK_START.md) (5 min)
2. Read [`SYSTEM_MAP.md`](./Context_Reconstruction/SYSTEM_MAP.md) (15 min)
3. Review [`PATTERNS.md`](./Context_Reconstruction/PATTERNS.md) (10 min)
4. Explore specific workflows as needed

### Scenario 3: Debugging an Issue
1. Run [`HEALTH_CHECKS.md`](./Context_Reconstruction/HEALTH_CHECKS.md) queries
2. Search [`INCIDENTS/`](./INCIDENTS/) for similar symptoms
3. Check [`PATTERNS.md`](./Context_Reconstruction/PATTERNS.md) for anti-patterns
4. Use [`ARCHAEOLOGY.md`](./Context_Reconstruction/ARCHAEOLOGY.md) to investigate history

### Scenario 4: Understanding a Feature
1. Check [`GLOSSARY.md`](./Context_Reconstruction/GLOSSARY.md) for terms
2. Read [`SYSTEM_MAP.md`](./Context_Reconstruction/SYSTEM_MAP.md) for architecture
3. Review specific Architecture/ docs
4. Check [`DECISIONS/`](./DECISIONS/) for rationale

### Scenario 5: Planning New Work
1. Review [`Architecture/WF4_WF5_WF7_GAPS_IMPROVEMENTS.md`](./Architecture/WF4_WF5_WF7_GAPS_IMPROVEMENTS.md)
2. Check [`PATTERNS.md`](./Context_Reconstruction/PATTERNS.md) for correct patterns
3. Review [`INCIDENTS/`](./INCIDENTS/) to avoid past mistakes
4. Check [`DECISIONS/`](./DECISIONS/) for architectural constraints

---

## Documentation Principles

### 1. Self-Contained
Everything needed to understand the system is here. No external dependencies.

### 2. Actionable
Real code examples, not abstract concepts. Copy-paste ready.

### 3. Connected
Everything links to everything. Follow the trail.

### 4. Honest
Documents failures and anti-patterns, not just successes.

### 5. Maintainable
Clear structure, easy to update, version controlled.

### 6. Survives Context Loss
Can rebuild understanding from scratch in 30-60 minutes.

---

## Quick Reference

### Key Commits
- **9f091f6** - Fixed sitemap jobs not processing (added background trigger)
- **1ffa371** - Removed HTTP service calls (use direct calls)
- **0aaaad6** - Disabled scheduler (caused 2-month outage)

### Key Workflows
- **WF1:** Single Search (Google Maps) - [WF1_SINGLE_SEARCH.md](./Architecture/WF1_SINGLE_SEARCH.md)
- **WF2:** Deep Scan (enrichment) - [WF2_WF3_ENRICHMENT_EXTRACTION.md](./Architecture/WF2_WF3_ENRICHMENT_EXTRACTION.md)
- **WF3:** Domain Extraction - [WF2_WF3_ENRICHMENT_EXTRACTION.md](./Architecture/WF2_WF3_ENRICHMENT_EXTRACTION.md)
- **WF4:** Sitemap Discovery - [WF4_WF5_WF7_COMPLETE_INDEX.md](./Architecture/WF4_WF5_WF7_COMPLETE_INDEX.md)
- **WF5:** Sitemap Curation - [WF4_WF5_WF7_COMPLETE_INDEX.md](./Architecture/WF4_WF5_WF7_COMPLETE_INDEX.md)
- **WF6:** Sitemap Import (URL extraction) - [WF4_WF5_WF7_COMPLETE_INDEX.md](./Architecture/WF4_WF5_WF7_COMPLETE_INDEX.md)
- **WF7:** Page Curation / Contact Extraction - [WF4_WF5_WF7_COMPLETE_INDEX.md](./Architecture/WF4_WF5_WF7_COMPLETE_INDEX.md)

**Note:** WF5 (Sitemap Curation) and WF6 (Sitemap Import) are distinct workflows

### Key Tables
- `places` → `local_business` → `domains` → `sitemap_files` → `pages`

### Key Services
- DomainToSitemapAdapterService (WF4)
- SitemapProcessingService (WF4→WF5)
- SitemapImportService (WF5)
- PageCurationService (WF7)

### External Dependencies
- **Google Maps API** (WF1-2 business discovery) - [DEPENDENCY_MAP.md](./Context_Reconstruction/DEPENDENCY_MAP.md#google-maps-api)
- **ScraperAPI** (WF7 page scraping) - [DEPENDENCY_MAP.md](./Context_Reconstruction/DEPENDENCY_MAP.md#scraperapi)
- **Supabase** (database) - [DEPENDENCY_MAP.md](./Context_Reconstruction/DEPENDENCY_MAP.md#supabase-database)
- **Render.com** (deployment) - [DEPENDENCY_MAP.md](./Context_Reconstruction/DEPENDENCY_MAP.md#rendercom)
- **Honeybee** (WF5-6 URL categorization) - [DEPENDENCY_MAP.md](./Context_Reconstruction/DEPENDENCY_MAP.md#honeybee)

---

## Maintenance

### When to Update This Documentation

**Always update when:**
- Adding new workflows
- Fixing critical bugs
- Making architectural decisions
- Experiencing incidents
- Changing external dependencies

**How to update:**
1. Update relevant files in Context_Reconstruction/
2. Add incidents to INCIDENTS/
3. Add decisions to DECISIONS/
4. Update Architecture/ docs as needed
5. Commit with clear message referencing WO-005

---

## Statistics

- **Total Files:** 20+ documentation files
- **Total Lines:** 4,500+ lines
- **Coverage:** WF4-7 fully documented, WF1-3 mapped
- **Time to Reconstruct:** 30-60 minutes
- **Created:** November 17, 2025 (WO-005)

---

## Getting Help

**If you're lost:**
1. You're reading the right file! 
2. Pick a path from "Quick Navigation" above
3. Follow the links
4. Trust the process

**If something is unclear:**
1. Check [`GLOSSARY.md`](./Context_Reconstruction/GLOSSARY.md)
2. Search [`INCIDENTS/`](./INCIDENTS/) for examples
3. Review [`PATTERNS.md`](./Context_Reconstruction/PATTERNS.md)

**If you find a gap:**
1. Document it in the relevant file
2. Add to [`Architecture/WF4_WF5_WF7_GAPS_IMPROVEMENTS.md`](./Architecture/WF4_WF5_WF7_GAPS_IMPROVEMENTS.md)
3. Create a work order if needed

---

**Welcome to the ScraperSky backend. Everything you need to understand it is here. Start with your chosen path above.** 🚀
