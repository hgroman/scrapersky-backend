**Subject: Task - Standardize Architectural Layer Numbering Across Documentation**

**Objective:**
To systematically update a defined set of project documentation to incorporate a standardized 7-layer architectural numbering system. This will enhance clarity, consistency, and maintainability of the documentation.

**1. Golden Standard Reference:**

- The definitive guide for layer definitions and numbering is: `Docs/Docs_10_Final_Audit/layer-numbering-guidance.md`.
- **You MUST strictly adhere to the layer definitions and numbering provided in this document.**
  - Layer 1: Models & ENUMs
  - Layer 2: Schemas
  - Layer 3: Routers
  - Layer 4: Services
  - Layer 5: Configuration
  - Layer 6: UI Components
  - Layer 7: Testing

**2. Scope of Work (Files and Directories):**
You are to process all relevant files within the following locations:

- **Key File (Primary Example for YAML):** `Docs/Docs_7_Workflow_Canon/workflow-comparison-structured.yaml`
- **Directory 1: Audit Files:** `Docs/Docs_7_Workflow_Canon/Audit/`
  - Includes: `ORPHAN_FILE_AUDIT_WORK_ORDER.md`, `WORKFLOW_AUDIT_JOURNAL.md`, `audit_cheat_sheet.md`, `1.1-API-Router-Layer.md`, `1.2-Background Processing Layer.md`, `2-evaluation_progress.yaml`, `1.0-System-Infrastructure-Layer.md`, `0-A-ALL-PYTHON-FILES-IN-SRC.md`, `0-B-PYTHON-FILE-LIST.md`, `0-C-AUDIT-FOR-ORPHANS.md`, `3-python_file_status_map.md`, `WORK_ORDER.md`, `validation_schema.json`
- **Directory 2: Dependency Traces:** `Docs/Docs_7_Workflow_Canon/Dependency_Traces/`
  - Includes all `.md` files.
- **Directory 3: Linear Steps:** `Docs/Docs_7_Workflow_Canon/Linear-Steps/`
  - Includes all `_linear_steps.md` files.
- **Directory 4: Micro-Work-Orders:** `Docs/Docs_7_Workflow_Canon/Micro-Work-Orders/`
  - Includes all `_micro_work_order.md` files AND `MICRO_WORK_ORDER_TEMPLATE.md`.
- **Directory 5: Canonical Workflows:** `Docs/Docs_7_Workflow_Canon/workflows/`
  - Includes all `_CANONICAL.yaml` files AND `README.md`.
- **Directory 6 (Templates & Guides - as per `layer-numbering-guidance.md`):**
  - `Docs/Docs_8_Document-X/Audit_And_Refactor_Workflow_Cheat_Sheet_TEMPLATE.md`
  - `Docs/Docs_6_Architecture_and_Status/CONVENTIONS_AND_PATTERNS_GUIDE.md`
  - `Docs/Docs_6_Architecture_and_Status/Q&A_Key_Insights.md`
  - (Also consider any files in `Docs/Docs_5_Project_Working_Docs/` if they explicitly reference these architectural layers by name only).

**3. General Execution Rules:**

- **Accuracy:** Ensure all transformations strictly match the "Golden Standard."
- **Preservation:** Maintain existing Markdown formatting, YAML structure, and all other file content not directly related to layer naming.
- **No Unrelated Changes:** Do not introduce any changes, fixes, or refactoring outside the scope of layer numbering.
- **Idempotency (if possible):** If the script is run again, it should not make further changes to already correctly formatted layer names.
- **Handle Case Sensitivity:** Be mindful of potential variations in capitalization (e.g., "schemas", "Schemas", "SCHEMAS") when searching, but always replace with the exact "Golden Standard" casing (e.g., "Layer 2: Schemas").

**4. Specific Update Instructions:**

    **A. For Markdown Files (`.md`):**
    *   **Headers:**
        *   Search for headers (e.g., `## Component Name`, `### Component Name`) that match the component names from the Golden Standard.
        *   Transform them: e.g., `## Models & ENUMs` becomes `## Layer 1: Models & ENUMs`.
        *   Adjust for existing numbering if present: e.g. `## 2.1 Models & ENUMs` becomes `## 2.1 Layer 1: Models & ENUMs`.
    *   **Inline Text & Lists:**
        *   Search for mentions of component names within sentences or list items.
        *   Transform them: e.g., "...the services will process..." becomes "...Layer 4: Services will process...".
        *   Be careful not to break sentence structure. If a simple prefix makes the sentence awkward, flag for human review.

    **B. For YAML Files (`.yaml`):**
    *   `Docs/Docs_7_Workflow_Canon/workflow-comparison-structured.yaml`:
        *   Focus on the `step:` field. Prepend the layer number and name.
            *   Example: `step: '**2. API Request Schema**'` becomes `step: '**Layer 2: API Request Schema**'`.
            *   Example: `step: '**3. API Router**'` becomes `step: '**Layer 3: API Router**'`.
        *   For `step:` fields describing multiple components (e.g., `'**4. Core Logic Location**'` which lists `Service (via background task)` and `Router directly`), if a single layer prefix is awkward, update the descriptive text to incorporate layer terminology thoughtfully or, if too complex, flag for human review.
    *   `*_CANONICAL.yaml` files (in `Docs/Docs_7_Workflow_Canon/workflows/`):
        *   Scan string values within the YAML structure (especially descriptions, notes, or step-like fields) for component names and update them as per the Markdown inline text rules.

    **C. Special Handling for `Docs/Docs_7_Workflow_Canon/Audit/` directory:**
    *   `1.0-System-Infrastructure-Layer.md`, `1.1-API-Router-Layer.md`, `1.2-Background Processing Layer.md`:
        *   **Analyze:** Determine how their existing "Layer" concept maps to the new 7-layer Golden Standard.
        *   **Update Content:** Modify their internal content to align with the new definitions. This might involve rephrasing or restructuring.
        *   **Propose Renaming:** Suggest new filenames based on the Golden Standard (e.g., `1.1-API-Router-Layer.md` could become `Layer-3_Routers_Audit-Notes.md` or similar – maintain clarity about its origin/purpose).
        *   For `1.0-System-Infrastructure-Layer.md`: Specifically analyze if its content refers to the application architecture layers (1-7) or IaaS/PaaS/Network layers. If the latter, or a confusing mix, make no changes and flag for human review with a summary. If it clearly maps to one or more of the 7 layers, proceed with updates.
    *   Other files in this directory: Apply standard Markdown/YAML update rules.

**5. Priority of Updates (Templates First):**

- If feasible, prioritize updating template files first, such as:
  - `Docs/Docs_8_Document-X/Audit_And_Refactor_Workflow_Cheat_Sheet_TEMPLATE.md`
  - `Docs/Docs_7_Workflow_Canon/Micro-Work-Orders/MICRO_WORK_ORDER_TEMPLATE.md`

**6. Handling Ambiguity and Edge Cases:**

- If a direct mapping is unclear, if a change would significantly alter the meaning, or if applying a layer name makes text awkward or unreadable, **DO NOT GUESS**.
- Instead, flag the specific file, line number, and the problematic text for human review. Provide a brief note on why it was flagged.

**7. Reporting and Output:**
Upon completion, provide the following:

- A list of all files that were modified.
- For each modified file, provide a diff of the changes made.
- A separate list of all files/sections flagged for human review, including the file path, line number(s), original text, and a brief reason for flagging.

**8. Final Verification:**

- Be aware that all changes will be reviewed by a human team member (us) before final acceptance.

---

How does this look as a set of instructions, Quarterback? We want to be as clear and unambiguous as possible for our AI helper.
