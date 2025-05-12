# Work Order: Standardize AI Guide Filenames with Layer Prefixes

**Date Created:** {{YYYY-MM-DD}} (To be filled by AI)
**Version:** 1.0
**Status:** Open
**Assigned To:** AI Assistant (for filename analysis and `git mv` command generation)
**Requestor:** Quarterback

## 1. Objective

To improve the organization and discoverability of AI-generated development guides by standardizing their filenames to include a prefix indicating the primary architectural layer they pertain to. This aligns with the 7-layer architectural model used in the ScraperSky backend project.

## 2. Background

The `Docs/Docs_1_AI_GUIDES/` directory contains numerous valuable guides. To enhance their utility and integrate them more clearly with the project's architectural documentation (like the `CONVENTIONS_AND_PATTERNS_GUIDE.md`), we need to rename them systematically. This will aid developers in quickly identifying guides relevant to specific layers of the architecture.

The 7-Layer Architecture is defined as:

- Layer 1: Models & ENUMs
- Layer 2: Schemas
- Layer 3: Routers
- Layer 4: Services & Schedulers
- Layer 5: Configuration
- Layer 6: UI Components
- Layer 7: Testing

## 3. Scope of Work

This work order applies to all Markdown files currently located within the `Docs/Docs_1_AI_GUIDES/` directory.

## 4. Detailed Tasks

The assigned AI Assistant will perform the following tasks:

1.  **List Files:** Programmatically list all `.md` files within the `Docs/Docs_1_AI_GUIDES/` directory.
2.  **Content Analysis & Layer Determination:** For each file:
    - Read and analyze the content of the guide.
    - Determine which of the 7 architectural layers (as defined above) the guide's content primarily addresses or is most relevant to.
    - If a guide clearly spans multiple layers, choose the most dominant layer or the lowest layer it significantly impacts (e.g., a guide about testing ORM models would be Layer 1, as ORM is Layer 1 and Testing is Layer 7). If truly ambiguous after careful consideration, flag for human review.
3.  **New Filename Generation:**
    - For each file, construct a new filename by inserting a layer prefix.
    - The format for the new filename will be: `{OriginalNumericPrefix}-LAYER{X}_{OriginalNameRest}.md`
      - `{OriginalNumericPrefix}`: The existing number and hyphen at the beginning of the filename (e.g., `01-`).
      - `LAYER{X}`: The determined layer number (e.g., `LAYER1`, `LAYER5`).
      - `{OriginalNameRest}`: The rest of the original filename after the numeric prefix and hyphen.
    - **Example:**
      - Original: `01-ABSOLUTE_ORM_REQUIREMENT.md`
      - Determined Layer: Layer 1 (Models & ENUMs, as ORM is part of this)
      - New Filename: `01-LAYER1_ABSOLUTE_ORM_REQUIREMENT.md`
    - **Example 2:**
      - Original: `06-COMPREHENSIVE_TEST_PLAN.md`
      - Determined Layer: Layer 7 (Testing)
      - New Filename: `06-LAYER7_COMPREHENSIVE_TEST_PLAN.md`
4.  **Report Generation:**
    - Produce a report listing:
      - Each original filename.
      - The determined primary architectural layer (and a brief justification if not obvious).
      - The proposed new filename.
      - The corresponding `git mv` command for renaming.
    - If any files are flagged for human review due to ambiguity, list them separately with a note explaining the ambiguity.

## 5. Deliverables

1.  A Markdown formatted report containing:
    - A list of all original filenames from `Docs/Docs_1_AI_GUIDES/`.
    - For each file:
      - The determined primary architectural layer.
      - A brief (1-sentence) justification for the layer choice, especially if the title is ambiguous.
      - The proposed new filename.
      - The exact `git mv` command to execute the rename. (e.g., `git mv "Docs/Docs_1_AI_GUIDES/01-ABSOLUTE_ORM_REQUIREMENT.md" "Docs/Docs_1_AI_GUIDES/01-LAYER1_ABSOLUTE_ORM_REQUIREMENT.md"`)
    - A separate list of any files flagged for human review with reasons.

## 6. Acceptance Criteria

- All files in `Docs/Docs_1_AI_GUIDES/` have been assessed.
- Each assessed file has a clearly determined architectural layer and a corresponding new filename proposal.
- The new filenames strictly follow the `NN-LAYERX_OriginalName.md` format.
- A `git mv` command is provided for each proposed rename.
- The justification for layer choices is clear and concise.
- Any ambiguities are clearly documented for human review.

## 7. Assumptions

- The AI has read access to the specified directory and files.
- The AI has a current understanding of the 7-layer architecture as defined in this project.
- The AI can accurately interpret the primary focus of technical documentation.

---

By Your Command.
