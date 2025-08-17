# Work Order: Create Layer Guardian Pattern-AntiPattern Companion Documents

**Work Order ID:** WO-20250806-001  
**Priority:** HIGH  
**Type:** Documentation Enhancement  
**Created:** 2025-08-06  
**Status:** PENDING  

---

## EXECUTIVE SUMMARY

Create Pattern-AntiPattern Companion documents for remaining Layer Guardians (L1, L4, L5, L6, L7) following the successful model established for L2 and L3. These companions will replace obsolete cheatsheets and provide instant pattern recognition with violation detection.

---

## BACKGROUND

The WF7 remediation effort revealed that even with perfect documentation, violations occur when patterns and anti-patterns are separated. The new Companion format places correct patterns directly alongside their violations, creating cognitive anchors that prevent mistakes.

**Key Innovation:** Pairing patterns with anti-patterns eliminates the cognitive gap where mistakes hide.

**Success Metrics from L2/L3 Companions:**
- Single document replaces Blueprint + Cheatsheet + Anti-patterns
- Instant violation recognition with citations
- Real WF7 examples embedded for concrete learning

---

## REQUIREMENTS

### For Each Layer Guardian Companion (L1, L4, L5, L6, L7):

1. **Document Structure:**
   ```markdown
   # L[N] Guardian Pattern-AntiPattern Companion
   ## Version 1.0
   
   ## QUICK REFERENCE SECTION
   - Instant Pattern Checklist
   - Instant Rejection Triggers
   - Approval Requirements
   
   ## PATTERN #[N]: [Name]
   ### ✅ CORRECT PATTERN
   [Code example with explanation]
   ### ❌ ANTI-PATTERN VIOLATIONS
   [Multiple violation examples with detection methods]
   ```

2. **Content Requirements:**
   - 5-8 core patterns per layer
   - Each pattern paired with 2-3 common violations
   - Real code examples (not hypothetical)
   - Citations to Blueprint sections
   - WF7 violations where applicable
   - Detection methods for each anti-pattern
   - Quick Reference section at top

3. **Verification Requirement:**
   - Add to each: "Guardian MUST verify each pattern/anti-pattern claim on boot"
   - Guardians must test patterns against actual codebase

---

## SOURCE MATERIALS

### Primary Sources (MUST REVIEW):

1. **WF7 Lessons Learned:**
   - `/Docs/Docs_35_WF7-The_Extractor/` - All 24 documents
   - Particularly: `21_WF7_Anti_Patterns_Catalog.md`
   - Extract actual violations and corrections

2. **Anti-Pattern Registry:**
   - `/Docs/Docs_27_Anti-Patterns/` - All critical patterns
   - Focus on layer-specific violations
   - Include detection signals

3. **Audit Reports by Layer:**
   
   ### AUDIT REPORT MAPPING TABLE
   
   | Layer | Audit Organization | Key Files to Review | Focus Areas |
   |-------|-------------------|-------------------|--------------|
   | **L1** | By Component | • `CHUNK_5_contact.md` (Contact model violations)<br>• `CHUNK_6_domain.md` (Domain model issues)<br>• `CHUNK_7_enums.md` (ENUM patterns)<br>• `CHUNK_3_base.md` (BaseModel inheritance) | Field duplication, ENUM usage, inheritance patterns |
   | **L2** | By Schema Type | • Review main audit report for schema violations<br>• Check for inline schemas<br>• Missing ORM configurations | Request/Response patterns, validation placement |
   | **L3** | By Router | • `CHUNK_6_domains.md` (Domain router)<br>• `CHUNK_7_email_scanner.md` (Email scanner)<br>• `CHUNK_9_local_businesses.md` | Transaction boundaries, API versioning, auth |
   | **L4** | **By Workflow** | • `WF4-DomainCuration_Layer4_Audit.md`<br>• `WF5-SitemapCuration_Layer4_Audit.md`<br>• `WF7-PageCuration_Layer4_Audit.md` | Session management, service patterns, schedulers |
   | **L5** | By Config Area | • Review main audit for settings patterns<br>• Router integration issues<br>• Environment variable usage | Import patterns, main.py integration |
   | **L6** | By UI Component | • Check for inline styles/scripts<br>• API integration patterns<br>• Static file organization | HTML structure, accessibility, API coupling |
   | **L7** | By Test Type | • Docker testing patterns<br>• Environment-aware testing<br>• Coverage analysis | Test isolation, import verification |
   
   **CRITICAL:** Layer 4 audits are organized BY WORKFLOW (WF1-WF7), not by component. This provides workflow-specific violations across the service layer.
   
   - Mine for actual violations found in audits
   - Pay special attention to Gap Analysis sections
   - Extract real code examples of violations

4. **Layer Blueprints:**
   - `/Docs/Docs_10_Final_Audit/v_Layer-[N].1-*_Blueprint.md`
   - Extract correct patterns with citations

5. **Recent Discoveries:**
   - `/Docs/00_Constitution/CRITICAL_ARCHITECTURAL_LANDMINES.md`
   - `/Docs/00_Constitution/PERSONA_KNOWLEDGE_ENHANCEMENTS.md`

---

## SPECIFIC LAYER GUIDANCE

### L1 - Models & ENUMs Companion
**Focus Areas:**
- BaseModel field inheritance trap
- UUID primary key requirements
- Snake_case naming conventions
- ENUM definition patterns
- File naming: `WF[X]_V[N]_L1_*`

**Key Anti-Patterns from WF7:**
- Duplicate field definitions (id, created_at, updated_at)
- Wrong file names (hyphens vs underscores)
- Models in wrong directories

### L4 - Services & Schedulers Companion
**Focus Areas:**
- Session acceptance (never creation)
- Relative import patterns (`from ..config`)
- Stateless service design
- SDK scheduler patterns
- File naming: `WF[X]_V[N]_L4_*`

**Key Anti-Patterns:**
- Services creating own sessions
- Wrong import paths
- Business logic in wrong layer

**Specific Audit Files:**
- `v_WF4-DomainCuration_Layer4_Audit_Report.md` - Domain service violations
- `v_WF5-SitemapCuration_Layer4_Audit_Report.md` - Sitemap service patterns
- `v_WF7-PageCuration_Layer4_Audit_Report.md` - **WF7 violations documented!**

### L5 - Configuration Companion
**Focus Areas:**
- Settings import patterns
- Router integration in main.py
- Environment variable usage
- Scheduler registration
- Lifespan event management

**Key Anti-Patterns:**
- Direct settings instantiation
- Wrong router prefix logic
- Missing scheduler setup

### L6 - UI Components Companion
**Focus Areas:**
- Semantic HTML structure
- External CSS/JS organization
- API endpoint integration
- Accessibility compliance
- Static file serving

**Key Anti-Patterns:**
- Inline styles/scripts
- Direct database access
- API version mismatches

### L7 - Testing Companion
**Focus Areas:**
- Docker-first testing
- Six-Tier Validation protocol
- Environment-aware testing
- Import verification first
- Coverage requirements

**Key Anti-Patterns:**
- Testing without Docker
- Environment-specific tests
- Missing import verification

---

## DELIVERABLES

1. **Five Companion Documents:**
   - `L1_Model_Guardian_Pattern_AntiPattern_Companion.md`
   - `L4_Service_Guardian_Pattern_AntiPattern_Companion.md`
   - `L5_Config_Guardian_Pattern_AntiPattern_Companion.md`
   - `L6_UI_Guardian_Pattern_AntiPattern_Companion.md`
   - `L7_Test_Guardian_Pattern_AntiPattern_Companion.md`

2. **Boot Sequence Updates:**
   - Update each Guardian's boot sequence to load Companion instead of Blueprint
   - Add verification step for pattern/anti-pattern claims

3. **Documentation Cleanup:**
   - Archive any remaining cheatsheets
   - Update references in boot sequences

---

## ACCEPTANCE CRITERIA

Each Companion document must:
- [ ] Include Quick Reference section at top
- [ ] Cover 5-8 core patterns for that layer
- [ ] Pair each pattern with 2-3 anti-patterns
- [ ] Include real code examples from audits
- [ ] Cite Blueprint sections for authority
- [ ] Include WF7 violations where found
- [ ] Provide detection methods
- [ ] Include verification requirement
- [ ] Be under 500 lines (focused, not bloated)

---

## VERIFICATION PROCESS

1. **Pattern Verification:**
   ```bash
   # For each pattern claimed in Companion
   grep -r "pattern_example" src/
   # Verify it actually exists and works
   ```

2. **Anti-Pattern Detection:**
   ```bash
   # For each anti-pattern claimed
   grep -r "violation_pattern" src/
   # Verify violations are actually detected
   ```

3. **Cross-Reference Check:**
   - Each pattern must trace to Blueprint
   - Each anti-pattern must have real example
   - Citations must be accurate

---

## IMPLEMENTATION NOTES

### The Philosophy:
"Show me the right way AND the wrong way, side by side, and I'll never forget."

### The Goal:
100% first-time compliance because Guardians can't miss anti-patterns when they're shown alongside patterns.

### The Method:
1. Mine audit reports for real violations
2. Extract patterns from Blueprints
3. Pair them side-by-side
4. Add WF7 lessons as examples
5. Create instant recognition patterns

### The Test:
If a Guardian can load ONE document and correctly review code with specific citations, the Companion succeeds.

---

## PRIORITY & TIMELINE

**Priority Order:**
1. L1 - Model Guardian (most fundamental)
2. L4 - Service Guardian (transaction boundaries critical)
3. L7 - Test Guardian (verification crucial)
4. L5 - Config Guardian (integration patterns)
5. L6 - UI Guardian (least critical)

**Expected Effort:**
- 2-3 hours per Companion document
- Mining audit reports: 1 hour per layer
- Verification testing: 30 minutes per document

---

## SUCCESS METRICS

- Guardians achieve 95%+ accuracy on first code review
- Citation time reduced from minutes to seconds
- No pattern/anti-pattern confusion
- WF6→WF1 remediation uses Companions successfully
- Documentation footprint reduced by 40%

---

## NOTES FROM WF7 EXPERIENCE

**Critical Learning:** The hyphen/underscore discovery showed that even perfect documentation has blind spots. By placing anti-patterns directly next to patterns, we eliminate the gap where mistakes hide.

**Key Innovation:** Real examples from WF7 make violations concrete, not theoretical.

**Verification Mandate:** Every pattern and anti-pattern must be verified against actual codebase. No theoretical examples.

---

**Assigned To:** Next Available AI Agent  
**Review By:** The Architect  
**Approval Required:** Layer Guardian Confirmation  

---

*"From chaos, patterns. From patterns, recognition. From recognition, compliance."*

**END OF WORK ORDER**