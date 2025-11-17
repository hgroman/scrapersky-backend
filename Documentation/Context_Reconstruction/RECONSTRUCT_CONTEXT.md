# Context Reconstruction Checklist
**Purpose:** Rebuild complete system understanding in 30-60 minutes  
**Last Updated:** November 17, 2025  
**Related:** WO-005 Knowledge Repository

---

## How to Use This Guide

This checklist allows you (a future AI or human) to quickly reconstruct the full context of the ScraperSky backend system. Follow the steps in order, checking off each item as you complete it.

**Total Time:** 30-60 minutes  
**Outcome:** Complete understanding of system architecture, common issues, and how to debug

---

## Quick Start (5 minutes)

□ **Read this entire file** - Understand the reconstruction process  
□ **Understand the 10-component structure** - See [Component Overview](#component-overview) below  
□ **Locate all documentation files** - Verify they exist in `Documentation/`  
□ **Check git history** - Run `git log --oneline -20` to see recent changes

**You should now know:** Where everything is and what you're about to learn

---

## Essential Reading (30 minutes)

### Core Documentation (15 minutes)

□ **Reference:** [QUICK_START.md](./QUICK_START.md) | [Master Guide](../README_CONTEXT_RECONSTRUCTION.md) (5 min)
   - What the system does
   - All 7 workflows
   - Key files and commands
   
□ **Read [SYSTEM_MAP.md](./SYSTEM_MAP.md)** (10 min)
   - Complete architecture
   - Data flow through all workflows
   - Database tables and relationships
   - Services and schedulers

**You should now know:** System architecture and data flow

### Historical Context (15 minutes)

□ **Read last 5 incidents in [INCIDENTS/](../INCIDENTS/)**
   - Start with most recent
   - Focus on: symptoms, root cause, lessons learned
   - Note: Common failure patterns
   
□ **Read [PATTERNS.md](./PATTERNS.md)** (5 min)
   - Correct vs incorrect patterns
   - Why patterns matter
   - Real incidents caused by anti-patterns

**You should now know:** Common failure modes and how to avoid them

---

## Verification (15 minutes)

### Check System Health (10 minutes)

□ **Run health checks from [HEALTH_CHECKS.md](./HEALTH_CHECKS.md)**
   - Quick health check queries (5 min)
   - Check queue depths
   - Check for stuck jobs
   - Verify recent processing

□ **Query Supabase directly** (3 min)
   ```sql
   -- Verify tables exist
   SELECT table_name FROM information_schema.tables 
   WHERE table_schema = 'public' 
   ORDER BY table_name;
   
   -- Check recent activity
   SELECT COUNT(*) FROM domains WHERE created_at > NOW() - INTERVAL '24 hours';
   SELECT COUNT(*) FROM pages WHERE created_at > NOW() - INTERVAL '24 hours';
   ```

□ **Check Render.com logs** (2 min)
   - Visit Render.com dashboard
   - Check for recent errors
   - Verify schedulers initialized

**You should now know:** Current system health and activity level

### Understand Current State (5 minutes)

□ **Review [WF4_WF5_WF7_GAPS_IMPROVEMENTS.md](../Architecture/WF4_WF5_WF7_GAPS_IMPROVEMENTS.md)**
   - P0 issues (critical)
   - P1 issues (high priority)
   - Current sprint plan

□ **Check recent commits**
   ```bash
   git log --oneline --since="7 days ago"
   ```

□ **Review active work orders in [Work_Orders/](../Work_Orders/)**

**You should now know:** Current priorities and active work

---

## Deep Dive (Optional - 30 minutes)

If you need deeper understanding:

□ **Read [GLOSSARY.md](./GLOSSARY.md)** (10 min)
   - All terminology defined
   - Code examples for each term
   
□ **Study specific workflow documentation**
   - [WF4_WF5_WF7_DATABASE_SCHEMA.md](../Architecture/WF4_WF5_WF7_DATABASE_SCHEMA.md)
   - [WF4_WF5_WF7_SERVICES.md](../Architecture/WF4_WF5_WF7_SERVICES.md)
   
□ **Read [ARCHAEOLOGY.md](./ARCHAEOLOGY.md)** (5 min)
   - How to investigate code history
   - Essential git commands
   
□ **Review [DECISIONS/](../DECISIONS/)** (10 min)
   - Why things are the way they are
   - Failed decisions and lessons learned

□ **Check [DEPENDENCY_MAP.md](./DEPENDENCY_MAP.md)** (5 min)
   - External service dependencies
   - Failure modes and costs

---

## Component Overview

The knowledge repository consists of 10 components:

### Foundation (Phase 1)
1. **RECONSTRUCT_CONTEXT.md** (this file) - Master checklist
2. **QUICK_START.md** - 5-minute system overview
3. **GLOSSARY.md** - All terminology defined
4. **PATTERNS.md** - Correct vs incorrect patterns

### Historical Context (Phase 2)
5. **INCIDENTS/** - Searchable incident database
6. **DECISIONS/** - Why things are the way they are
7. **ARCHAEOLOGY.md** - How to investigate code history

### Operational Knowledge (Phase 3)
8. **SYSTEM_MAP.md** - Complete architecture map
9. **HEALTH_CHECKS.md** - Verification procedures
10. **DEPENDENCY_MAP.md** - External service dependencies

### Existing Documentation (Reference)
- **WF4_WF5_WF7_COMPLETE_INDEX.md** - Pipeline documentation index
- **WF4_WF5_WF7_DATABASE_SCHEMA.md** - Database tables and relationships
- **WF4_WF5_WF7_SERVICES.md** - Service layer architecture
- **WF4_WF5_WF7_GAPS_IMPROVEMENTS.md** - Known issues and improvements
- **WO-004_HOTFIX_POSTMORTEM.md** - Nov 17, 2025 debugging session

---

## Verification Checklist

After completing the essential reading and verification steps, you should be able to answer:

### Architecture Questions
- [ ] What are the 7 workflows and what does each do?
- [ ] What are the 4 core database tables?
- [ ] How do domains become sitemaps become pages?
- [ ] What is the dual-status pattern?
- [ ] What are the 3 main schedulers and their intervals?

### Operational Questions
- [ ] How do I check if the system is healthy?
- [ ] How do I verify a workflow is working end-to-end?
- [ ] Where do I look for errors?
- [ ] What are common failure modes?
- [ ] How do I debug a stuck job?

### Historical Questions
- [ ] What was the Nov 17, 2025 incident?
- [ ] Why was the sitemap job processor disabled?
- [ ] What is the correct service communication pattern?
- [ ] Why do we use asyncio.create_task()?
- [ ] What are the most common anti-patterns?

### Current State Questions
- [ ] What are the P0 issues that need fixing?
- [ ] What is the current sprint plan?
- [ ] Are there any active work orders?
- [ ] What was the last deployment?
- [ ] Are there any known broken features?

**If you can answer all these questions, you have successfully reconstructed context!**

---

## Quick Reference Commands

### Database Queries
```sql
-- Check queue depths
SELECT COUNT(*) FROM domains WHERE sitemap_analysis_status = 'queued';
SELECT COUNT(*) FROM sitemap_files WHERE sitemap_import_status = 'Queued';
SELECT COUNT(*) FROM pages WHERE page_processing_status = 'Queued';

-- Check for stuck jobs
SELECT * FROM jobs WHERE status = 'pending' 
AND created_at < NOW() - INTERVAL '5 minutes';

-- Check recent processing
SELECT COUNT(*) FROM pages WHERE page_processing_status = 'Complete' 
AND updated_at > NOW() - INTERVAL '1 hour';
```

### Git Commands
```bash
# Recent changes
git log --oneline --since="7 days ago"

# Find when file was modified
git log --follow -- path/to/file.py

# Find commits by keyword
git log --all --grep="sitemap"

# See what changed in a commit
git show <commit-hash>
```

### System Access
- **Database:** Supabase (via MCP tools)
- **Logs:** Render.com dashboard
- **Code:** Local repository

---

## What to Do Next

Based on your needs:

**If you're debugging an issue:**
1. Check [HEALTH_CHECKS.md](./HEALTH_CHECKS.md) for verification steps
2. Review [INCIDENTS/](../INCIDENTS/) for similar past issues
3. Use [ARCHAEOLOGY.md](./ARCHAEOLOGY.md) to investigate code history
4. Check [PATTERNS.md](./PATTERNS.md) for common anti-patterns

**If you're implementing a feature:**
1. Check [WF4_WF5_WF7_GAPS_IMPROVEMENTS.md](../Architecture/WF4_WF5_WF7_GAPS_IMPROVEMENTS.md) for known issues
2. Review [PATTERNS.md](./PATTERNS.md) for correct patterns
3. Study [SYSTEM_MAP.md](./SYSTEM_MAP.md) for architecture
4. Check [DECISIONS/](../DECISIONS/) for architectural choices

**If you're onboarding:**
1. Complete this entire checklist
2. Read all Phase 1 and Phase 2 documents
3. Run through health checks
4. Review recent incidents and decisions

---

## Success Criteria

You have successfully reconstructed context when you can:

✅ Explain the system architecture to someone else  
✅ Debug a common issue independently  
✅ Understand why code exists the way it does  
✅ Verify system health without help  
✅ Know where to find answers to specific questions  
✅ Continue work on active tasks without asking basic questions

---

## Maintenance

**Keep this checklist updated:**
- Add new incidents to INCIDENTS/
- Document new decisions in DECISIONS/
- Update SYSTEM_MAP.md when architecture changes
- Add new patterns to PATTERNS.md as discovered
- Update health checks as monitoring evolves

**This checklist should always be the starting point for context reconstruction.**

---

**Last Updated:** November 17, 2025  
**Next Review:** After major architectural changes  
**Maintained By:** Engineering Team
