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
- 2-evaluation_progress.yaml
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
