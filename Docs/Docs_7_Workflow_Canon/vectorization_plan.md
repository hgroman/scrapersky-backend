# Document Vectorization Priority Plan
## Implementing v_ Naming Convention for Consumption Order

**Document Status:** DRAFT - Pending Local AI Review  
**Created:** 2025-01-07  
**Purpose:** Establish naming convention to indicate document consumption priority while preserving historical structure

---

## Executive Summary

This plan implements a `v_` prefixed naming convention to indicate document consumption priority without reorganizing the existing directory structure. Documents retain their current locations but receive new names that explicitly communicate their reading order for human developers and AI partners.

## The Problem We're Solving

- **Discovery Issue:** Critical documents are buried in subdirectories
- **Priority Confusion:** No clear indication of what to read first
- **AI Vectorization Ambiguity:** Unclear which documents are most important to process
- **Historical Preservation:** Need to maintain audit trail and structural integrity

## The Solution: Priority-Based Naming Convention

### Naming Pattern
```
v_{priority_number}_{descriptive_name}.{extension}
```

**Examples:**
- `v_0_QUICK_START_GUIDE.md` (new navigation document)
- `v_1_CONTEXT_GUIDE.md` (system philosophy)
- `v_4_PATTERN_COMPARISON.yaml` (workflow patterns)

### Benefits
- **Self-Organizing:** `ls v_*` shows consumption order automatically
- **AI-Friendly:** Clear directive: "Vectorize v_ files in numerical order"
- **History-Preserving:** Documents stay in original locations
- **Future-Proof:** New documents can be inserted with appropriate numbering

---

## Implementation Plan

### Phase 1: Core Document Renaming

**Priority 0-6: Essential Reading Path**

| Current Name | New Name | Location | Purpose |
|--------------|----------|----------|---------|
| *(new document)* | `v_0_QUICK_START_GUIDE.md` | `/root` | Navigation hub with essential reading order |
| `v_CONTEXT_GUIDE.md` | `v_1_CONTEXT_GUIDE.md` | `Template Resources/` | System philosophy and principles |
| `v_README Workflow Cannon.md` | `v_2_WORKFLOW_CANON_README.md` | `/root` | Master directory map and structure |
| *(locate in templates)* | `v_3_WORKFLOW_BUILDER_CHEAT_SHEET.md` | `Template Resources/` | Step-by-step implementation process |
| `workflow-comparison-structured.yaml` | `v_4_PATTERN_COMPARISON.yaml` | `/root` | Cross-workflow pattern analysis |
| `workflows/WF2-StagingEditor_CANONICAL.yaml` | `v_5_REFERENCE_IMPLEMENTATION_WF2.yaml` | `workflows/` | Gold standard workflow example |
| `Audit/2-evaluation_progress.yaml` | `v_6_SYSTEM_SCOPE_MAP.yaml` | `Audit/` | Complete file inventory and status |

### Phase 2: Secondary Document Renaming

**Priority 7+: Implementation References**

| Current Name | New Name | Location | Purpose |
|--------------|----------|----------|---------|
| `workflows/WF1-SingleSearch_CANONICAL.yaml` | `v_7_WF1_CANONICAL.yaml` | `workflows/` | Single Search workflow |
| `workflows/WF2-StagingEditor_CANONICAL.yaml` | `v_8_WF2_CANONICAL.yaml` | `workflows/` | Staging Editor Curation workflow |
| `workflows/WF3-LocalBusinessCuration_CANONICAL.yaml` | `v_9_WF3_CANONICAL.yaml` | `workflows/` | Local Business Curation workflow |
| `workflows/WF4-DomainCuration_CANONICAL.yaml` | `v_10_WF4_CANONICAL.yaml` | `workflows/` | Domain Curation workflow |
| `workflows/WF5-SitemapCuration_CANONICAL.yaml` | `v_11_WF5_CANONICAL.yaml` | `workflows/` | Sitemap Curation workflow |
| `workflows/WF6-SitemapImport_CANONICAL.yaml` | `v_12_WF6_CANONICAL.yaml` | `workflows/` | Sitemap Import workflow |
| `Audit/v_WORKFLOW_AUDIT_JOURNAL.md` | `v_13_AUDIT_JOURNAL.md` | `Audit/` | Compliance and issue tracking |
| `Audit/v_WORK_ORDER.md` | `v_14_WORK_ORDER.md` | `Audit/` | Current work tracking |

### Phase 3: Reference Update Process

**Step-by-Step Execution:**

1. **Rename Files** (one at a time to avoid confusion)
   ```bash
   # Example for first file
   mv "Template Resources/v_CONTEXT_GUIDE.md" "Template Resources/v_1_CONTEXT_GUIDE.md"
   ```

2. **Find and Update References**
   ```bash
   # Search for all references to old name
   grep -r "v_CONTEXT_GUIDE.md" .
   
   # Update each reference with new name
   # (Manual editing or sed commands)
   ```

3. **Verify No Broken Links**
   ```bash
   # Check that all internal links still work
   grep -r "v_1_CONTEXT_GUIDE.md" .
   ```

4. **Repeat for Each Document**

### Phase 4: Create Navigation Document

**New File: `v_0_QUICK_START_GUIDE.md`**

Content framework:
```markdown
# ScraperSky Workflow System: Essential Reading Path

## For Human Developers
Read documents v_1 through v_6 in order. Each builds on the previous.

## For AI Partners  
Vectorize all documents prefixed with v_ in numerical order.

## Essential Reading (v_1 to v_6)
1. [System Philosophy](path/to/v_1_CONTEXT_GUIDE.md)
2. [Directory Structure](v_2_WORKFLOW_CANON_README.md)
3. [Implementation Process](path/to/v_3_WORKFLOW_BUILDER_CHEAT_SHEET.md)
4. [Pattern Analysis](v_4_PATTERN_COMPARISON.yaml)
5. [Reference Example](workflows/v_5_REFERENCE_IMPLEMENTATION_WF2.yaml)
6. [System Scope](Audit/v_6_SYSTEM_SCOPE_MAP.yaml)

## Workflow References (v_7+)
Continue with additional v_ documents as needed for specific implementations.
```

---

## Expected Outcomes

### For Development Team
- **Zero-friction onboarding:** Clear reading path from v_0 → v_6
- **Reduced cognitive load:** No hunting through directories
- **Consistent understanding:** Everyone follows same learning path

### For AI Partners
- **Clear vectorization directive:** "Process v_ files in numerical order"
- **Priority awareness:** Higher numbered files are less critical
- **Efficient processing:** Focus effort on essential documents first

### For System Maintenance
- **Preserved audit trail:** All documents stay in historical locations
- **Scalable system:** New essential documents easily added as v_13+, v_14+
- **Simple updates:** Grep searches become trivial with consistent naming

---

## Risk Mitigation

**Potential Issues:**
- **Broken internal links:** Mitigated by systematic grep-and-replace process
- **Confusion during transition:** Mitigated by phased approach (rename core docs first)
- **Tool compatibility:** Mitigated by preserving file locations (only names change)

**Rollback Plan:**
- All renames are reversible since locations don't change
- Git history preserves original names
- Can revert individual files if issues arise

---

## Success Metrics

**Immediate (Post-Implementation):**
- [ ] All v_1 through v_6 documents accessible via clear path
- [ ] No broken internal references
- [ ] v_0 guide provides complete navigation

**Medium-term (30 days):**
- [ ] New team members can onboard using v_0 → v_6 path
- [ ] AI partners successfully vectorize documents in priority order
- [ ] Zero confusion about which documents are essential

**Long-term (90 days):**
- [ ] System scales cleanly with new v_numbered documents
- [ ] Historical audit value preserved
- [ ] Improved development velocity due to clearer documentation access

---

## Next Steps

1. **Get Local AI Feedback** on this plan
2. **Identify exact location** of workflow builder cheat sheet for v_3 naming
3. **Create backup** of current directory state
4. **Begin Phase 1** with v_1 (CONTEXT_GUIDE) rename and reference updates
5. **Test navigation** after each document rename
6. **Create v_0** guide once core documents are renamed

---

*This plan balances accessibility improvements with preservation of the historical and methodological value embedded in the current directory structure.*