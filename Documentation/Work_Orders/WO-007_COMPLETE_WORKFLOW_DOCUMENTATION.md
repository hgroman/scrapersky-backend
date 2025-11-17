# WO-007: Complete Workflow Documentation & Extensibility Patterns
**Created:** November 17, 2025  
**Priority:** P0 (Critical for uniform codebase)  
**Estimated Time:** 12-16 hours  
**Status:** Ready for Claude  
**Related:** WO-005, WO-006

---

## Mission Statement

**Goal:** Achieve complete and total documentation across ALL workflows to enable:
1. **Uniform code** - Same patterns, same quality across WF1-7
2. **Easy understanding** - Any developer can understand any workflow
3. **Extendability** - Clear patterns for adding new entry points (direct submission)

---

## Context

**Current State:**
- ✅ WF4-7: Fully documented (sitemap discovery → contact extraction)
- ❌ WF1-3: Minimal documentation (Google Maps → domain extraction)
- ⚠️ WF6: Clarified as monitoring window for WF5, not true workflow
- ❌ Extensibility patterns: Not documented

**Why This Matters:**
- Can't achieve uniform code without understanding all workflows
- Can't extend system without documented patterns
- WF1-3 are entry points - critical for understanding data flow
- Need to document "how to add direct submission" patterns

---

## Phase 1: Document WF1-3 (8-10 hours)

### Objective
Document WF1 (Single Search), WF2 (Deep Scan), WF3 (Domain Extraction) to same standard as WF4-7.

### Tasks

#### 1.1 WF1: Single Search (Google Maps) - 3 hours
**Purpose:** Search Google Maps for businesses, create Place records

**Deliverables:**
- [ ] Find all WF1 services and routers
- [ ] Document data flow: Search query → Google Maps API → Place records
- [ ] Document Place model fields and their purpose
- [ ] Document Google Maps API integration (key, limits, costs)
- [ ] Identify patterns used (schedulers? direct API calls?)
- [ ] Document error handling
- [ ] Add to SYSTEM_MAP.md

**Investigation Starting Points:**
```bash
find src/ -name "*WF1*" -o -name "*single*search*" -o -name "*places*"
grep -r "google.*maps" src/
grep -r "Place" src/models/
```

**Expected Outputs:**
- Architecture/WF1_SINGLE_SEARCH.md
- Update to SYSTEM_MAP.md
- Update to DEPENDENCY_MAP.md (Google Maps API)

---

#### 1.2 WF2: Deep Scan (Enrichment) - 2 hours
**Purpose:** Enrich Place records with additional details (photos, reviews, hours)

**Deliverables:**
- [ ] Find all WF2 services and schedulers
- [ ] Document what "deep scan" enriches (specific fields)
- [ ] Document when/how it's triggered
- [ ] Document scheduler configuration (if exists)
- [ ] Document error handling and retry logic
- [ ] Identify dual-status pattern usage
- [ ] Add to SYSTEM_MAP.md

**Investigation Starting Points:**
```bash
find src/ -name "*WF2*" -o -name "*deep*scan*" -o -name "*enrich*"
grep -r "deep_scan" src/
grep -r "PlacesDeepService" src/
```

**Expected Outputs:**
- Architecture/WF2_DEEP_SCAN.md
- Update to SYSTEM_MAP.md

---

#### 1.3 WF3: Domain Extraction - 3 hours
**Purpose:** Extract website domains from Place records, create LocalBusiness and Domain records

**Deliverables:**
- [ ] Find all WF3 services and routers
- [ ] Document data flow: Place → LocalBusiness → Domain
- [ ] Document LocalBusiness model and purpose
- [ ] Document Domain model fields
- [ ] Document extraction logic (how domains are extracted from Place.website)
- [ ] Document validation and deduplication
- [ ] Identify dual-status pattern usage
- [ ] Add to SYSTEM_MAP.md

**Investigation Starting Points:**
```bash
find src/ -name "*WF3*" -o -name "*domain*extract*"
grep -r "LocalBusiness" src/models/
grep -r "Domain" src/models/
```

**Expected Outputs:**
- Architecture/WF3_DOMAIN_EXTRACTION.md
- Update to SYSTEM_MAP.md
- Update to GLOSSARY.md (LocalBusiness term)

---

### Phase 1 Success Criteria
- [ ] WF1-3 documented to same standard as WF4-7
- [ ] All services, models, and data flows mapped
- [ ] Patterns identified and documented
- [ ] SYSTEM_MAP.md shows complete WF1→WF7 flow
- [ ] No more "Unknown" or "Needs Documentation" placeholders

---

## Phase 2: Extensibility Patterns (4-6 hours)

### Objective
Document how to add new entry points and extend the system.

### 2.1 Direct Submission Patterns - 2 hours

**Purpose:** Document how to add direct submission endpoints (bypass earlier workflows)

**Deliverables:**
- [ ] Document pattern: "How to add direct Page submission"
  - Skip WF1-5, go straight to WF7
  - Required fields and validation
  - Status initialization
  - Scheduler triggering

- [ ] Document pattern: "How to add direct Domain submission"
  - Skip WF1-3, go straight to WF4
  - Required fields and validation
  - Status initialization
  - Adapter service usage

- [ ] Document pattern: "How to add direct Sitemap submission"
  - Skip WF1-4, go straight to WF5
  - Required fields and validation
  - Status initialization
  - Import triggering

**Expected Output:**
- Context_Reconstruction/EXTENSIBILITY_PATTERNS.md

**Template Structure:**
```markdown
# Extensibility Patterns

## Pattern: Add Direct Page Submission

### Use Case
User has a list of URLs and wants to scrape them directly,
bypassing sitemap discovery.

### Implementation Steps
1. Create API endpoint
2. Validate URL format
3. Create Page record with correct statuses
4. Trigger WF7 processing

### Code Example
[Real code showing the pattern]

### Pitfalls to Avoid
[Common mistakes]
```

---

### 2.2 New Workflow Pattern - 2 hours

**Purpose:** Document how to add a completely new workflow

**Deliverables:**
- [ ] Document workflow creation checklist
  - Model creation (with dual-status fields)
  - Service layer (SDK pattern)
  - Router/API endpoints
  - Scheduler setup
  - Status enums
  - Error handling
  - Testing

- [ ] Document integration patterns
  - How to connect to existing workflows
  - Adapter service pattern
  - Background task triggering
  - Status transitions

**Expected Output:**
- Context_Reconstruction/NEW_WORKFLOW_PATTERN.md

---

### 2.3 Clarify WF6 Status - 30 minutes

**Purpose:** Document that WF6 is monitoring, not a workflow

**Deliverables:**
- [ ] Update all docs to clarify WF6 = monitoring window for WF5
- [ ] Remove "Unknown" status
- [ ] Explain why it's labeled WF6 (historical investment)
- [ ] Document what it monitors

**Files to Update:**
- SYSTEM_MAP.md
- QUICK_START.md
- RECONSTRUCT_CONTEXT.md

---

### 2.4 Cross-Workflow Patterns - 1-2 hours

**Purpose:** Document patterns that span multiple workflows

**Deliverables:**
- [ ] Document "Dual-Status Pattern" across ALL workflows
  - Which workflows use it
  - Which don't (and why)
  - Consistency rules

- [ ] Document "Scheduler Pattern" across ALL workflows
  - Which workflows have schedulers
  - Configuration patterns
  - Triggering patterns

- [ ] Document "Adapter Pattern" across ALL workflows
  - Where adapters exist
  - When to create new adapters
  - Communication patterns

**Expected Output:**
- Update to PATTERNS.md (expand to cover WF1-7)

---

## Phase 3: Verification & Polish (2 hours)

### 3.1 Code Verification - 1 hour
- [ ] Verify all WF1-3 documentation against actual code
- [ ] Verify extensibility patterns with real examples
- [ ] Check all file paths and line numbers
- [ ] Verify all commit references

### 3.2 Cross-Reference Updates - 1 hour
- [ ] Update SYSTEM_MAP.md with complete WF1-7
- [ ] Update GLOSSARY.md with WF1-3 terms
- [ ] Update PATTERNS.md with cross-workflow patterns
- [ ] Update HEALTH_CHECKS.md with WF1-3 queries
- [ ] Update README_CONTEXT_RECONSTRUCTION.md

---

## Deliverables Summary

### New Files to Create
1. `Architecture/WF1_SINGLE_SEARCH.md`
2. `Architecture/WF2_DEEP_SCAN.md`
3. `Architecture/WF3_DOMAIN_EXTRACTION.md`
4. `Context_Reconstruction/EXTENSIBILITY_PATTERNS.md`
5. `Context_Reconstruction/NEW_WORKFLOW_PATTERN.md`

### Files to Update
1. `Context_Reconstruction/SYSTEM_MAP.md` - Complete WF1-7 flow
2. `Context_Reconstruction/PATTERNS.md` - Cross-workflow patterns
3. `Context_Reconstruction/GLOSSARY.md` - WF1-3 terms
4. `Context_Reconstruction/HEALTH_CHECKS.md` - WF1-3 queries
5. `Context_Reconstruction/DEPENDENCY_MAP.md` - Google Maps API
6. `Context_Reconstruction/QUICK_START.md` - WF6 clarification
7. `Context_Reconstruction/RECONSTRUCT_CONTEXT.md` - WF6 clarification
8. `README_CONTEXT_RECONSTRUCTION.md` - Updated navigation

---

## Success Criteria

### Uniform Code
- [ ] All workflows documented to same standard
- [ ] Same pattern library applies to all workflows
- [ ] Consistent terminology across all docs

### Easy Understanding
- [ ] Any developer can understand any workflow in 15 minutes
- [ ] Clear data flow from WF1 → WF7
- [ ] All models and their purposes documented

### Extendability
- [ ] Clear pattern for adding direct submission endpoints
- [ ] Clear pattern for adding new workflows
- [ ] Clear pattern for connecting workflows
- [ ] Real code examples for all patterns

### Completeness
- [ ] No "Unknown" or "Needs Documentation" placeholders
- [ ] All services mapped
- [ ] All models documented
- [ ] All patterns identified
- [ ] WF6 status clarified

---

## Instructions for Claude

### Your Mission
Document the complete system (WF1-7) to enable uniform code, easy understanding, and extendability.

### Approach
1. **Follow the investigation starting points** - Use grep/find commands provided
2. **Read actual code** - Don't guess, verify everything
3. **Match WF4-7 quality** - Use existing docs as template
4. **Document patterns, not just facts** - Show how things work
5. **Include real code examples** - With file paths and line numbers
6. **Think about extensibility** - How would someone add to this?

### Phase Order
1. **Phase 1 first** - WF1-3 documentation (foundation)
2. **Phase 2 second** - Extensibility patterns (building on foundation)
3. **Phase 3 last** - Verification and polish

### Quality Bar
- Same standard as WF4-7 documentation
- 100% code verification
- Real examples with line numbers
- Patterns, not just descriptions
- Honest about gaps

### Questions to Answer
- How does data flow from WF1 → WF7?
- What patterns are consistent across all workflows?
- What patterns are unique to specific workflows?
- How would someone add a direct submission endpoint?
- How would someone add a new workflow?

---

## Time Estimate Breakdown

| Phase | Task | Hours |
|-------|------|-------|
| 1.1 | WF1 Documentation | 3 |
| 1.2 | WF2 Documentation | 2 |
| 1.3 | WF3 Documentation | 3 |
| 2.1 | Direct Submission Patterns | 2 |
| 2.2 | New Workflow Pattern | 2 |
| 2.3 | WF6 Clarification | 0.5 |
| 2.4 | Cross-Workflow Patterns | 1.5 |
| 3.1 | Code Verification | 1 |
| 3.2 | Cross-Reference Updates | 1 |
| **Total** | | **16 hours** |

---

## Priority Justification

**P0 (Critical) because:**
- Blocks achieving uniform code across all workflows
- Blocks understanding complete data flow
- Blocks adding new entry points (direct submission)
- Foundation for all future development
- Required for onboarding new developers

**This is the natural next step after WO-005** - We have the foundation (WF4-7), now complete the picture (WF1-3) and enable extension.

---

## Expected Outcome

After WO-007 completion:
- ✅ Complete WF1→WF7 documentation
- ✅ Uniform patterns across all workflows
- ✅ Clear extensibility patterns
- ✅ Any developer can add new entry points
- ✅ Any developer can add new workflows
- ✅ System fully documented and extendable

**This enables the next phase:** Implementing uniform patterns across all workflows, adding direct submission endpoints, and extending the system with confidence.

---

**Status:** Ready for Claude to execute. All investigation starting points provided. Quality bar set by WF4-7 docs.
