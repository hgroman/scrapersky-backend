# ScraperSky Standardization Master Workflow

This document outlines the complete process for standardizing the ScraperSky codebase workflow by workflow, starting with WF1-SingleSearch.

## Key Principles

- Document-First: Complete documentation before changing code
- Zero Assumptions: Never proceed if information is ambiguous
- One Section at a Time: Work methodically through each component
- Review Gates: Verify each section before proceeding

## Current Status

- Active Workflow: WF1-SingleSearch
- Progress: Initial setup

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

### Task 1.1: Create Cheat Sheet & Complete Layer 1 (Models & ENUMs)

```
Windsurf, assume Technical Lead role for WF1 section 2.1 (Layer 1: Models & ENUMs).

Based on these documents, please create WF1-SingleSearch_Cheat_Sheet.md for the single_search workflow.

If WF1-SingleSearch_Cheat_Sheet.md already exists, update only section 2.1; do NOT modify previous sections unless instructed.

Complete section 2.1 (Layer 1: Models & ENUMs):
1. Analyze src/models/place_search.py and src/models/place.py
2. Document the current state in the cheat sheet
3. Compare with the standards in CONVENTIONS_AND_PATTERNS_GUIDE.md
4. Identify gaps and prescribed refactoring actions
5. Set status to "To Do" for all items

Note: For source table, use "place_search" as this is the primary model for WF1-SingleSearch.

If any gap analysis item is unclear, insert <!-- NEED_CLARITY --> in that row and await my response instead of choosing "best guess".

After updating the cheat-sheet progress counter, also update the "Progress:" line in this Master Workflow doc.

Add <!-- STOP_FOR_REVIEW --> when you've completed this section.

After reaching this point:
```

git add WF1-SingleSearch_Cheat_Sheet.md
git commit -m "WF1 2.1 draft (awaiting review)" --no-verify

```

```

**ACTION REQUIRED**: Review section 2.1 content and provide feedback.

### Task 1.2: Complete Layer 2 (Schemas)

```
Windsurf, assume Technical Lead role for WF1 section 2.2 (Layer 2: Schemas).

Now please complete section 2.2 (Layer 2: Schemas) of the WF1-SingleSearch_Cheat_Sheet.md.

If WF1-SingleSearch_Cheat_Sheet.md already exists, update only section 2.2; do NOT modify previous sections unless instructed.

1. Identify all schema files relevant to WF1-SingleSearch
2. Document their current state
3. Compare with standards
4. Prescribe necessary refactoring actions
5. Set status to "To Do" for all items

If any gap analysis item is unclear, insert <!-- NEED_CLARITY --> in that row and await my response instead of choosing "best guess".

After updating the cheat-sheet progress counter, also update the "Progress:" line in this Master Workflow doc.

After updating the cheat-sheet progress counter, also update the "Progress:" line in this Master Workflow doc.

Add <!-- STOP_FOR_REVIEW --> when done.

After reaching this point:
```

git add WF1-SingleSearch_Cheat_Sheet.md scripts/ci/wf1-lint.sh
git commit -m "WF1 final cheat sheet and lint script (awaiting review)" --no-verify

```

After reaching this point:
```

git add WF1-SingleSearch_Cheat_Sheet.md
git commit -m "WF1 2.2 draft (awaiting review)" --no-verify

```

```

**ACTION REQUIRED**: Review section 2.2 content and provide feedback.

### Task 1.3: Complete Layer 3 (Routers)

```
Windsurf, assume Technical Lead role for WF1 section 2.3 (Layer 3: Routers).

Now please complete section 2.3 (Layer 3: Routers) of the WF1-SingleSearch_Cheat_Sheet.md.

If WF1-SingleSearch_Cheat_Sheet.md already exists, update only section 2.3; do NOT modify previous sections unless instructed.

1. Analyze src/routers/google_maps_api.py
2. Document current state, especially noting SCRSKY-250 (missing transaction boundary)
3. Compare with standards
4. Prescribe necessary refactoring actions
5. Set status to "To Do" for all items

If any gap analysis item is unclear, insert <!-- NEED_CLARITY --> in that row and await my response instead of choosing "best guess".

After updating the cheat-sheet progress counter, also update the "Progress:" line in this Master Workflow doc.

Add <!-- STOP_FOR_REVIEW --> when done.

After reaching this point:
```

git add WF1-SingleSearch_Cheat_Sheet.md
git commit -m "WF1 2.3 draft (awaiting review)" --no-verify

```

```

**ACTION REQUIRED**: Review section 2.3 content and provide feedback.

### Task 1.4: Complete Layer 4 (Services)

```
Windsurf, assume Technical Lead role for WF1 section 2.4 (Layer 4: Services).

Now please complete section 2.4 (Layer 4: Services) of the WF1-SingleSearch_Cheat_Sheet.md.

If WF1-SingleSearch_Cheat_Sheet.md already exists, update only section 2.4; do NOT modify previous sections unless instructed.

1. Analyze:
   - src/services/places/places_search_service.py
   - src/services/places/places_service.py
   - src/services/places/places_storage_service.py
2. Document current state, especially noting:
   - SCRSKY-225: Raw SQL in storage service
   - SCRSKY-226: Hardcoded connection parameters
   - SCRSKY-251: Missing error handling for API failures
3. Compare with standards
4. Prescribe necessary refactoring actions
5. Set status to "To Do" for all items

If any gap analysis item is unclear, insert <!-- NEED_CLARITY --> in that row and await my response instead of choosing "best guess".

After updating the cheat-sheet progress counter, also update the "Progress:" line in this Master Workflow doc.

Add <!-- STOP_FOR_REVIEW --> when done.

After reaching this point:
```

git add WF1-SingleSearch_Cheat_Sheet.md
git commit -m "WF1 2.4 draft (awaiting review)" --no-verify

```

```

**ACTION REQUIRED**: Review section 2.4 content and provide feedback.

### Task 1.5: Complete Layer 5 (Configuration)

```
Windsurf, assume Technical Lead role for WF1 section 2.5 (Layer 5: Configuration).

Now please complete section 2.5 (Layer 5: Configuration) of the WF1-SingleSearch_Cheat_Sheet.md.

If WF1-SingleSearch_Cheat_Sheet.md already exists, update only section 2.5; do NOT modify previous sections unless instructed.

1. Analyze environment variables and settings for WF1-SingleSearch
2. Document current state
3. Compare with standards
4. Prescribe necessary refactoring actions
5. Set status to "To Do" for all items

If any gap analysis item is unclear, insert <!-- NEED_CLARITY --> in that row and await my response instead of choosing "best guess".

After updating the cheat-sheet progress counter, also update the "Progress:" line in this Master Workflow doc.

Add <!-- STOP_FOR_REVIEW --> when done.

After reaching this point:
```

git add WF1-SingleSearch_Cheat_Sheet.md
git commit -m "WF1 2.5 draft (awaiting review)" --no-verify

```

```

**ACTION REQUIRED**: Review section 2.5 content and provide feedback.

### Task 1.6: Complete Layer 6 (UI Components)

```
Windsurf, assume Technical Lead role for WF1 section 2.6 (Layer 6: UI Components).

Now please complete section 2.6 (Layer 6: UI Components) of the WF1-SingleSearch_Cheat_Sheet.md.

If WF1-SingleSearch_Cheat_Sheet.md already exists, update only section 2.6; do NOT modify previous sections unless instructed.

1. Analyze:
   - static/js/single-search-tab.js
   - Related HTML templates
2. Document current state
3. Compare with standards
4. Prescribe necessary refactoring actions
5. Set status to "To Do" for all items

If any gap analysis item is unclear, insert <!-- NEED_CLARITY --> in that row and await my response instead of choosing "best guess".

After updating the cheat-sheet progress counter, also update the "Progress:" line in this Master Workflow doc.

Add <!-- STOP_FOR_REVIEW --> when done.

After reaching this point:
```

git add WF1-SingleSearch_Cheat_Sheet.md
git commit -m "WF1 2.6 draft (awaiting review)" --no-verify

```

```

**ACTION REQUIRED**: Review section 2.6 content and provide feedback.

### Task 1.7: Complete Layer 7 (Testing)

```
Windsurf, assume Technical Lead role for WF1 section 2.7 (Layer 7: Testing).

Now please complete section 2.7 (Layer 7: Testing) of the WF1-SingleSearch_Cheat_Sheet.md.

If WF1-SingleSearch_Cheat_Sheet.md already exists, update only section 2.7; do NOT modify previous sections unless instructed.

1. Analyze existing tests for WF1-SingleSearch
2. Document current state
3. Compare with standards
4. Prescribe necessary refactoring actions
5. Set status to "To Do" for all items

If any gap analysis item is unclear, insert <!-- NEED_CLARITY --> in that row and await my response instead of choosing "best guess".

After updating the cheat-sheet progress counter, also update the "Progress:" line in this Master Workflow doc.

Add <!-- STOP_FOR_REVIEW --> when done.

After reaching this point:
```

git add WF1-SingleSearch_Cheat_Sheet.md
git commit -m "WF1 2.7 draft (awaiting review)" --no-verify

```

```

**ACTION REQUIRED**: Review section 2.7 content and provide feedback.

### Task 1.8: Finalize Cheat Sheet

````
Windsurf, assume Technical Lead role for WF1 finalization.

Please review the entire WF1-SingleSearch_Cheat_Sheet.md for consistency and completeness.

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
````

Also run:

```
chmod +x scripts/ci/wf1-lint.sh
```

to make it executable

3. Update the progress at the top to "Progress: 7/7 sections completed, ready for implementation"

Add <!-- STOP_FOR_REVIEW --> when done.

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

If WF1-SingleSearch_Cheat_Sheet.md already exists, update only the status fields; do NOT modify the content unless instructed.

```

**ACTION REQUIRED**: Review proposed changes and approve implementation.

### Task 2.2-2.X: Continue Implementation
Repeat Task 2.1 format for each refactoring item identified in the Implementation Priority Order section.

### Task 2.Y: Final Verification
```

Windsurf, switch to Developer role (do not edit documentation) for WF1 verification.

Please run the scripts/ci/wf1-lint.sh script and verify all tests pass.

Then update the WF1-SingleSearch_Cheat_Sheet.md to mark the workflow as completed.

On success, open a pull request from feature/wf1-standardization to main with the title "WF1 Standardization: Models-to-Tests" and paste the PR URL here.

```

**ACTION REQUIRED**: Verify successful completion of WF1-SingleSearch standardization.

## Phase 3: Next Workflow Standardization (WF2-StagingEditor)

### Task 3.1: Create WF2 Cheat Sheet & Complete Layer 1 (Models & ENUMs)
```

Windsurf, assume Technical Lead role for WF2 section 2.1 (Layer 1: Models & ENUMs).

Let's begin standardizing WF2-StagingEditor.

Please create WF2-StagingEditor_Cheat_Sheet.md and complete section 2.1 (Layer 1: Models & ENUMs).

If WF2-StagingEditor_Cheat_Sheet.md already exists, update only section 2.1; do NOT modify previous sections unless instructed.

If any gap analysis item is unclear, insert <!-- NEED_CLARITY --> in that row and await my response instead of choosing "best guess".

After updating the cheat-sheet progress counter, also update the "Progress:" line in this Master Workflow doc.

Add <!-- STOP_FOR_REVIEW --> when done.

After reaching this point:

```
git add WF2-StagingEditor_Cheat_Sheet.md
git commit -m "WF2 2.1 draft (awaiting review)" --no-verify
```

```

**ACTION REQUIRED**: Review section 2.1 (WF2) content and provide feedback.

### Task 3.2: Complete Layer 2 (Schemas) for WF2
```

Windsurf, assume Technical Lead role for WF2 section 2.2 (Layer 2: Schemas).

Now please complete section 2.2 (Layer 2: Schemas) of the WF2-StagingEditor_Cheat_Sheet.md.

If WF2-StagingEditor_Cheat_Sheet.md already exists, update only section 2.2; do NOT modify previous sections unless instructed.

1. Identify all schema files relevant to WF2-StagingEditor
2. Document their current state
3. Compare with standards
4. Prescribe necessary refactoring actions
5. Set status to "To Do" for all items

If any gap analysis item is unclear, insert <!-- NEED_CLARITY --> in that row and await my response instead of choosing "best guess".

After updating the cheat-sheet progress counter, also update the "Progress:" line in this Master Workflow doc.

Add <!-- STOP_FOR_REVIEW --> when done.

After reaching this point:

```
git add WF2-StagingEditor_Cheat_Sheet.md
git commit -m "WF2 2.2 draft (awaiting review)" --no-verify
```

```

**ACTION REQUIRED**: Review section 2.2 (WF2) content and provide feedback.

### Task 3.3: Complete Layer 3 (Routers) for WF2
```

Windsurf, assume Technical Lead role for WF2 section 2.3 (Layer 3: Routers).

Now please complete section 2.3 (Layer 3: Routers) of the WF2-StagingEditor_Cheat_Sheet.md.

If WF2-StagingEditor_Cheat_Sheet.md already exists, update only section 2.3; do NOT modify previous sections unless instructed.

1. Identify and analyze relevant router files for WF2-StagingEditor
2. Document current state
3. Compare with standards
4. Prescribe necessary refactoring actions
5. Set status to "To Do" for all items

If any gap analysis item is unclear, insert <!-- NEED_CLARITY --> in that row and await my response instead of choosing "best guess".

After updating the cheat-sheet progress counter, also update the "Progress:" line in this Master Workflow doc.

Add <!-- STOP_FOR_REVIEW --> when done.

After reaching this point:

```
git add WF2-StagingEditor_Cheat_Sheet.md
git commit -m "WF2 2.3 draft (awaiting review)" --no-verify
```

```

**ACTION REQUIRED**: Review section 2.3 (WF2) content and provide feedback.

### Task 3.4: Complete Layer 4 (Services) for WF2
```

Windsurf, assume Technical Lead role for WF2 section 2.4 (Layer 4: Services).

Now please complete section 2.4 (Layer 4: Services) of the WF2-StagingEditor_Cheat_Sheet.md.

If WF2-StagingEditor_Cheat_Sheet.md already exists, update only section 2.4; do NOT modify previous sections unless instructed.

1. Identify and analyze relevant service files for WF2-StagingEditor
2. Document current state
3. Compare with standards
4. Prescribe necessary refactoring actions
5. Set status to "To Do" for all items

If any gap analysis item is unclear, insert <!-- NEED_CLARITY --> in that row and await my response instead of choosing "best guess".

After updating the cheat-sheet progress counter, also update the "Progress:" line in this Master Workflow doc.

Add <!-- STOP_FOR_REVIEW --> when done.

After reaching this point:

```
git add WF2-StagingEditor_Cheat_Sheet.md
git commit -m "WF2 2.4 draft (awaiting review)" --no-verify
```

```

**ACTION REQUIRED**: Review section 2.4 (WF2) content and provide feedback.

### Task 3.5: Complete Layer 5 (Configuration) for WF2
```

Windsurf, assume Technical Lead role for WF2 section 2.5 (Layer 5: Configuration).

Now please complete section 2.5 (Layer 5: Configuration) of the WF2-StagingEditor_Cheat_Sheet.md.

If WF2-StagingEditor_Cheat_Sheet.md already exists, update only section 2.5; do NOT modify previous sections unless instructed.

1. Analyze environment variables and settings for WF2-StagingEditor
2. Document current state
3. Compare with standards
4. Prescribe necessary refactoring actions
5. Set status to "To Do" for all items

If any gap analysis item is unclear, insert <!-- NEED_CLARITY --> in that row and await my response instead of choosing "best guess".

After updating the cheat-sheet progress counter, also update the "Progress:" line in this Master Workflow doc.

Add <!-- STOP_FOR_REVIEW --> when done.

After reaching this point:

```
git add WF2-StagingEditor_Cheat_Sheet.md
git commit -m "WF2 2.5 draft (awaiting review)" --no-verify
```

```

**ACTION REQUIRED**: Review section 2.5 (WF2) content and provide feedback.

### Task 3.6: Complete Layer 6 (UI Components) for WF2
```

Windsurf, assume Technical Lead role for WF2 section 2.6 (Layer 6: UI Components).

Now please complete section 2.6 (Layer 6: UI Components) of the WF2-StagingEditor_Cheat_Sheet.md.

If WF2-StagingEditor_Cheat_Sheet.md already exists, update only section 2.6; do NOT modify previous sections unless instructed.

1. Identify and analyze relevant UI component files (JS, HTML templates) for WF2-StagingEditor
2. Document current state
3. Compare with standards
4. Prescribe necessary refactoring actions
5. Set status to "To Do" for all items

If any gap analysis item is unclear, insert <!-- NEED_CLARITY --> in that row and await my response instead of choosing "best guess".

After updating the cheat-sheet progress counter, also update the "Progress:" line in this Master Workflow doc.

Add <!-- STOP_FOR_REVIEW --> when done.

After reaching this point:

```
git add WF2-StagingEditor_Cheat_Sheet.md
git commit -m "WF2 2.6 draft (awaiting review)" --no-verify
```

```

**ACTION REQUIRED**: Review section 2.6 (WF2) content and provide feedback.

### Task 3.7: Complete Layer 7 (Testing) for WF2
```

Windsurf, assume Technical Lead role for WF2 section 2.7 (Layer 7: Testing).

Now please complete section 2.7 (Layer 7: Testing) of the WF2-StagingEditor_Cheat_Sheet.md.

If WF2-StagingEditor_Cheat_Sheet.md already exists, update only section 2.7; do NOT modify previous sections unless instructed.

1. Analyze existing tests for WF2-StagingEditor
2. Document current state
3. Compare with standards
4. Prescribe necessary refactoring actions
5. Set status to "To Do" for all items

If any gap analysis item is unclear, insert <!-- NEED_CLARITY --> in that row and await my response instead of choosing "best guess".

After updating the cheat-sheet progress counter, also update the "Progress:" line in this Master Workflow doc.

Add <!-- STOP_FOR_REVIEW --> when done.

After reaching this point:

```
git add WF2-StagingEditor_Cheat_Sheet.md
git commit -m "WF2 2.7 draft (awaiting review)" --no-verify
```

```

**ACTION REQUIRED**: Review section 2.7 (WF2) content and provide feedback.

### Task 3.8: Finalize WF2 Cheat Sheet
```

Windsurf, assume Technical Lead role for WF2 finalization.

Please review the entire WF2-StagingEditor_Cheat_Sheet.md for consistency and completeness.

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
   ```

   Also run:

   ```
   chmod +x scripts/ci/wf2-lint.sh
   ```

   to make it executable

3. Update the progress at the top of WF2-StagingEditor_Cheat_Sheet.md to "Progress: 7/7 sections completed, ready for implementation"

Add <!-- STOP_FOR_REVIEW --> when done.

After reaching this point:

```
git add WF2-StagingEditor_Cheat_Sheet.md scripts/ci/wf2-lint.sh
git commit -m "WF2 final cheat sheet and lint script (awaiting review)" --no-verify
```

```

**ACTION REQUIRED**: Review finalized WF2 cheat sheet and approve for implementation.

### Task 3.9: Begin WF2 Implementation of High-Priority Items
```

Windsurf, switch to Developer role (do not edit documentation) for WF2 implementation.

Let's begin implementing the changes documented in the WF2-StagingEditor_Cheat_Sheet.md. Start with the highest priority item:

1. Show me exactly what changes you plan to make
2. Run pre-commit hooks with:
   pre-commit run --files $(git diff --name-only HEAD)
3. Paste the console output
4. Await my approval before proceeding

After implementation:

1. Update the status in the WF2-StagingEditor_Cheat_Sheet.md to "Done"
2. Verify against the checklist

If WF2-StagingEditor_Cheat_Sheet.md already exists, update only the status fields; do NOT modify the content unless instructed.

```

**ACTION REQUIRED**: Review proposed WF2 changes and approve implementation.

### Task 3.10-3.X: Continue WF2 Implementation
Repeat Task 3.9 format for each refactoring item identified in the WF2 Implementation Priority Order section.

### Task 3.Y: Final WF2 Verification
```

Windsurf, switch to Developer role (do not edit documentation) for WF2 verification.

Please run the scripts/ci/wf2-lint.sh script and verify all tests pass.

Then update the WF2-StagingEditor_Cheat_Sheet.md to mark the workflow as completed.

On success, open a pull request from feature/wf2-standardization to main with the title "WF2 Standardization: StagingEditor Models-to-Tests" and paste the PR URL here.

```

**ACTION REQUIRED**: Verify successful completion of WF2-StagingEditor standardization.

Continue with the same pattern as Phase 1 & 2 for WF2 and subsequent workflows.

---

**NOTES:**
1. After each "ACTION REQUIRED" step, review Windsurf's output before proceeding
2. Provide feedback/corrections as needed before moving to the next task
3. Update the "Current Status" section at the top as you progress
4. When creating follow-up workflows, copy and adapt the Phase 1 & 2 tasks, updating workflow names appropriately
```
