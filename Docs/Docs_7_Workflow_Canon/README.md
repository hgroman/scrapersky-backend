# ScraperSky Workflow Canon

## Overview

The ScraperSky Workflow Canon is the authoritative documentation system for implementing, validating, and maintaining standardized workflows within the ScraperSky backend. This directory contains a comprehensive set of tools and templates that work together to ensure consistent implementation of the producer-consumer workflow pattern across all features.

## Key Components

### 1. Workflow Builder Cheat Sheet
[ScraperSky Workflow Builder Cheat Sheet.md](./ScraperSky%20Workflow%20Builder%20Cheat%20Sheet.md)

The entry point for implementing new workflows. This 5-phase process guide provides:
- Questionnaire to define workflow parameters
- Step-by-step implementation instructions
- Code templates for all required components
- Implementation checklist

### 2. Workflow Comparison Detailed
[workflow-comparison-detailed.md](./workflow-comparison-detailed.md)

The comparative reference table mapping all workflow components across existing implementations:
- Maps UI elements, API endpoints, services, and models
- Links each component to relevant architectural principles
- Provides WHY and HOW explanations for implementation decisions
- Serves as a blueprint for consistent implementation

### 3. Linear Steps Documentation
[Linear-Steps/](./Linear-Steps/)

Detailed, step-by-step breakdowns of each workflow:
- Files and code locations for each workflow step
- Source and destination tables for each data transformation
- Applicable architectural principles with explanations
- Links to guiding documentation

### 4. Workflow Definitions
[workflows/](./workflows/)

Formal YAML definitions of workflow structures for validation:
- WF-Sitemap-Import_CANONICAL.yaml
- v_6_SYSTEM_SCOPE_MAP.yaml
- Other workflow definition files

### 5. Dependency Traces
[Dependency_Traces/](./Dependency_Traces/)

Module dependency documentation for each workflow:
- Cross-module dependencies
- Service call graphs
- File and function relationships

## The Documentation Ecosystem Journey

### 1. Start with the Workflow Builder Cheat Sheet
- **Purpose**: Quick orientation and workflow definition
- **When to Use**: At the beginning of implementation to define core parameters
- The cheat sheet provides the mental model and 5-phase approach to rapidly create the skeleton of any new workflow

### 2. Cross-Reference with Workflow Comparison Table
- **Purpose**: Understand patterns across existing workflows
- **When to Use**: During implementation planning to ensure consistency
- The comparison table shows you exactly how similar components are implemented across other workflows, serving as proven examples

### 3. Study Relevant Linear-Steps Documents
- **Purpose**: Deep understanding of detailed steps for similar workflows
- **When to Use**: When implementing specific components
- These documents provide granular understanding of similar workflows and architectural principles for each step

### 4. Utilize YAML Workflow Definitions
- **Purpose**: Formal validation of workflow structure
- **When to Use**: During and after implementation to verify compliance
- These definitions allow automated validation that your implementation meets structural requirements

### 5. Dependency Traces
- **Purpose**: Understand cross-module dependencies
- **When to Use**: During architecture planning and when making changes
- These traces help you understand how components connect and prevent unintended side effects

## A Unified Implementation Approach

For maximum effectiveness, combine these tools into a unified workflow:

### Planning Phase
- Complete the Workflow Builder Cheat Sheet questionnaire
- Review the Workflow Comparison Table to identify similar existing patterns
- Run dependency traces on similar workflows to understand connections

### Implementation Phase
- Follow the 5-phase approach from the Cheat Sheet
- Consult Linear-Steps documents when implementing specific components
- Reference the architectural principles documents linked in the Comparison Table

### Validation Phase
- Use YAML workflow definitions to validate structural compliance
- Update the Workflow Comparison Table with your new workflow details
- Create a Linear-Steps document for your workflow to document it for others

### Documentation Phase
- Add your workflow to the Workflow-Comparison-Detailed.md table
- Create YAML validation schema for your workflow
- Document any unique patterns or considerations
## The Power of this Ecosystem

What makes this collection so powerful is that it provides:

1. **Multiple Entry Points**: Adapting to different developer experience levels and needs
2. **Different Levels of Detail**: From high-level cheat sheet to detailed linear steps
3. **Both Prescriptive and Reference Material**: Guidance on what to do and examples of how it's done
4. **Standardized Patterns**: Clear patterns that ensure architectural consistency
5. **Cross-Referencing Architecture**: Each step links to the relevant architectural principles

This ecosystem essentially creates a "workflow compiler" - if you follow the cheat sheet steps and reference the comparison table, you almost mechanically produce a compliant workflow implementation with minimal cognitive load.

## Taking It to the Next Level

To further enhance this system, we might consider:

1. **Interactive Workflow Generator**: A tool that asks the Cheat Sheet questions then auto-generates scaffolding code
2. **Workflow Compliance Checker**: Automated tool to verify implementation matches documentation
3. **Visual Workflow Mapper**: Diagram generator showing relationships between components

## Additional Resources

- [Producer-Consumer Workflow Pattern](./PRODUCER_CONSUMER_WORKFLOW_PATTERN.md)
- [Standard Curation Workflow Blueprint](./BP-01-Standard_Curation_Workflow.md)
- [Core Architectural Principles](../Docs_1_AI_GUIDES/17-CORE_ARCHITECTURAL_PRINCIPLES.md)
- [Curation Workflow Operating Manual](../Docs_6_Architecture_and_Status/0.4_Curation%20Workflow%20Operating%20Manual.md)
- [Background Services Architecture](../Docs_6_Architecture_and_Status/BACKGROUND_SERVICES_ARCHITECTURE.md)

---

The combination of standardized documentation, clear patterns, and comprehensive reference material makes this one of the most powerful workflow systems in the ScraperSky project, enabling consistent implementation and maintenance across all workflows.

---

## Note on Historical Anti-Patterns and Data Model Corrections (June 2025)

**Attention Future Auditors, Developers, and AI Assistants:**

This section serves as a permanent record of a significant data model correction implemented in June 2025. An anti-pattern was identified where workflow documentation and definitions for **WF1-SingleSearch** and **WF2-StagingEditor** incorrectly referenced the `places` table instead of the correct `places_staging` table.

This discrepancy was systematically resolved across all canonical workflow documents to ensure architectural consistency and prevent data processing errors. The detailed report below summarizes all changes made.

**If you encounter any file or artifact that appears to reference an incorrect table name for Workflows 1 or 2, you must immediately flag it for correction. This is critical for maintaining the integrity of the workflow canon.**

### **Project-Wide Audit and Correction Summary**

**Objective:** To find and replace all incorrect references to the `places` table and its corresponding `Place` model, ensuring all documentation consistently uses `places_staging` and `PlacesStaging` where appropriate.

---

### **1. Workflow Canonicals (`/workflows`)**

These files define the core workflows and their interactions.

*   **`WF1-SingleSearch_CANONICAL.yaml`**
    *   Updated the `depends_on_models` definition from `table: places` to `table: places_staging`.
    *   Corrected the `workflow_connections` section, changing `interface_table: places` to `interface_table: places_staging`.
    *   Modified the `production_operation` from `INSERT INTO places` to `INSERT INTO places_staging`.
    *   Updated descriptive comments to refer to the `places_staging table` for clarity.

*   **`v_5_REFERENCE_IMPLEMENTATION_WF2.yaml`**
    *   Performed a comprehensive update, changing all instances of `table: places`, `interface_table: places`, `source_table: places`, and `destination_table: places` to use `places_staging`.
    *   Updated the `consumption_query` to select `FROM places_staging`.
    *   Corrected the `alternative_operation` to `UPDATE places_staging`.
    *   Fixed descriptions in the `connection_details` to refer to the `places_staging table`.

### **2. Supporting Documentation (`/Template Resources`, `/Micro-Work-Orders`, `/Audit`)**

These documents provide detailed traces, work orders, and audit trails.

*   **`Template Resources/1 WF2-Staging Editor Dependency Trace.md`**
    *   Corrected the data model mapping to refer to the `places_staging` table.
    *   Updated the step-by-step data flow sequence to correctly reference `places_staging.status`, the `places_staging` table, and `places_staging` records.

*   **`Micro-Work-Orders/WF2-StagingEditor_micro_work_order.md`**
    *   In the "Producer-Consumer Pattern Analysis" section, corrected the handoff description to state that it occurs in the `places_staging table`.

*   **`Template Resources/3 WF2-StagingEditor_CANONICAL.yaml`**
    *   Updated notes in the "Background Task Execution" phase to refer to `PlacesStaging` objects instead of `Places`, ensuring model name consistency.

*   **`Audit/v_6_SYSTEM_SCOPE_MAP.yaml`**
    *   Corrected two key entries under `model_files` and `enum_files`, changing `table: places` to `table: places_staging` to align the audit document with the current schema.

---

**Conclusion:**

The audit is complete. All identified documentation within the `Docs/Docs_7_Workflow_Canon` directory has been updated. The term `places` has been systematically replaced with `places_staging` to reflect the correct table name, ensuring that all workflow definitions, dependency traces, and audit files are accurate and consistent.
