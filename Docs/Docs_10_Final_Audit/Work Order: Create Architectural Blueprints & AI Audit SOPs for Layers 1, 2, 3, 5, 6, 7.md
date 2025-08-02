# Work Order: Create Architectural Blueprints & AI Audit SOPs for Layers 1, 2, 3, 5, 6, 7

**Document Version:** 1.0
**Date:** 2025-05-13
**Requester:** User (via Gemini intermediary)
**Objective:** To develop a comprehensive set of architectural `Blueprint` documents and accompanying `AI Audit SOP` (Standard Operating Procedure) documents for ScraperSky Layers 1, 2, 3, 5, 6, and 7. These documents will enable consistent, accurate, and detailed architectural assessments and the identification of technical debt by AI assistants.

---

## 1. Background & Core Philosophy

We have recently completed a rigorous process of defining and refining the `Layer-4-Services_Blueprint.md` (Version 2.1) and its corresponding `Layer-4-Services_AI_Audit_SOP.md` (Version 2.1). These documents have proven highly effective in guiding an AI assistant (Windsurf/Sonet) to perform nuanced architectural assessments that:

- Acknowledge the current state of the codebase ("Code is King").
- Measure the current state against **ideal architectural standards** derived from authoritative source documents.
- Clearly identify all deviations from the ideal as **technical debt**.
- Distinguish between different _types_ of deviations (e.g., use of an acceptable "Exception Pattern" vs. violating the rules of that exception).
- Prescribe clear refactoring actions.

The **core philosophy** is that the Blueprints define the "ideal," and the SOPs guide an AI to use that Blueprint to assess the "real," with all differences being cataloged as technical debt to inform future refactoring.

This work order aims to replicate this successful methodology for all other architectural layers of the ScraperSky backend.

---

## 2. Authoritative Source Documents

The creation of each layer-specific Blueprint and SOP **MUST** be grounded in the following primary authoritative source documents:

1.  **`Docs/Docs_6_Architecture_and_Status/1.0-ARCH-TRUTH-Definitive_Reference.md`**: Provides the high-level definition, responsibilities, key patterns, and current status/technical debt for each of the 7 layers. This is the **foundational document** for understanding each layer's role and ideal state.
2.  **`Docs/Docs_6_Architecture_and_Status/archive-dont-vector/CONVENTIONS_AND_PATTERNS_GUIDE.md`**: Contains detailed, prescriptive naming conventions and structural patterns for components across various layers (especially Layers 1, 2, 3, 4, and 5). This is critical for defining specific, auditable criteria.
3.  **`Docs/Docs_6_Architecture_and_Status/Q&A_Key_Insights.md`**: Offers clarifications, elaborations, and specific answers to questions about implementation standards and conventions for various layers. Often provides the "why" behind certain rules.
4.  **`Docs/Docs_6_Architecture_and_Status/3.0-ARCH-TRUTH-Layer_Classification_Analysis.md`**: Useful for understanding how existing project efforts and components have been historically classified into layers, providing context on the typical scope and nature of work within each layer.
5.  **`Docs/Docs_6_Architecture_and_Status/4.0-ARCH-TRUTH-State_of_the_Nation_May_2025.md`**: Provides a snapshot of current compliance, known issues, and strategic direction, which can inform the "current reality" aspect of the assessment.
6.  **Existing Codebase (`src/` directory primarily):** The current code represents the "Code is King" reality. Patterns observed in the code, especially those that are consistently applied across multiple workflows and align with principles in the truth documents, should be considered.

**Reference Gold Standard Examples:**

- **`Docs/Docs_10_Final_Audit/Layer-4-Services_Blueprint.md` (Version 2.1)**
- **`Docs/Docs_10_Final_Audit/Layer-4-Services_AI_Audit_SOP.md` (Version 2.1)**

These Layer 4 documents should be used as a template and quality benchmark for the structure, level of detail, and clarity required for the documents for other layers.

---

## 3. Task: For EACH Target Layer (1, 2, 3, 5, 6, 7)

You will create **two** markdown documents:

1.  A `Layer-X-{LayerName}_Blueprint.md`
2.  A `Layer-X-{LayerName}_AI_Audit_SOP.md`

(Replace `X` with the layer number and `{LayerName}` with a concise name for the layer, e.g., `Layer-1-Models_Enums_Blueprint.md`).

### 3.1. `Layer-X-{LayerName}_Blueprint.md` - Requirements

This document defines the "ideal" architectural standard for the specific layer. It should be structured similarly to the `Layer-4-Services_Blueprint.md (v2.1)` and include:

- **Version and Date.**
- **Derived From:** Clearly list the authoritative source documents used (primarily from Section 2 of this work order).
- **Contextual References:** (Optional) Other relevant documents.
- **(Optional) Preamble:** If useful, a brief section linking this layer's standards to the Core Architectural Principles from `1.0-ARCH-TRUTH-Definitive_Reference.md`.
- **Core Principle(s) for the Layer:** What are the overarching goals and philosophies governing this layer? (Derived from `1.0-ARCH-TRUTH-Definitive_Reference.md`).
- **Standard Pattern(s):**
  - Define the **preferred/ideal** way components in this layer should be structured, named, and behave.
  - Detail its **Definition & Scope** and **Responsibilities**.
  - Provide **Key Compliance Criteria:** These must be specific, measurable, and auditable points directly derived from the `CONVENTIONS_AND_PATTERNS_GUIDE.md`, `Q&A_Key_Insights.md`, and `1.0-ARCH-TRUTH-Definitive_Reference.md`.
- **(If Applicable) Documented Exception Pattern(s):**
  - If the authoritative documents describe accepted alternative patterns or justifiable deviations for specific use cases within this layer (similar to the "Router-Handled CRUD" pattern for Layer 4), document these clearly.
  - Define the **Definition & Scope** and **Responsibilities** for this exception.
  - Provide **Key Compliance Criteria** for this exception, including clearly defined **boundaries** for its acceptable use. Logic or structure exceeding these boundaries becomes technical debt.
- **Audit & Assessment Guidance (Crucial Section - Model after Layer 4 Blueprint Section 4):**
  - **Core Philosophy:** Reiterate the goal of identifying all deviations from the ideal to catalog technical debt, while acknowledging current code.
  - Step 1: **Identify Implemented Pattern:** How to classify the _current state_ of a component.
  - Step 2: **Assess Against Ideal & Specific Criteria:** Detailed logic on how to compare the current state to:
    - The "Ideal/Standard Pattern."
    - The criteria of an "Exception Pattern" if one is identified as being used.
    - How to determine if an Exception Pattern's use is within its defined, bounded scope.
  - Step 3: **Document Technical Debt:** Instructions on what constitutes technical debt for this layer. This MUST include:
    - Use of an "Exception Pattern" where the "Standard Pattern" is the ideal.
    - Use of an "Exception Pattern" where its own rules or bounded scope are violated.
    - Any violation of specific compliance criteria for any pattern.
  - Step 4: **Prescribe Refactoring Actions:** Guidance on suggesting actions to move towards the ideal, prioritizing critical fixes.

### 3.2. `Layer-X-{LayerName}_AI_Audit_SOP.md` - Requirements

This document guides an AI assistant in performing the audit using the corresponding `Blueprint`. It should be structured similarly to `Layer-4-Services_AI_Audit_SOP.md (v2.1)` and include:

- **Version and Date.**
- **Purpose.**
- **(Optional) Introduction: Context from Architectural Truth:** Linking to overarching ARCH-TRUTH docs.
- **Prerequisites & Inputs:**
  - The Layer-X Blueprint (this SOP is for).
  - Relevant sections of the Core Architectural & Convention Guides (from Section 2 of this work order).
  - The target workflow-specific cheat sheet file.
  - Instructions on identifying relevant source code files for _this specific layer_.
  - Other contextual documents (e.g., `workflow-comparison-structured.yaml`).
- **Audit Procedure:**
  - **Step X.1: Identify Service/Logic Implementation Pattern (or equivalent for the layer):** How the AI should determine the current pattern of the component being audited, referencing the Blueprint's Audit & Assessment Guidance.
  - **Step X.2: Analyze Relevant Code Files Against the Blueprint:** Detailed instructions on how to apply the Blueprint's criteria for the identified pattern, including checking scope boundaries for exception patterns.
  - **Step X.3: Populate the Cheat Sheet (Layer X Section):**
    - **File Path.**
    - **Current State Summary:** Including the identified implemented pattern.
    - **Gap Analysis (Technical Debt Identification):** Explicitly instruct the AI to follow the logic from the Blueprint's "Audit & Assessment Guidance" (Section 4 or equivalent) for identifying and phrasing gaps. This must include correctly flagging use of exception patterns vs. ideal, and violations of exception pattern scopes.
    - **Prescribed Refactoring Actions:** Guide the AI to align suggestions with the Blueprint's guidance, including nuanced actions for "acceptable but not ideal" vs. "critical deviation."
    - **Verification Checklist.**
  - **Step X.4: Review and Finalize.**
- **Output:** Expected outcome (updated cheat sheet section).

---

## 4. Key Considerations & Lessons Learned (Incorporate these into your process)

- **Clarity is Paramount:** Ensure all definitions, criteria, and instructions are unambiguous.
- **Actionable Criteria:** Compliance criteria in the Blueprint must be verifiable.
- **Nuance in Technical Debt:** The system must allow for identifying something as "technical debt because it's not the ideal pattern" while also assessing if that "non-ideal but currently used" pattern is at least implemented _correctly according to its own rules_.
- **Bounded Exceptions:** If a layer has acceptable "exception" patterns, their scope and limitations must be clearly defined in the Blueprint. Anything exceeding those bounds is critical technical debt.
- **Direct Referencing:** Both documents should heavily reference specific sections of the authoritative source documents to justify standards and instructions.
- **Iterative Refinement Mindset:** While striving for thoroughness, understand that these documents may undergo further refinement as they are used. Focus on creating a strong V1.0.

---

## 5. Deliverables

For **each** of Layers 1, 2, 3, 5, 6, and 7:

1.  One `Layer-X-{LayerName}_Blueprint.md` file.
2.  One `Layer-X-{LayerName}_AI_Audit_SOP.md` file.

Place these in `Docs/Docs_10_Final_Audit/`.

---

This is a significant undertaking. Please proceed methodically, one layer at a time, using the Layer 4 documents as your guide and the authoritative sources as your foundation. Ask clarifying questions if any part of this work order is unclear.
