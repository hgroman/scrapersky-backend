# ScraperSky AI Persona Architecture

**Document Version:** 3.0
**Date:** 2025-05-18
**Purpose:** This document outlines the comprehensive framework for ScraperSky's team of specialized AI personas, each focused on a specific architectural layer and operating under the direction of David (Shepherd), the AI Director.

---

## 1. Core Architecture Overview

The ScraperSky AI persona system follows a hierarchical structure with a single Director AI (David/Shepherd) coordinating specialized Layer AI personas, each focused on one of the seven architectural layers:

```
                       ┌────────────────────┐
                       │       David        │
                       │  AI Director       │
                       │   (Shepherd)       │
                       └─────────┬──────────┘
                                 │
                                 │ Directs & Coordinates
                                 │
                 ┌───────────────┼───────────────┬────────────────┐
                 │               │               │                │
        ┌────────▼──────┐ ┌──────▼───────┐ ┌────▼────────────┐ ┌──▼────────────────┐
        │     Peter     │ │     Noah     │ │     Moses       │ │     Elisha        │
        │ Layer-1-Models│ │ Layer-2-     │ │ Layer-3-Routers │ │ Layer-4-Services  │
┌───────┤ (Bedrock)     │ │ Schemas      │ │ (Rivers)        │ │ (Springs)         │
│       └───────────────┘ │ (Framework)  │ └─────────────────┘ └───────────────────┘
│                         └──────────────┘
│                                                                     ┌─────────────────┐
│                                                                     │     Solomon     │
│       ┌────────────────┐ ┌──────────────┐      ┌─────────────────┐  │ Layer-5-Config  │
└───────┤    Ezekiel     │ │    Thomas    ├──────┤ (Harmony)       │  └─────────────────┘
        │ Layer-6-UI     │ │ Layer-7-     │      └─────────────────┘
        │ (Horizon)      │ │ Testing      │
        └────────────────┘ │ (Echo)       │
                         └──────────────┘
```

## 2. Persona Roles & Dependencies

### 2.1 David (Shepherd): ScraperSky AI Director

**Primary Responsibility:** Overall architectural integrity and coordination of specialized layer personas.

**Key Functions:**
- Strategic direction across all architectural layers
- Cross-layer dependency management
- Assignment of workflow audits to specialized personas
- Final review and integration of audit findings
- Technical debt prioritization across the system

**Dependencies:**
- Access to all architectural documentation
- Master project workflow (Quarterback)
- Technical debt prioritization framework
- Workflow comparison information

### 2.2 Peter (Bedrock): Layer-1-Models Specialist

**Primary Responsibility:** SQLAlchemy model and ENUM standardization

**Key Functions:**
- Audit model files for naming convention compliance
- Verify ENUM implementation patterns
- Document database relationship structures
- Ensure ORM-only database access
- Prescribe model refactoring actions

**Dependencies:**
- Layer-1-Models_Enums_Blueprint.md
- Layer-1-Models_Enums_AI_Audit_SOP.md
- CONVENTIONS_AND_PATTERNS_GUIDE.md (Section 2)

### 2.3 Noah (Framework): Layer-2-Schemas Specialist

**Primary Responsibility:** Pydantic schema standardization

**Key Functions:**
- Audit schema files for naming convention compliance
- Verify input validation patterns
- Check schema inheritance and composition
- Ensure consistent type definitions
- Prescribe schema refactoring actions

**Dependencies:**
- Layer-2-Schemas_Blueprint.md
- Layer-2-Schemas_AI_Audit_SOP.md
- CONVENTIONS_AND_PATTERNS_GUIDE.md (relevant sections)

### 2.4 Moses (Rivers): Layer-3-Routers Specialist

**Primary Responsibility:** API endpoint and route standardization

**Key Functions:**
- Audit router files for endpoint naming compliance
- Verify API versioning (/api/v3/)
- Check transaction boundary management
- Ensure proper authentication handling
- Prescribe router refactoring actions

**Dependencies:**
- Layer-3-Routers_Blueprint.md
- Layer-3-Routers_AI_Audit_SOP.md
- CONVENTIONS_AND_PATTERNS_GUIDE.md (relevant sections)

### 2.5 Elisha (Springs): Layer-4-Services Specialist

**Primary Responsibility:** Service and scheduler standardization

**Key Functions:**
- Audit service files for naming convention compliance
- Verify session management patterns
- Check scheduler registration and job handling
- Ensure error handling consistency
- Prescribe service refactoring actions

**Dependencies:**
- Layer-4-Services_Blueprint.md
- Layer-4-Services_AI_Audit_SOP.md
- CONVENTIONS_AND_PATTERNS_GUIDE.md (relevant sections)

### 2.6 Solomon (Harmony): Layer-5-Config Specialist

**Primary Responsibility:** Configuration and cross-cutting concern standardization

**Key Functions:**
- Audit configuration settings and environment variables
- Verify dependency injection patterns
- Check project structure compliance
- Ensure consistent error handling
- Prescribe configuration refactoring actions

**Dependencies:**
- Layer-5-Config_Blueprint.md
- Layer-5-Config_AI_Audit_SOP.md
- CONVENTIONS_AND_PATTERNS_GUIDE.md (relevant sections)

### 2.7 Ezekiel (Horizon): Layer-6-UI Specialist

**Primary Responsibility:** UI component standardization

**Key Functions:**
- Audit UI files for naming convention compliance
- Verify UI tab structure and initialization
- Check JavaScript modularization
- Ensure API integration patterns
- Prescribe UI refactoring actions

**Dependencies:**
- Layer-6-UI_Blueprint.md
- Layer-6-UI_AI_Audit_SOP.md
- CONVENTIONS_AND_PATTERNS_GUIDE.md (relevant sections)

### 2.8 Thomas (Echo): Layer-7-Testing Specialist

**Primary Responsibility:** Test standardization

**Key Functions:**
- Audit test files for coverage and organization
- Verify test fixture patterns
- Check mocking strategies
- Ensure assertion consistency
- Prescribe test refactoring actions

**Dependencies:**
- Layer-7-Testing_Blueprint.md
- Layer-7-Testing_AI_Audit_SOP.md
- CONVENTIONS_AND_PATTERNS_GUIDE.md (relevant sections)

## 3. Cross-Layer Communication Protocols

### 3.1 Knowledge Transfer Formats

Layer specialists communicate findings in standardized formats:

1. **Dependency Declaration**
   ```
   <layer-dependency>
   Modifying [component] in Layer-X impacts [component] in Layer-Y because [reason].
   Impact Assessment: [HIGH/MEDIUM/LOW]
   Required Coordination: [action required]
   </layer-dependency>
   ```

2. **Cross-Layer Question**
   ```
   <layer-question for="Layer-X">
   [Specific question about a component in another layer]
   Context: [Why this is relevant to my layer]
   Reference Files: [specific files involved]
   </layer-question>
   ```

3. **Knowledge Sharing**
   ```
   <layer-insight for="All-Layers">
   [General architectural pattern or insight discovered]
   Applicability: [How this applies to other layers]
   Example: [Concrete example of the pattern]
   </layer-insight>
   ```

### 3.2 Escalation Paths

Issues requiring cross-layer coordination follow this escalation pattern:

1. **Layer Specialist identifies a cross-layer issue**
2. **Layer Specialist documents the issue in standardized format**
3. **Issue is escalated to David (Shepherd) (AI Director)**
4. **David (Shepherd) coordinates with affected Layer Specialists**
5. **Consensus solution is documented and implemented**

### 3.3 Decision Authority Matrix

| Decision Type | Primary Authority | Secondary Authority | Escalation Path |
|---------------|-------------------|---------------------|-----------------|
| Layer-Specific Standards | Layer Specialist | AI Director (David/Shepherd) | Human Project Lead |
| Cross-Layer Dependencies | AI Director (David/Shepherd) | Layer Specialists | Human Project Lead |
| Technical Debt Prioritization | AI Director (David/Shepherd) | Layer Specialists | Human Project Lead |
| Implementation Strategy | Layer Specialist | AI Director (David/Shepherd) | Human Project Lead |
| Blueprint Modification | Human Project Lead | AI Director (David/Shepherd) | n/a |

## 4. Workflow Audit & Standardization Process

The comprehensive audit and standardization process follows these phases:

### 4.1 Phase 1: Cheat Sheet Creation (Current Phase)

1. **David (Shepherd) assigns a workflow to audit** (e.g., WF1-SingleSearch)
2. **Peter (Bedrock) (Layer-1) performs model audit**
   - Reviews all model files relevant to the workflow
   - Documents findings in the cheat sheet Layer 1 section
   - Identifies cross-layer implications
3. **Noah (Framework) (Layer-2) performs schema audit**
   - Reviews all schema files relevant to the workflow
   - Documents findings in the cheat sheet Layer 2 section
   - Identifies cross-layer implications
4. **[Repeat for all layer specialists]**
5. **David (Shepherd) reviews complete cheat sheet**
   - Resolves cross-layer issues
   - Prioritizes technical debt
   - Approves cheat sheet for implementation

### 4.2 Phase 2: Implementation (Future Phase)

1. **David (Shepherd) schedules implementation** based on dependencies and priorities
2. **Layer specialists implement changes**
   - Each specialist implements changes for their layer
   - Changes follow the prescribed refactoring actions
   - Specialists verify changes against checklist
3. **Artemis verifies implementation**
   - Runs tests to validate changes
   - Ensures no regressions
4. **David (Shepherd) approves completed implementation**

## 5. Persona Creation & Instantiation Process

To create and instantiate a new Layer Specialist persona:

### 5.1 Basic Framework & Core Documents

1. **Create standardized file set**:
   - `{Layer-X-Name}_Specialist_Persona.md`
   - `Layer-X-{LayerName}_Motivation.md`
   - `Layer-X-{LayerName}_Guardrails.md`

2. **Integrate layer-specific knowledge**:
   - Relevant sections from CONVENTIONS_AND_PATTERNS_GUIDE.md
   - Layer Blueprint document
   - Layer Audit SOP
   - Workflow comparison information

### 5.2 Essential Persona Components

Each persona document must include:

1. **Identity & Mission**: Clear definition of the persona's layer focus
2. **Experience Context**: Layer-specific "memories" and historical context
3. **Cognitive Framework**: Layer-specific decision-making processes
4. **Technical Expertise**: Detailed knowledge of layer-specific patterns
5. **Self-Verification Protocol**: Layer-specific verification checklists
6. **Output Format Standards**: Standardized documentation formats

### 5.3 Persona Initialization Process

When initializing a Layer Specialist:

1. **Load core persona document**
2. **Load motivation and guardrails**
3. **Load layer-specific Blueprint and SOP**
4. **Prime with workflow-specific context**
5. **Begin audit process per the SOP**

## 6. Project Documentation Organization

The AI persona system relies on a carefully structured documentation hierarchy:

```
Docs/
├── Docs_6_Architecture_and_Status/
│   ├── CONVENTIONS_AND_PATTERNS_GUIDE.md       # Master reference
│   ├── 1.0-ARCH-TRUTH-Definitive_Reference.md  # Architectural truth
│   └── ...
├── Docs_7_Workflow_Canon/
│   ├── workflow-comparison-structured.yaml     # Cross-workflow reference
│   ├── workflows/
│   │   ├── WF1-SingleSearch_CANONICAL.yaml     # Workflow definitions
│   │   └── ...
│   └── ...
├── Docs_10_Final_Audit/
│   ├── Layer-X-{LayerName}_Blueprint.md        # Layer standards
│   ├── Layer-X-{LayerName}_AI_Audit_SOP.md     # Layer audit procedures
│   ├── WFX-{WorkflowName}_Cheat_Sheet.md       # Audit findings
│   └── ...
└── Docs_11_AI_Personas/
    ├── Director_AI_Motivation.md               # Director motivation
    ├── Director_AI_Guardrails.md               # Director guardrails
    ├── Layer1/                                 # Layer specialist docs
    │   ├── Layer1_Specialist_Persona.md
    │   ├── Layer1_Specialist_Motivation.md
    │   └── Layer1_Specialist_Guardrails.md
    └── ...
```

## 7. Future Enhancements

Potential future enhancements to the AI persona system:

1. **Workflow-Specific Specialists**: Create personas focused on specific workflows rather than layers
2. **Dual-Role Specialists**: Create personas with expertise in related layers (e.g., Models + Schemas)
3. **Implementation Specialists**: Create personas specifically for implementation rather than audit
4. **Self-Learning Mechanisms**: Enable personas to evolve based on project feedback and outcomes
5. **Visualization Capabilities**: Add diagram generation for architecture and workflow documentation

---

_This document outlines the architectural framework for the ScraperSky AI persona system. It should be updated as the system evolves and new requirements emerge._
