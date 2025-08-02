# ScraperSky Standardization Master Workflow

## Overall Progress Tracker

**Instructions for AI Assistant:** We are proceeding through this master workflow phase by phase, as per our agreed strategy (completing all of Phase 1 before starting Phase 2). Upon starting a new session and reading this document, please first consult the 'Current Operational Phase' table below and state your understanding of our current position.

**Current Operational Phase:**

| Phase Description                                    | Status      |
| :--------------------------------------------------- | :---------- |
| **Phase 1: Cheat Sheet Creation (All WFs: WF1-WF7)** | **Complete**|
| Phase 2: Layer-by-Layer Audit (Layer 4: Services)    | **Active**  |
| Phase 2: Layer-by-Layer Audit (Layer 1: Models)      | To Do       |
| Phase 2: Layer-by-Layer Audit (Layer 2: Schemas)     | To Do       |
| Phase 2: Layer-by-Layer Audit (Layer 3: Routers)     | To Do       |
| Phase 2: Layer-by-Layer Audit (Layer 5: Config)      | To Do       |
| Phase 2: Layer-by-Layer Audit (Layer 6: UI)          | To Do       |
| Phase 2: Layer-by-Layer Audit (Layer 7: Testing)     | To Do       |
| Phase 3: Cross-Workflow Analysis & Pattern Review    | To Do       |

_(This table will be updated as we complete each major phase/sub-phase)._

This document outlines the complete process for standardizing the ScraperSky codebase workflow by workflow, starting with WF1-SingleSearch.

## Key Principles

- Document-First: Complete documentation before changing code
- Zero Assumptions: Never proceed if information is ambiguous
- One Section at a Time: Work methodically through each component
- Review Gates: Verify each section before proceeding
- **Layered Documentation Strategy**: For each architectural layer, our audit and standardization process will be guided by two key documents:
  - `Layer-X-{LayerName}_Blueprint.md`: This document defines the architectural standard, quality bar, and "what good looks like" for the layer. It is the definitive reference for compliance.
  - `Layer-X-{LayerName}_AI_Audit_SOP.md`: This document is a Standard Operating Procedure specifically for AI assistants, detailing the step-by-step process to audit the layer against its Blueprint and populate the workflow-specific cheat sheet.

**Overarching Strategy Note:** We will complete Phase 1 (Cheat Sheet creation and assessment) for all workflows (WF1 through WF7) before commencing any Phase 2 (Layer-by-Layer Audit) activities. This 'breadth-first' documentation approach provides a comprehensive understanding of the system-wide technical debt landscape. In Phase 2, we will systematically audit each architectural layer across all workflows, rather than auditing entire workflows one by one.

## Current Status

- Active Phase: Layer-by-Layer Audit (Phase 2)
- Current Layer: Layer 4 (Services)
- Current Activity: Analyzing service implementations across all workflows
- Progress: Gathering information about implementation patterns and technical debt

### Automation hint

Windsurf: after updating a cheat-sheet progress counter, reflect the same "Progress" value here.

## Reference Documents

- Draft Work Order: Docs/Docs_5_Project_Working_Docs/52-Gold-Standard-Blue-Print/52.0-Draft-Work-Order.md
- Conventions Guide: Docs/Docs_6_Architecture_and_Status/CONVENTIONS_AND_PATTERNS_GUIDE.md
- Q&A Insights: Docs/Docs_6_Architecture_and_Status/Q&A_Key_Insights.md
- AI Constitution: Docs/Docs_8_Document-X/8.0-AI-COLLABORATION-CONSTITUTION.md
- Cheat Sheet Template: Docs/Docs_8_Document-X/Audit_And_Refactor_Workflow_Cheat_Sheet_TEMPLATE.md

## Phase 0: Setup & Preparation

### Task 0.1: Save This Master Workflow Document

Save this document for reference throughout the standardization process.

### Task 0.2: Prime Windsurf with Key Documents

```
Windsurf, I need you to read these key documents to understand our codebase standardization project:

1. Docs/Docs_5_Project_Working_Docs/52-Gold-Standard-Blue-Print/52.0-Draft-Work-Order.md
2. Docs/Docs_6_Architecture_and_Status/CONVENTIONS_AND_PATTERNS_GUIDE.md
3. Docs/Docs_6_Architecture_and_Status/Q&A_Key_Insights.md
4. Docs/Docs_8_Document-X/8.0-AI-COLLABORATION-CONSTITUTION.md
5. Docs/Docs_8_Document-X/Audit_And_Refactor_Workflow_Cheat_Sheet_TEMPLATE.md
```

### Task 0.3: Create Template Snapshot

```
Windsurf, please create an immutable template snapshot by copying:
Docs/Docs_8_Document-X/Audit_And_Refactor_Workflow_Cheat_Sheet_TEMPLATE.md
to:
Docs/Docs_8_Document-X/_archive/Cheat_Sheet_TEMPLATE_v1_$(git rev-parse --short HEAD).md

This preserves the exact Git commit hash in the filename for future reference.
```

## Phase 1: WF1-SingleSearch Cheat Sheet Creation

**Layer-by-Layer Audit Process (Phase 2):** In Phase 2, we audit each architectural layer across all workflows systematically. For each layer:

1. **Layer Report Creation:** Create a dedicated Layer Report document (`Layer-X-{LayerName}_Audit_Report.md`) that will serve as the consolidated findings document.

2. **Cross-Workflow Analysis:** For each workflow (WF1-WF7):
   - Review the corresponding sections in the workflow's cheat sheet
   - Use the layer's Blueprint (`Layer-X-{LayerName}_Blueprint.md`) and SOP (`Layer-X-{LayerName}_AI_Audit_SOP.md`) as reference
   - Analyze the actual code implementation
   - Document findings in BOTH the workflow cheat sheet AND the layer report
   - Include full file paths in both documents for clear reference

3. **Good Pattern Identification:** Throughout the audit, identify implementations that follow the CONVENTIONS_AND_PATTERNS_GUIDE.md with no technical debt. These will be highlighted in the Layer Report as exemplary patterns to follow in future remediation efforts.

4. **Code Mapping:** Each Layer Report will include a clear mapping between workflows and their code files at the top, plus detailed file paths in the workflow-specific sections.

5. **Future Remediation Planning:** The actual fixing of identified technical debt will be planned in a future phase after all Layer Reports are complete.

We will begin with Layer 4 (Services) as it provides critical context for understanding other layers. The format established for the Layer 4 report will serve as a template for subsequent layer reports.

### Task 1.1: Prioritized - Complete Layer 4 (Services Audit)

```
Windsurf, assume Technical Lead role for WF1 section 2.4 (Layer 4: Services).

Following the procedure in `Docs/Docs_10_Final_Audit/Layer-4-Services_AI_Audit_SOP.md` (which uses `Docs/Docs_10_Final_Audit/Layer-4-Services_Blueprint.md` as the standard), please complete section 2.4 (Layer 4: Services) of the Docs/Docs_10_Final_Audit/WF1-SingleSearch_Cheat_Sheet.md.

If Docs/Docs_10_Final_Audit/WF1-SingleSearch_Cheat_Sheet.md already exists, update only section 2.4; do NOT modify previous sections unless instructed.

1. Analyze:
   - src/services/places/places_search_service.py
   - src/services/places/places_service.py
   - src/services/places/places_storage_service.py
2. Document current state in the cheat sheet, especially noting:
   - SCRSKY-225: Raw SQL in storage service
   - SCRSKY-226: Hardcoded connection parameters
   - SCRSKY-251: Missing error handling for API failures
3. Compare with standards in CONVENTIONS_AND_PATTERNS_GUIDE.md and Q&A_Key_Insights.md
4. Identify gaps and prescribed refactoring actions
5. Set status to "To Do" for all items in this section

If any gap analysis item is unclear, insert <!-- NEED_CLARITY --> in that row and await my response instead of choosing "best guess".

After updating the cheat-sheet progress counter for this section, also update the "Progress:" line in this Master Workflow doc.

Add <!-- STOP_FOR_REVIEW --> when you've completed this section.

After reaching this point:
```

git add Docs/Docs_10_Final_Audit/WF1-SingleSearch_Cheat_Sheet.md
git commit -m "WF1 2.4 (Layer 4 Services - Prioritized) draft (awaiting review)" --no-verify

```

**ACTION REQUIRED**: Review section 2.4 (Layer 4) content and provide feedback.

### Task 1.2: Complete Layer 1 (Models & ENUMs)

```

Windsurf, assume Technical Lead role for WF1 section 2.1 (Layer 1: Models & ENUMs).

Now, based on insights from the Layer 4 audit (if any) and the reference documents, please complete section 2.1 (Layer 1: Models & ENUMs) of Docs/Docs_10_Final_Audit/WF1-SingleSearch_Cheat_Sheet.md.

If Docs/Docs_10_Final_Audit/WF1-SingleSearch_Cheat_Sheet.md already exists, update only section 2.1.

Complete section 2.1 (Layer 1: Models & ENUMs):

1. Analyze src/models/place_search.py and src/models/place.py
2. Document the current state in the cheat sheet
3. Compare with the standards in the relevant blueprint.
4. Identify gaps and prescribed refactoring actions
5. Set status to "To Do" for all items

Note: For source table, use "place_search" as this is the primary model for WF1-SingleSearch.

If any gap analysis item is unclear (including pre-existing ones like the one for place.py), insert <!-- NEED_CLARITY --> in that row and await my response.

After updating the cheat-sheet progress counter, also update the "Progress:" line in this Master Workflow doc.

Add <!-- STOP_FOR_REVIEW --> when you've completed this section.

After reaching this point:

```

git add Docs/Docs_10_Final_Audit/WF1-SingleSearch_Cheat_Sheet.md
git commit -m "WF1 2.1 (Layer 1 Models) draft (awaiting review)" --no-verify

```

**ACTION REQUIRED**: Review section 2.1 content and provide feedback.

### Task 1.3: Complete Layer 2 (Schemas)

```
Windsurf, assume Technical Lead role for WF1 section 2.2 (Layer 2: Schemas).

Now please complete section 2.2 (Layer 2: Schemas) of the Docs/Docs_10_Final_Audit/WF1-SingleSearch_Cheat_Sheet.md.

If Docs/Docs_10_Final_Audit/WF1-SingleSearch_Cheat_Sheet.md already exists, update only section 2.2.

1. Identify all schema files relevant to WF1-SingleSearch
2. Document their current state
3. Compare with standards
4. Prescribe necessary refactoring actions
5. Set status to "To Do" for all items

If any gap analysis item is unclear, insert <!-- NEED_CLARITY --> in that row and await my response.

After updating the cheat-sheet progress counter, also update the "Progress:" line in this Master Workflow doc.

Add <!-- STOP_FOR_REVIEW --> when done.

After reaching this point:
```

git add Docs/Docs_10_Final_Audit/WF1-SingleSearch_Cheat_Sheet.md
git commit -m "WF1 2.2 (Layer 2 Schemas) draft (awaiting review)" --no-verify

```

**ACTION REQUIRED**: Review section 2.2 content and provide feedback.

### Task 1.4: Complete Layer 3 (Routers)

```

Windsurf, assume Technical Lead role for WF1 section 2.3 (Layer 3: Routers).

Now please complete section 2.3 (Layer 3: Routers) of the Docs/Docs_10_Final_Audit/WF1-SingleSearch_Cheat_Sheet.md.

If Docs/Docs_10_Final_Audit/WF1-SingleSearch_Cheat_Sheet.md already exists, update only section 2.3.

1. Analyze src/routers/google_maps_api.py
2. Document current state, especially noting SCRSKY-250 (missing transaction boundary)
3. Compare with standards
4. Prescribe necessary refactoring actions
5. Set status to "To Do" for all items

If any gap analysis item is unclear, insert <!-- NEED_CLARITY --> in that row and await my response.

After updating the cheat-sheet progress counter, also update the "Progress:" line in this Master Workflow doc.

Add <!-- STOP_FOR_REVIEW --> when done.

After reaching this point:

```

git add Docs/Docs_10_Final_Audit/WF1-SingleSearch_Cheat_Sheet.md
git commit -m "WF1 2.3 (Layer 3 Routers) draft (awaiting review)" --no-verify

```

**ACTION REQUIRED**: Review section 2.3 content and provide feedback.

### Task 1.5: Complete Layer 5 (Configuration)

```
Windsurf, assume Technical Lead role for WF1 section 2.5 (Layer 5: Configuration).

Now please complete section 2.5 (Layer 5: Configuration) of the Docs/Docs_10_Final_Audit/WF1-SingleSearch_Cheat_Sheet.md.

If Docs/Docs_10_Final_Audit/WF1-SingleSearch_Cheat_Sheet.md already exists, update only section 2.5.

1. Analyze environment variables and settings for WF1-SingleSearch
2. Document current state
3. Compare with standards
4. Prescribe necessary refactoring actions
5. Set status to "To Do" for all items

If any gap analysis item is unclear, insert <!-- NEED_CLARITY --> in that row and await my response.

After updating the cheat-sheet progress counter, also update the "Progress:" line in this Master Workflow doc.

Add <!-- STOP_FOR_REVIEW --> when done.

After reaching this point:
```

git add Docs/Docs_10_Final_Audit/WF1-SingleSearch_Cheat_Sheet.md
git commit -m "WF1 2.5 (Layer 5 Config) draft (awaiting review)" --no-verify

```

**ACTION REQUIRED**: Review section 2.5 content and provide feedback.

### Task 1.6: Complete Layer 6 (UI Components)

```

Windsurf, assume Technical Lead role for WF1 section 2.6 (Layer 6: UI Components).

Now please complete section 2.6 (Layer 6: UI Components) of the Docs/Docs_10_Final_Audit/WF1-SingleSearch_Cheat_Sheet.md.

If Docs/Docs_10_Final_Audit/WF1-SingleSearch_Cheat_Sheet.md already exists, update only section 2.6.

1. Analyze:
   - static/js/single-search-tab.js
   - Related HTML templates
2. Document current state
3. Compare with standards
4. Prescribe necessary refactoring actions
5. Set status to "To Do" for all items

If any gap analysis item is unclear, insert <!-- NEED_CLARITY --> in that row and await my response.

After updating the cheat-sheet progress counter, also update the "Progress:" line in this Master Workflow doc.

Add <!-- STOP_FOR_REVIEW --> when done.

After reaching this point:

```

git add Docs/Docs_10_Final_Audit/WF1-SingleSearch_Cheat_Sheet.md
git commit -m "WF1 2.6 (Layer 6 UI) draft (awaiting review)" --no-verify

```

**ACTION REQUIRED**: Review section 2.6 content and provide feedback.

### Task 1.7: Complete Layer 7 (Testing)

```
Windsurf, assume Technical Lead role for WF1 section 2.7 (Layer 7: Testing).

Now please complete section 2.7 (Layer 7: Testing) of the Docs/Docs_10_Final_Audit/WF1-SingleSearch_Cheat_Sheet.md.

If Docs/Docs_10_Final_Audit/WF1-SingleSearch_Cheat_Sheet.md already exists, update only section 2.7.

1. Analyze existing tests for WF1-SingleSearch
2. Document current state
3. Compare with standards
4. Prescribe necessary refactoring actions
5. Set status to "To Do" for all items

If any gap analysis item is unclear, insert <!-- NEED_CLARITY --> in that row and await my response.

After updating the cheat-sheet progress counter, also update the "Progress:" line in this Master Workflow doc.

Add <!-- STOP_FOR_REVIEW --> when done.

After reaching this point:
```

git add Docs/Docs_10_Final_Audit/WF1-SingleSearch_Cheat_Sheet.md
git commit -m "WF1 2.7 (Layer 7 Testing) draft (awaiting review)" --no-verify

```

**ACTION REQUIRED**: Review section 2.7 content and provide feedback.

### Task 1.8: Finalize Cheat Sheet

```

Windsurf, assume Technical Lead role for WF1 finalization.

Please review the entire Docs/Docs_10_Final_Audit/WF1-SingleSearch_Cheat_Sheet.md for consistency and completeness.

1. Create a final section "Implementation Priority Order" that lists:

   - High priority items (technical debt)
   - Logical dependencies between changes
   - Recommended implementation sequence

2. Create a simple shell script at scripts/ci/wf1-lint.sh with the following content:
   ```bash
   #!/usr/bin/env bash
   set -e
   pytest tests/workflows/wf1  # or your exact path
   ruff src/models src/routers src/services
   echo "WF1 READY"
   ```

```

Also run:

```

chmod +x scripts/ci/wf1-lint.sh

```

to make it executable

3. Update the progress at the top to "Progress: 7/7 sections completed, ready for implementation"

Add <!-- STOP_FOR_REVIEW --> when done.

```

git add Docs/Docs_10_Final_Audit/WF1-SingleSearch_Cheat_Sheet.md scripts/ci/wf1-lint.sh
git commit -m "WF1 final cheat sheet and lint script (awaiting review)" --no-verify

```

**ACTION REQUIRED**: Review finalized cheat sheet and approve for implementation.

## Phase 2: WF1-SingleSearch Implementation

### Task 2.1: Begin Implementation of High-Priority Items

```

Windsurf, switch to Developer role (do not edit documentation) for WF1 implementation.

Let's begin implementing the changes documented in the cheat sheet. Start with the highest priority item:

1. Show me exactly what changes you plan to make
2. Run pre-commit hooks with:
   pre-commit run --files $(git diff --name-only HEAD)
3. Paste the console output
4. Await my approval before proceeding

After implementation:

1. Update the status in the cheat sheet to "Done"
2. Verify against the checklist

If Docs/Docs_10_Final_Audit/WF1-SingleSearch_Cheat_Sheet.md already exists, update only the status fields; do NOT modify the content unless instructed.

```

**ACTION REQUIRED**: Review proposed changes and approve implementation.

### Task 2.2-2.X: Continue Implementation

Repeat Task 2.1 format for each refactoring item identified in the Implementation Priority Order section.

### Task 2.Y: Final Verification

```

Windsurf, switch to Developer role (do not edit documentation) for WF1 verification.

Please run the scripts/ci/wf1-lint.sh script and verify all tests pass.

Then update the Docs/Docs_10_Final_Audit/WF1-SingleSearch_Cheat_Sheet.md to mark the workflow as completed.

On success, open a pull request from feature/wf1-standardization to main with the title "WF1 Standardization: Models-to-Tests" and paste the PR URL here.

```

**ACTION REQUIRED**: Verify successful completion of WF1-SingleSearch standardization.

## Phase 3: Next Workflow Standardization (WF2-StagingEditor)

**Strategic Note on Layer Prioritization for Phase 1 (repeated for all workflows):** To better inform the analysis of all architectural layers, we will begin Phase 1 for each workflow by first auditing Layer 4 (Services). The understanding gained from the service layer's logic and data handling will provide critical context for subsequently auditing Models, Schemas, Routers, and other components. The AI assistant should follow the `Docs/Docs_10_Final_Audit/Layer-4-Services_AI_Audit_SOP.md`, which references the `Docs/Docs_10_Final_Audit/Layer-4-Services_Blueprint.md` as the definitive standard.

### Task 3.1: Prioritized - Complete Layer 4 (Services Audit) for WF2

```

Windsurf, assume Technical Lead role for WF2 section 2.4 (Layer 4: Services).

Let's begin standardizing WF2-StagingEditor.
Following the procedure in `Docs/Docs_10_Final_Audit/Layer-4-Services_AI_Audit_SOP.md` (which uses `Docs/Docs_10_Final_Audit/Layer-4-Services_Blueprint.md` as the standard), please complete section 2.4 (Layer 4: Services) of Docs/Docs_10_Final_Audit/WF2-StagingEditor_Cheat_Sheet.md.

**To create the cheat sheet:** If `Docs/Docs_10_Final_Audit/WF2-StagingEditor_Cheat_Sheet.md` does not exist, copy the content from the master template at `Docs/Docs_8_Document-X/_archive/Cheat_Sheet_TEMPLATE_v1_c5660e3.md` into the new `WF2-StagingEditor_Cheat_Sheet.md` file. Then, update only section 2.4 as per this task.

If Docs/Docs_10_Final_Audit/WF2-StagingEditor_Cheat_Sheet.md already exists, update only section 2.4.

1. Identify and analyze relevant service files for WF2-StagingEditor (refer to workflow-comparison-structured.yaml and canonical workflow docs for WF2 if needed)
2. Document current state in the cheat sheet
3. Compare with standards
4. Prescribe necessary refactoring actions
5. Set status to "To Do" for all items in this section

If any gap analysis item is unclear, insert <!-- NEED_CLARITY --> in that row and await my response.

After updating the cheat-sheet progress counter, also update the "Progress:" line in this Master Workflow doc.

Add <!-- STOP_FOR_REVIEW --> when done.

After reaching this point:

```
git add Docs/Docs_10_Final_Audit/WF2-StagingEditor_Cheat_Sheet.md
git commit -m "WF2 2.4 (Layer 4 Services - Prioritized) draft (awaiting review)" --no-verify
```

**ACTION REQUIRED**: Review section 2.4 (WF2 Layer 4) content and provide feedback.

### Task 3.2: Complete Layer 1 (Models & ENUMs) for WF2

```
Windsurf, assume Technical Lead role for WF2 section 2.1 (Layer 1: Models & ENUMs).

Now, please complete section 2.1 (Layer 1: Models & ENUMs) of Docs/Docs_10_Final_Audit/WF2-StagingEditor_Cheat_Sheet.md.

If Docs/Docs_10_Final_Audit/WF2-StagingEditor_Cheat_Sheet.md already exists, update only section 2.1.

1. Identify and analyze relevant model and enum files for WF2-StagingEditor
2. Document their current state
3. Compare with standards
4. Prescribe necessary refactoring actions
5. Set status to "To Do" for all items

If any gap analysis item is unclear, insert <!-- NEED_CLARITY --> in that row and await my response.

After updating the cheat-sheet progress counter, also update the "Progress:" line in this Master Workflow doc.

Add <!-- STOP_FOR_REVIEW --> when done.

After reaching this point:
```

git add Docs/Docs_10_Final_Audit/WF2-StagingEditor_Cheat_Sheet.md
git commit -m "WF2 2.1 (Layer 1 Models) draft (awaiting review)" --no-verify

```

**ACTION REQUIRED**: Review section 2.1 (WF2 Layer 1) content and provide feedback.

### Task 3.3: Complete Layer 2 (Schemas) for WF2

```

Windsurf, assume Technical Lead role for WF2 section 2.2 (Layer 2: Schemas).

Now please complete section 2.2 (Layer 2: Schemas) of the Docs/Docs_10_Final_Audit/WF2-StagingEditor_Cheat_Sheet.md.

If Docs/Docs_10_Final_Audit/WF2-StagingEditor_Cheat_Sheet.md already exists, update only section 2.2.

1. Identify all schema files relevant to WF2-StagingEditor
2. Document their current state
3. Compare with standards
4. Prescribe necessary refactoring actions
5. Set status to "To Do" for all items

If any gap analysis item is unclear, insert <!-- NEED_CLARITY --> in that row and await my response.

After updating the cheat-sheet progress counter, also update the "Progress:" line in this Master Workflow doc.

Add <!-- STOP_FOR_REVIEW --> when done.

After reaching this point:

```
git add Docs/Docs_10_Final_Audit/WF2-StagingEditor_Cheat_Sheet.md
git commit -m "WF2 2.2 (Layer 2 Schemas) draft (awaiting review)" --no-verify
```

**ACTION REQUIRED**: Review section 2.2 (WF2 Layer 2) content and provide feedback.

### Task 3.4: Complete Layer 3 (Routers) for WF2

```
Windsurf, assume Technical Lead role for WF2 section 2.3 (Layer 3: Routers).

Now please complete section 2.3 (Layer 3: Routers) of the Docs/Docs_10_Final_Audit/WF2-StagingEditor_Cheat_Sheet.md.

If Docs/Docs_10_Final_Audit/WF2-StagingEditor_Cheat_Sheet.md already exists, update only section 2.3.

1. Identify and analyze relevant router files for WF2-StagingEditor
2. Document current state
3. Compare with standards
4. Prescribe necessary refactoring actions
5. Set status to "To Do" for all items

If any gap analysis item is unclear, insert <!-- NEED_CLARITY --> in that row and await my response.

After updating the cheat-sheet progress counter, also update the "Progress:" line in this Master Workflow doc.

Add <!-- STOP_FOR_REVIEW --> when done.

After reaching this point:
```

git add Docs/Docs_10_Final_Audit/WF2-StagingEditor_Cheat_Sheet.md
git commit -m "WF2 2.3 (Layer 3 Routers) draft (awaiting review)" --no-verify

```

**ACTION REQUIRED**: Review section 2.3 (WF2 Layer 3) content and provide feedback.

### Task 3.5: Complete Layer 5 (Configuration) for WF2

```

Windsurf, assume Technical Lead role for WF2 section 2.5 (Layer 5: Configuration).

Now please complete section 2.5 (Layer 5: Configuration) of the Docs/Docs_10_Final_Audit/WF2-StagingEditor_Cheat_Sheet.md.

If Docs/Docs_10_Final_Audit/WF2-StagingEditor_Cheat_Sheet.md already exists, update only section 2.5.

1. Analyze environment variables and settings for WF2-StagingEditor
2. Document current state
3. Compare with standards
4. Prescribe necessary refactoring actions
5. Set status to "To Do" for all items

If any gap analysis item is unclear, insert <!-- NEED_CLARITY --> in that row and await my response.

After updating the cheat-sheet progress counter, also update the "Progress:" line in this Master Workflow doc.

Add <!-- STOP_FOR_REVIEW --> when done.

After reaching this point:

```
git add Docs/Docs_10_Final_Audit/WF2-StagingEditor_Cheat_Sheet.md
git commit -m "WF2 2.5 (Layer 5 Config) draft (awaiting review)" --no-verify
```

**ACTION REQUIRED**: Review section 2.5 (WF2 Layer 5) content and provide feedback.

### Task 3.6: Complete Layer 6 (UI Components) for WF2

```
Windsurf, assume Technical Lead role for WF2 section 2.6 (Layer 6: UI Components).

Now please complete section 2.6 (Layer 6: UI Components) of the Docs/Docs_10_Final_Audit/WF2-StagingEditor_Cheat_Sheet.md.

If Docs/Docs_10_Final_Audit/WF2-StagingEditor_Cheat_Sheet.md already exists, update only section 2.6.

1. Identify and analyze relevant UI component files (JS, HTML templates) for WF2-StagingEditor
2. Document current state
3. Compare with standards
4. Prescribe necessary refactoring actions
5. Set status to "To Do" for all items

If any gap analysis item is unclear, insert <!-- NEED_CLARITY --> in that row and await my response.

After updating the cheat-sheet progress counter, also update the "Progress:" line in this Master Workflow doc.

Add <!-- STOP_FOR_REVIEW --> when done.

After reaching this point:
```

git add Docs/Docs_10_Final_Audit/WF2-StagingEditor_Cheat_Sheet.md
git commit -m "WF2 2.6 (Layer 6 UI) draft (awaiting review)" --no-verify

```

**ACTION REQUIRED**: Review section 2.6 (WF2 Layer 6) content and provide feedback.

### Task 3.7: Complete Layer 7 (Testing) for WF2

```

Windsurf, assume Technical Lead role for WF2 section 2.7 (Layer 7: Testing).

Now please complete section 2.7 (Layer 7: Testing) of the Docs/Docs_10_Final_Audit/WF2-StagingEditor_Cheat_Sheet.md.

If Docs/Docs_10_Final_Audit/WF2-StagingEditor_Cheat_Sheet.md already exists, update only section 2.7.

1. Analyze existing tests for WF2-StagingEditor
2. Document current state
3. Compare with standards
4. Prescribe necessary refactoring actions
5. Set status to "To Do" for all items

If any gap analysis item is unclear, insert <!-- NEED_CLARITY --> in that row and await my response.

After updating the cheat-sheet progress counter, also update the "Progress:" line in this Master Workflow doc.

Add <!-- STOP_FOR_REVIEW --> when done.

After reaching this point:

```
git add Docs/Docs_10_Final_Audit/WF2-StagingEditor_Cheat_Sheet.md
git commit -m "WF2 2.7 (Layer 7 Testing) draft (awaiting review)" --no-verify
```

**ACTION REQUIRED**: Review section 2.7 (WF2 Layer 7) content and provide feedback.

### Task 3.8: Finalize WF2 Cheat Sheet

````
Windsurf, assume Technical Lead role for WF2 finalization.

Please review the entire Docs/Docs_10_Final_Audit/WF2-StagingEditor_Cheat_Sheet.md for consistency and completeness.

1. Create a final section "Implementation Priority Order" that lists:

   - High priority items (technical debt)
   - Logical dependencies between changes
   - Recommended implementation sequence

2. Create a simple shell script at scripts/ci/wf2-lint.sh with the following content:

   ```bash
   #!/usr/bin/env bash
   set -e
   pytest tests/workflows/wf2  # or your exact path for WF2
   ruff src/models src/routers src/services # Adjust paths if WF2 affects different areas
   echo "WF2 READY"
````

```

Also run:

```

chmod +x scripts/ci/wf2-lint.sh

```

```
