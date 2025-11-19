# Documentation Audit Methodology

**Purpose:** Systematically review Docs/ against actual working code to extract valuable clarifications

**Created:** Nov 16, 2025

---

## Ground Truth Baseline

### 1. Code Reality (Primary Source)
- **ClaudeAnalysis_CodebaseDocumentation_2025-11-07/** - Comprehensive Nov 2025 analysis
- **WF7 Implementation** - Most modern workflow (100% success, production-ready Sept 2025)
  - `src/models/WF7_V2_L1_1of1_ContactModel.py`
  - `src/schemas/WF7_V3_L2_1of1_PageCurationSchemas.py`
  - `src/routers/v3/WF7_V3_L3_1of1_PagesRouter.py`
  - `src/services/WF7_V2_L4_1of2_PageCurationService.py`
  - `src/services/WF7_V2_L4_2of2_PageCurationScheduler.py`
  - `src/utils/simple_scraper.py`
- **CLAUDE.md** - Project truth as of Nov 2025
- **Working patterns:** Async-first, transaction ownership, 3-phase scheduler, Simple Scraper

### 2. Extracted Essentials (Secondary Source)
- **Documentation/Architecture/** - 5 ADRs (Supavisor, Tenant Removal, Dual-Status, Transactions, ENUM Catastrophe)
- **Documentation/Development/CONTRIBUTING.md** - Code patterns and anti-patterns
- **Documentation/Workflows/README.md** - WF1-WF7 pipeline
- **Documentation/Operations/** - Vector DB, ScraperAPI Cost Control, Security Incidents

### 3. Evolution Understanding
- **Workflow progression:** WF1 → WF2 → WF3 → WF4 → WF5 → WF7 (no WF6)
- **Assumption:** WF7 is MOST compliant with lessons learned from WF1-WF5
- **Pattern:** Later workflows incorporate fixes from earlier disasters

---

## Audit Process (4-Step)

### Step 1: Establish Code Understanding
**For each document to audit:**

1. Read document completely
2. Identify code references:
   - File paths mentioned
   - Function/class names cited
   - Import patterns described
   - Command examples given

**Output:** List of code claims made by document

### Step 2: Verify Against Working Code
**For each code claim:**

1. Check if file/function exists in current codebase
2. Verify claim matches actual implementation
3. Note discrepancies:
   - ✅ Accurate - matches working code
   - ⚠️ Outdated - code has evolved
   - ❌ Inaccurate - never matched code
   - 🔮 Aspirational - describes ideal, not current reality

**Output:** Accuracy assessment for each claim

### Step 3: Assess Value Beyond Existing Documentation
**Ask these questions:**

1. **Does it explain WHY?**
   - Does it clarify WHY code works this way?
   - Does it explain WHY certain patterns are critical?
   - Is this "why" already in ADRs or CONTRIBUTING.md?

2. **Does it provide operational clarity?**
   - Symptom → solution mappings?
   - Quick command references?
   - Diagnostic procedures?
   - Is this already in Operations/ docs?

3. **Does it document enforced ideals?**
   - STOP signs that prevent disasters?
   - Mandatory processes that work?
   - Evidence these are actually followed?

4. **Does it add practical value?**
   - Would a developer use this when coding?
   - Does it prevent real mistakes?
   - Is it actionable (not just aspirational)?

**Output:** Value assessment (EXTRACT / REFERENCE / ARCHIVE)

### Step 4: Extract or Archive
**Based on assessment:**

**EXTRACT** - Add to Documentation/ if:
- ✅ Explains working code patterns not in CONTRIBUTING.md
- ✅ Provides operational procedures not in Operations/
- ✅ Documents proven ideals actively enforced
- ✅ Offers symptom diagnosis not elsewhere
- ✅ Contains anti-patterns verified in code comments

**REFERENCE** - Link from Documentation/ if:
- ⚠️ Contains valuable detail but belongs in historical context
- ⚠️ Explains evolution that clarifies current state
- ⚠️ Documents experiments that led to ADRs

**ARCHIVE** - No action if:
- ❌ Aspirational documentation for unimplemented systems
- ❌ Outdated patterns superseded by current code
- ❌ Duplicate of content already in Documentation/
- ❌ Work journals or process documentation

**Output:** Extraction plan with specific content to migrate

---

## Audit Template (Per Document)

```markdown
### Document: [filename]

**Code Claims:**
1. [Claim about code/pattern/file]
2. [Claim about code/pattern/file]

**Verification:**
- Claim 1: ✅ Accurate / ⚠️ Outdated / ❌ Inaccurate / 🔮 Aspirational
- Claim 2: ✅ Accurate / ⚠️ Outdated / ❌ Inaccurate / 🔮 Aspirational

**Value Assessment:**
- Explains WHY: [Yes/No - already in ADRs?]
- Operational clarity: [Yes/No - already in Operations/?]
- Enforced ideals: [Yes/No - evidence in code?]
- Practical value: [Yes/No - actionable?]

**Decision:** EXTRACT / REFERENCE / ARCHIVE

**Extraction Plan:**
- [ ] Section [X] → Documentation/[target file]
- [ ] Content: [specific paragraphs/tables/commands]
```

---

## Example: Docs/01_Architectural_Guidance/03_ARCHITECTURAL_PATTERNS_LIBRARY.md

**Code Claims:**
1. V7 naming: `WF7_V2_L1_1of1_ContactModel.py` (underscores in Python)
2. Transaction ownership: Routers own, services accept session
3. SQLAlchemy Enum bug: Must use `.value` in queries

**Verification:**
- Claim 1: ✅ Accurate - WF7 files follow this pattern exactly
- Claim 2: ✅ Accurate - WF7 routers have `async with session.begin()`
- Claim 3: ✅ Accurate - Critical bug documented in war stories

**Value Assessment:**
- Explains WHY: Yes (Python can't import hyphens) - NOT in CONTRIBUTING.md
- Operational clarity: Yes (verification commands) - NOT in Operations/
- Enforced ideals: Yes (WF7 follows V7 naming in production)
- Practical value: Yes (Enum bug prevents production failures)

**Decision:** EXTRACT

**Extraction Plan:**
- [ ] V7 naming convention → CONTRIBUTING.md "Naming Standards" section
- [ ] Enum bug anti-pattern → CONTRIBUTING.md Anti-Patterns section
- [ ] Verification commands → Operations/Code-Health-Checks.md (new)

---

## Success Criteria

Audit is complete when:
1. ✅ Every document in target directory assessed
2. ✅ All valuable content extracted to Documentation/
3. ✅ Extraction verified against working code
4. ✅ No duplication created
5. ✅ User approves extraction plan

**Current Status:** Methodology defined, ready to begin systematic audit

---

**Next:** Apply this methodology to Docs/01_Architectural_Guidance/ (23 files)
