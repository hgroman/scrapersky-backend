# 09: The Pattern Crafting Methodology

## Component Overview

This component defines the cognitive and practical process an AI agent should follow to identify, analyze, distill, and formulate patterns (both problem patterns and good pattern exemplars) from source documentation. This methodology is crucial for transforming raw information into the structured intelligence stored in the Vector DB.

## Purpose

To provide a repeatable and effective method for agents to extract valuable knowledge from project documentation and structure it into the defined pattern format, thereby building their specialized knowledge base.

## Key Considerations

*   **Analytical Process:** The steps involved in reading, understanding, and analyzing complex technical documentation.
*   **Pattern Identification:** How to recognize recurring issues (technical debt, anti-patterns) and examples of good practices within the text.
*   **Intelligence Distillation:** The process of extracting the core concepts, reasoning, and actionable guidance from the descriptive text.
*   **Structuring Knowledge:** Mapping the distilled intelligence to the specific fields required for the Vector DB `fix_patterns` table.
*   **Linking to Source:** Identifying and correctly linking to the relevant DART documents containing code examples or more detailed context.
*   **Consistency:** Ensuring patterns are documented consistently following the defined format and standards.

## Methodology Steps

1.  **Select Source Document(s):** Identify the relevant Specific Knowledge documents for your assigned specialization scope (referencing the "Index of Knowledge Documents").
2.  **Initial Read-Through:** Read the document(s) to gain a general understanding of the content, key topics, and overall structure.
3.  **Active Analysis - Identify Potential Patterns:** Reread the document(s) with an analytical mindset, actively looking for:
    *   Descriptions of problems, issues, or technical debt.
    *   Discussions of standards, conventions, or best practices.
    *   Examples of code or design that illustrate a point (good or bad).
    *   Sections explaining the "why" behind a particular approach or rule.
    *   Recurring themes or issues mentioned in audit reports.
4.  **Distill Core Intelligence:** For each potential pattern identified, distill the core intelligence:
    *   What is the essence of the problem or good practice? (Problem Description / Description)
    *   What are the underlying causes or principles? (Learnings / Principles Demonstrated)
    *   How can this be identified in code or design? (Implicit in Problem Description/Learnings)
    *   What are the conceptual steps to address or implement it? (Solution Steps)
    *   Where are the concrete examples? (Identify references to code or specific DART documents).
5.  **Formulate Pattern Document (Internal/Temporary):** Structure the distilled intelligence into the defined pattern format, populating the fields required for the Vector DB entry. At this stage, this might be an internal representation or a temporary markdown file following the standard pattern document structure.
6.  **Identify/Create DART Documents for Code Examples:** If the source document refers to code examples or if examples are needed to illustrate the pattern, identify existing DART documents or create new ones containing the relevant `code_before`, `code_after`, or `code_example` snippets. Obtain the DART URLs for these documents.
7.  **Refine Pattern Fields and Add DART Links:** Review the formulated pattern data. Ensure the Problem Description, Solution Steps, Learnings, and Prevention Guidance are clear, concise, and conceptual (no literal code). Add the DART document URL(s) to the appropriate field(s). Assign relevant Tags, Severity, Problem Type, Code Type, Layers, Workflows, and File Types based on the analysis.
8.  **Prepare for Extraction:** Ensure the pattern data is in a format that the Data Extraction Mechanism can process (e.g., a correctly formatted markdown file or a structured data representation).
9.  **Submit for Onboarding:** Provide the prepared pattern data to the Data Extraction Mechanism for processing and subsequent insertion into the Vector DB.

## Required Outputs

*   A detailed description of the steps involved in identifying and crafting patterns.
*   Emphasis on distilling conceptual intelligence vs. copying literal code.
*   Guidance on linking to DART documents for code examples.

## Dependencies

*   The source knowledge documents.
*   The defined format for markdown pattern documents.
*   Access to DART for creating/linking code examples.
*   The Data Extraction Mechanism (which consumes the output of this methodology).

## Responsible Role

*   **Onboarding Agent:** Executes this methodology to create patterns.
*   **Architect Persona (Roo):** Defines and documents this methodology.
*   **Librarian Persona (Future):** Could assist in identifying relevant sections or potential patterns in source documents.

## Notes

This methodology is the core "skill" an agent needs to build its specialized knowledge base. It requires analytical reasoning and the ability to synthesize information from various sources. The quality of the patterns in the Vector DB directly depends on the effective application of this methodology.