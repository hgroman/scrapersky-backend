# Work Order: Standardize Project Working Document Subdirectory Names with Layer Prefixes

**Work Order ID:** WO4.0-Layer-Prefix-Project-Working-Docs
**Date Created:** {{YYYY-MM-DD}} (To be filled by AI generating this WO)
**Version:** 1.1
**Status:** Open
**Assigned To:** AI Document Analysis Specialist
**Requestor:** Quarterback

## 1. Objective

To significantly improve the organization, discoverability, and contextual understanding of historical project working documents located within the `Docs/Docs_5_Project_Working_Docs/` directory. This will be achieved by systematically renaming its subdirectories to include a prefix indicating the primary architectural layer their collective content pertains to, based on a thorough content analysis. This aligns with the 7-layer architectural model used in the ScraperSky backend project.

## 2. Background

The `Docs/Docs_5_Project_Working_Docs/` directory houses a chronological collection of working documents, capturing the evolution of various project tasks, features, and refactoring efforts. While the numbered prefixes suggest a timeline, the directory names themselves often describe tasks or features rather than their primary architectural impact. This makes it challenging to quickly locate all documents related to a specific architectural layer.

Standardizing these subdirectory names with layer prefixes, similar to the convention used in `Docs/Docs_1_AI_GUIDES/`, will create a more coherent and easily navigable knowledge base.

The 7-Layer Architecture is defined as:

- Layer 1: Models & ENUMs
- Layer 2: Schemas
- Layer 3: Routers
- Layer 4: Services & Schedulers
- Layer 5: Configuration
- Layer 6: UI Components
- Layer 7: Testing

## 3. Scope of Work

This work order applies to all immediate subdirectories currently located within the `Docs/Docs_5_Project_Working_Docs/` directory.

## 4. Detailed Tasks for AI Analyst

This section outlines the precise steps you, the AI Document Analysis Specialist, will perform.

### 4.1 Context (C.R.A.F.T. Element)

You are embarking on a crucial initiative to dramatically enhance the ScraperSky project's knowledge management infrastructure. The `Docs/Docs_5_Project_Working_Docs/` directory contains a rich chronological history of development efforts, but its current subdirectory naming conventions lack consistent architectural context, hindering efficient information retrieval. Your primary objective is to meticulously analyze the _collective content within each subdirectory_ to accurately assign it a primary architectural layer. Based on this determination, you will propose a new, prefixed name for each subdirectory, thereby transforming this valuable archive into a systematically organized and easily searchable resource. This task requires a keen eye for detail and a deep understanding of software development documentation.

### 4.2 Role (C.R.A.F.T. Element)

You are a distinguished AI Document Analysis Specialist, possessing more than two decades of unparalleled experience in advanced semantic understanding, sophisticated content categorization, and the architecting of large-scale information systems. Your core competency lies in the precise discernment of the central subject matter within complex technical documentation and its accurate mapping to predefined architectural frameworks. The quality of your analysis and subsequent recommendations is expected to be industry-leading, far exceeding typical automated outputs.

### 4.3 Action (C.R.A.F.T. Element)

Please execute the following steps sequentially and with meticulous attention to detail:

1.  **Preparation:** Take a deep breath and mentally prepare for a thorough and nuanced analysis of diverse technical documents.
2.  **List Subdirectories:** Programmatically identify and list all immediate subdirectories within the `Docs/Docs_5_Project_Working_Docs/` directory.
3.  **Iterative Content Analysis & Layer Determination:** For each identified subdirectory:
    a. **File Identification:** Systematically identify and ensure you can access all files contained within the current subdirectory (e.g., `.md`, `.txt`, `.yaml`, plain text files, etc., disregarding binary or image files unless their names are clearly indicative).
    b. **Comprehensive Semantic Analysis:** Perform a deep semantic analysis of the _combined content_ of all relevant files within the subdirectory. Your focus should be on identifying the dominant technical themes, programming languages, specific technologies mentioned, software modules or functions referenced, architectural patterns discussed, or problems solved.
    c. **Layer Assignment:** Based on your holistic analysis of the subdirectory's content, determine which of the 7 ScraperSky architectural layers (as defined in Section 2. Background) the subdirectory's content _primarily and most significantly_ addresses.
    d. **Handling Ambiguity:**
    i. If a subdirectory's content clearly spans multiple layers, you **MUST** choose the single most dominant layer.
    ii. If dominance is unclear, select the lowest numerical layer that the content significantly impacts (e.g., if Layer 4 content heavily relies on and discusses Layer 1 specifics, and the Layer 1 aspect is substantial, Layer 1 might be appropriate if not clearly dominated by Layer 4 themes).
    iii. If, after careful consideration, the layer assignment remains genuinely ambiguous or if the content is too sparse or generic for a confident assignment, you **MUST** flag the subdirectory for human review, providing a clear explanation of the ambiguity.
    e. **Missing Information Query:** If you determine that critical information required for an accurate layer assignment is evidently missing from the documents within a subdirectory, or if instructions in this work order are unclear for a specific edge case you encounter, please formulate a precise question to request clarification. You may list these as part of your "human review" section if they block a determination.
4.  **New Directory Name Generation:**
    a. For each subdirectory that you successfully assign a layer to, construct a new proposed directory name.
    b. **Format:** The new directory name **MUST** follow the pattern: `{OriginalNumericPrefix}-LAYER{X}_{OriginalNameRest}`. - `{OriginalNumericPrefix}`: The existing number and hyphen at the beginning of the directory name (e.g., `02-`). - `LAYER{X}`: The determined layer number (e.g., `LAYER1`, `LAYER5`). - `{OriginalNameRest}`: The rest of the original directory name _after_ the numeric prefix and hyphen.
    c. **Example:** - Original: `02-database-consolidation/` - Determined Layer: Layer 1 - Proposed New Name: `02-LAYER1_database-consolidation/`
    d. **Example 2:** - Original: `30-Javascript-Refactor/` - Determined Layer: Layer 6 - Proposed New Name: `30-LAYER6_Javascript-Refactor/`
    e. **Handling names without a hyphen after the numeric prefix:** If an original name is, for example, `01initial-assessment` (no hyphen after `01`), the `LAYER{X}` should still be inserted logically after the numeric part and before the textual part, with an underscore: `01-LAYERX_initial-assessment`. If the original name part after the numeric prefix already started with an underscore or was a single word, adjust accordingly to maintain readability, e.g. `01_SomeName` -> `01-LAYERX_SomeName`. Prioritize the `{OriginalNumericPrefix}-LAYER{X}_{OriginalNameRest}` pattern where possible.
5.  **Report Generation:** Compile a comprehensive report detailing your findings and proposals, adhering to the specifications in the "Format" section below.

### 4.4 Format (C.R.A.F.T. Element - for the AI Analyst's output report)

Your final deliverable **MUST** be a single Markdown formatted report. This report must be structured as follows:

1.  **Summary Table:** The primary section of your report will be a table with the following columns:
    - `Original Subdirectory Name`: The full original name of the subdirectory.
    - `Determined Primary Layer`: The layer number and name you assigned (e.g., "Layer 1: Models & ENUMs").
    - `Brief Justification (1-3 sentences)`: A concise explanation for your layer choice. This is crucial if the choice isn't immediately obvious from the directory name or if the content was sparse or multifaceted. Clearly state the key indicators from the content that led to your decision.
    - `Proposed New Subdirectory Name`: The new name you generated using the specified format.
    - `git mv Command`: The exact `git mv` command required to rename the directory. Ensure correct quoting for names with spaces or special characters.
      Example `git mv` command:
      `git mv "Docs/Docs_5_Project_Working_Docs/01-initial-assessment" "Docs/Docs_5_Project_Working_Docs/01-LAYER5_initial-assessment"`
2.  **Subdirectories Flagged for Human Review:** A separate section listing any subdirectories you flagged for human review. For each flagged item, include:
    - The `Original Subdirectory Name`.
    - A clear and detailed `Reason for Flagging` (e.g., explaining the ambiguity, conflicting indicators, sparse content, or specific questions you have).

### 4.5 Target Audience (C.R.A.F.T. Element - for the AI Analyst's output report)

Your meticulously crafted report will be presented to the Project Quarterback and senior development team. These stakeholders require clear, accurate, and immediately actionable information to approve and implement the proposed changes. Your justifications must be cogent and instill confidence in your analytical rigor.

## 5. Deliverables

1.  A single Markdown formatted report as specified in Section 4.4, containing the analysis and renaming proposals for all subdirectories within `Docs/Docs_5_Project_Working_Docs/`.

## 6. Acceptance Criteria

- All immediate subdirectories within `Docs/Docs_5_Project_Working_Docs/` have been analyzed and included in the report.
- Each assessed subdirectory has either a clearly determined architectural layer and a corresponding new name proposal, or is explicitly flagged for human review with a clear justification.
- Proposed new subdirectory names strictly adhere to the `{OriginalNumericPrefix}-LAYER{X}_{OriginalNameRest}` format (or a close, logical derivative if the original numeric prefix isn't followed by a hyphen).
- A syntactically correct `git mv` command is provided for each proposed rename.
- The justification for layer choices is clear, concise, and directly supported by your (briefly summarized) content analysis.
- Any ambiguities or issues preventing a layer determination are clearly documented in the "human review" section.

## 7. Assumptions

- The AI Analyst has read access to the `Docs/Docs_5_Project_Working_Docs/` directory and all files contained within its immediate subdirectories.
- The AI Analyst has a current and accurate understanding of the 7-layer architecture as defined in this project (see Section 2. Background).
- The AI Analyst can accurately interpret the primary focus of technical documentation, notes, and other project-related artifacts found within the subdirectories.
- The AI Analyst will infer the character encoding of text files or default to UTF-8.

---

By Your Command.
