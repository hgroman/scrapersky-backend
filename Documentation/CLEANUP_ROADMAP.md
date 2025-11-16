# ScraperSky Documentation Cleanup Roadmap

**Goal:** Retire the 54-directory Docs/ library, keeping only Documentation/

**Status:** Phase 1 Complete (Essential Documentation created)

---

## Current State

### ✅ What We Have (Documentation/)

**Essential Docs (14 files, 166KB):**
- Architecture/ (5 ADRs - critical decisions)
- Workflows/ (WF1-WF7 overview)
- Operations/ (Vector DB, costs, security)
- Development/ (CONTRIBUTING guide)

**Comprehensive Reference (12 files, ~200KB):**
- ClaudeAnalysis_CodebaseDocumentation_2025-11-07/
  - Complete codebase analysis
  - 01_ARCHITECTURE.md (31KB)
  - 02_DATABASE_SCHEMA.md (16KB)
  - 03_API_ENDPOINTS.md (16KB)
  - 04_SERVICE_LAYER.md (19KB)
  - 05_SCHEDULERS_WORKFLOWS.md (35KB)
  - 06_AUTHENTICATION_SECURITY.md (15KB)
  - 07_CONFIGURATION.md (26KB)
  - 08_EXTERNAL_INTEGRATIONS.md (22KB)
  - Plus audits, quick references

**Total:** 26 files, ~366KB (well-organized, comprehensive)

### 📦 What We're Retiring (Docs/)

**54 directories, 1000+ documents:**
- Learning journeys
- Persona systems
- Historical experiments
- Redundant documentation
- Pattern extraction attempts

**Status:** Preserved for reference, to be gradually archived/deleted

---

## Cleanup Phases

### Phase 1: Foundation ✅ COMPLETE

**Completed Nov 2025:**
- ✅ Created Documentation/ structure (14 essential files)
- ✅ Documented 5 critical ADRs
- ✅ Integrated WF7 production knowledge
- ✅ Created comprehensive ClaudeAnalysis reference
- ✅ Established side-by-side structure

**Result:** Documentation/ is production-ready and comprehensive.

---

### Phase 2: Audit Remaining Value (NEXT)

**Goal:** Identify any remaining valuable content in Docs/ worth extracting

**Documents to Review:**
Based on DOCUMENTATION_AUDIT_2025-11-16.md:

**KEEP Directories (8 total) - Already integrated:**
- ✅ Docs_7_Workflow_Canon → Extracted to Workflows/README.md
- ✅ Docs_18_Vector_Operations → Extracted to Operations/Vector-Database.md
- ✅ Docs_27_Anti-Patterns → Extracted to CONTRIBUTING.md
- ✅ Docs_37_JWT_Audit → Extracted to Operations/Security-Incidents.md
- ✅ Docs_44_ScraperAPI-Cost-Crisis → Extracted to Operations/ScraperAPI-Cost-Control.md
- ✅ Docs_51_WF7_Knowledge_Archive → Extracted to Workflows/README.md + CONTRIBUTING.md
- 🔍 Docs_16_ScraperSky_Code_Canon → Review for additional standards
- 🔍 Docs_4_ProjectDocs → Review for business context

**EXTRACT Then Archive Directories (12 total):**
Review each for any missing nuggets:
- Docs_5_Project_Working_Docs (session patterns?)
- Docs_6_Architecture_and_Status (outdated architecture?)
- Docs_10_Final_Audit (audit findings worth keeping?)
- Docs_11_Workflow_Context_Analysis (workflow insights?)
- Docs_26_Train-Wreck-Recovery-2 (disaster recovery procedures?)
- Others listed in DOCUMENTATION_AUDIT_2025-11-16.md

**Action Plan:**
1. Review Docs_16_ScraperSky_Code_Canon
2. Review Docs_4_ProjectDocs
3. Scan EXTRACT directories for missing critical knowledge
4. Add any findings to Documentation/

**Timeline:** 1-2 sessions (2-4 hours)

---

### Phase 3: Archive Historical Docs

**Goal:** Move Docs/ out of active repository

**Options:**

**Option A: Git Archive (Recommended)**
```bash
# Create archive branch
git checkout -b archive/historical-docs-2025-11
git mv Docs/ Archive_Docs_2025-11/
git commit -m "archive: move historical Docs/ to archive branch"
git push origin archive/historical-docs-2025-11

# Remove from main
git checkout main
git rm -r Docs/
git commit -m "cleanup: retire historical Docs/ (archived in archive/historical-docs-2025-11)"
git push origin main
```

**Option B: Compressed Archive**
```bash
# Create tarball
tar -czf Archive_Docs_2025-11-Retired.tar.gz Docs/
mv Archive_Docs_2025-11-Retired.tar.gz ~/archives/

# Remove from repo
git rm -r Docs/
git commit -m "cleanup: retire historical Docs/ (archived locally)"
```

**Option C: Keep as docs-archive/ subdirectory**
```bash
# Rename to clearly signal "archived"
git mv Docs/ docs-archive/
git commit -m "cleanup: rename Docs/ to docs-archive/ (retired)"
```

**Recommendation:** Option A (git branch) - preserves history, removes from main, easily retrievable

**Timeline:** 1 session (30 minutes)

---

### Phase 4: Maintain Documentation/

**Ongoing Process:**

**When to Update Documentation/:**

1. **New ADRs (Architecture/):**
   - Major architectural decision made
   - Lesson learned from production incident
   - Pattern established that must be enforced
   - Example: "ADR-006: Why We Removed Feature X"

2. **New Workflows (Workflows/):**
   - New workflow added (WF8, WF9, etc.)
   - Existing workflow significantly changed
   - Production status updated (success/failure)

3. **Operations Changes (Operations/):**
   - New critical procedure added
   - Cost/security incident occurred
   - Troubleshooting procedure updated

4. **Development Updates (Development/):**
   - New anti-pattern discovered
   - Code standards changed
   - New critical pattern established

**When NOT to Create Docs:**
- ❌ Learning journeys
- ❌ Exploratory documentation
- ❌ Temporary work orders
- ❌ Persona instructions
- ❌ Experimental approaches

**Maintenance Rule:** "Would a new developer need this to avoid mistakes? Would AI need this to write correct code?"
- Yes → Documentation/
- No → Don't create it

---

## Success Criteria

**Documentation/ is successful when:**

✅ **New developers can onboard in <2 hours** by reading:
- Documentation/README.md
- Documentation/Development/CONTRIBUTING.md
- Documentation/Workflows/README.md

✅ **AI assistants can write correct code** by referencing:
- ADRs (what NOT to do)
- CONTRIBUTING.md (patterns to copy)
- Workflows (how system works)

✅ **Operations team can prevent disasters** by following:
- Operations/Security-Incidents.md
- Operations/ScraperAPI-Cost-Control.md
- Operations/Vector-Database.md

✅ **Docs/ is fully retired** (archived or deleted)

✅ **No new docs created outside Documentation/**

---

## Current Status

**Phase 1:** ✅ COMPLETE
**Phase 2:** 🔄 IN PROGRESS (review remaining Docs/)
**Phase 3:** ⏳ PENDING (archive Docs/)
**Phase 4:** ⏳ ONGOING (maintain Documentation/)

**Next Action:** Review Docs_16 and Docs_4 for any missing critical knowledge

---

## Timeline

**Total Estimated Time:** 3-5 hours
- Phase 1: ✅ Complete (8 hours)
- Phase 2: 2-4 hours (review and extract)
- Phase 3: 30 minutes (archive)
- Phase 4: Ongoing (minimal maintenance)

**Target Completion:** End of Nov 2025

---

## Metrics

**Starting State (Nov 1, 2025):**
- Documentation files: 0
- Docs/ directories: 54
- Total docs: 1000+
- Organized: 0%

**Current State (Nov 16, 2025):**
- Documentation files: 26 (14 essential + 12 reference)
- Docs/ directories: 54 (to be retired)
- Essential knowledge: 100% captured
- Organized: 95%

**Target State (Nov 30, 2025):**
- Documentation files: ~30 (with any Phase 2 additions)
- Docs/ directories: 0 (archived)
- Essential knowledge: 100% captured
- Organized: 100%

---

## Questions & Decisions

**Q: What if we discover critical knowledge in Docs/ during Phase 2?**
A: Extract it into appropriate Documentation/ section, document the source, delete original

**Q: What if someone needs historical context from Docs/?**
A: Retrieve from archive branch (Option A) or compressed archive (Option B)

**Q: How do we prevent Docs/ from coming back?**
A: Strict rule: All new docs go in Documentation/. Review in code reviews.

**Q: What about AI-generated documentation during development?**
A: Temporary working docs are fine, but must be distilled into Documentation/ or deleted before PR merge

---

## Related Documents

- CONTINUATION_GUIDE.md (how to continue this work in new sessions)
- ClaudeAnalysis_CodebaseDocumentation_2025-11-07/ (comprehensive reference)
- DOCUMENTATION_AUDIT_2025-11-16.md (54-directory audit)
- PERSONA_AUDIT_2025-11-16.md (persona system analysis)
