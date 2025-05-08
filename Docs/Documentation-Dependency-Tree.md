# ScraperSky Documentation Dependency Tree

## Overview

This document maps the hierarchical relationships between ScraperSky documentation components, showing which documents serve as authoritative references for others.

```
ScraperSky Documentation Hierarchy
│
├── Foundation Documents (Primary Authority)
│   ├── AI Collaboration Constitution [Docs_8_Document-X/8.0-AI-COLLABORATION-CONSTITUTION.md]
│   ├── 30,000-ft Project Overview [Docs_6_Architecture_and_Status/00-30000-FT-PROJECT-OVERVIEW.md]
│   ├── Core Architectural Principles [Docs_1_AI_GUIDES/17-CORE_ARCHITECTURAL_PRINCIPLES.md]
│   └── Producer-Consumer Pattern [Docs_1_AI_GUIDES/32-PRODUCER_CONSUMER_WORKFLOW_PATTERN.md]
│
├── Architectural Guides (Secondary Authority)
│   ├── AI Guides [Docs_1_AI_GUIDES/]
│   │   ├── Database Standards
│   │   │   ├── 01-ABSOLUTE_ORM_REQUIREMENT.md
│   │   │   ├── 07-DATABASE_CONNECTION_STANDARDS.md
│   │   │   ├── 13-TRANSACTION_MANAGEMENT_GUIDE.md
│   │   │   ├── 18-DATABASE_SCHEMA_CHANGE_GUIDE.md
│   │   │   ├── 20-DATABASE_CONNECTION_ASYNCPG_COMPATIBILITY.md
│   │   │   ├── 25-SQLALCHEMY_MODEL_INTEGRITY_GUIDE.md
│   │   │   ├── 27-ENUM_HANDLING_STANDARDS.md
│   │   │   ├── 29-DATABASE_ENUM_ISOLATION.md
│   │   │   └── 31.1-MCP-MIGRATION-GUIDE.md ← Depends on 18-DATABASE_SCHEMA_CHANGE_GUIDE.md
│   │   │
│   │   ├── API Standards
│   │   │   ├── 15-API_STANDARDIZATION_GUIDE.md
│   │   │   ├── 23-FASTAPI_ROUTER_PREFIX_CONVENTION.md
│   │   │   └── 30-STANDARD_DEPENDENCY_INJECTION_PATTERNS.md
│   │   │
│   │   ├── Authentication
│   │   │   ├── 08-RBAC_SYSTEM_SIMPLIFIED.md
│   │   │   ├── 09-TENANT_ISOLATION_REMOVED.md
│   │   │   └── 11-AUTHENTICATION_BOUNDARY.md
│   │   │
│   │   ├── Scheduler Standards
│   │   │   ├── 21-SCHEDULED_TASKS_APSCHEDULER_PATTERN.md
│   │   │   ├── 24-SHARED_SCHEDULER_INTEGRATION_GUIDE.md
│   │   │   └── 28-SCHEDULER_AND_SETTINGS_PATTERNS.md
│   │   │
│   │   └── Core Patterns
│   │       ├── 32-PRODUCER_CONSUMER_WORKFLOW_PATTERN.md
│   │       └── 33-BACKGROUND_SERVICES_ARCHITECTURE.md
│   │
│   └── Architecture & Status [Docs_6_Architecture_and_Status/]
│       ├── 00-30000-FT-PROJECT-OVERVIEW.md
│       ├── CONVENTIONS_AND_PATTERNS_GUIDE.md
│       └── Implementation Status [0.2_ScraperSky_Architecture_and_Implementation_Status.md]
│
├── Implementation Templates (Tertiary Authority)
│   ├── Workflow Builder Cheat Sheet [Docs_8_Document-X/ScraperSky Workflow-Builder-Cheat-Sheet-TEMPLATE-Enhanced.md]
│   │   └── Depends on: 32-PRODUCER_CONSUMER_WORKFLOW_PATTERN.md, 31.1-MCP-MIGRATION-GUIDE.md
│   │
│   ├── Session Context Documents [Docs_8_Document-X/8.1-AI-SESSION-CONTEXT-PAGE-CURATION.md]
│   │   └── Depends on: 8.0-AI-COLLABORATION-CONSTITUTION.md, Workflow-Builder-Cheat-Sheet-TEMPLATE-Enhanced.md
│   │
│   ├── Canonical Workflow Definitions [Docs_7_Workflow_Canon/workflows/WF*_CANONICAL.yaml]
│   │   └── Depends on: 32-PRODUCER_CONSUMER_WORKFLOW_PATTERN.md
│   │
│   └── Domain Content Constitution [Docs_9_Constitution/]
│       ├── Domain-Content-Extraction-Constitution.md
│       ├── Domain-Content-Extraction-Audit-Request.md
│       └── Domain-Content-Extraction-Launch-Checklist.md
│
├── Workflow Reference Implementations (Quaternary Authority)
│   ├── Dependency Traces [Docs_7_Workflow_Canon/Dependency_Traces/]
│   │   ├── WF1-Single Search.md
│   │   ├── WF2-Staging Editor.md
│   │   ├── WF3-Local Business Curation.md
│   │   ├── WF4-Domain Curation.md
│   │   ├── WF5-Sitemap Curation.md
│   │   ├── WF6-SitemapImport_dependency_trace.md
│   │   └── WF7-Page Curation.md
│   │
│   └── Linear Steps [Docs_7_Workflow_Canon/Linear-Steps/]
│       ├── WF1-SingleSearch_linear_steps.md
│       ├── WF2-StagingEditor_linear_steps.md
│       ├── WF3-LocalBusiness_linear_steps.md
│       ├── WF4-DomainCuration_linear_steps.md
│       ├── WF5-SitemapCuration_linear_steps.md
│       └── WF6-SitemapImport_linear_steps.md
│
└── Project Working Documents (Implementation Specific)
    ├── Working Implementation Plans [Docs_5_Project_Working_Docs/]
    │   ├── Database Consolidation [02-database-consolidation/]
    │   ├── Tenant Isolation Removal [06-tenant-isolation/]
    │   └── Google Maps Integration [07-Google-Maps-to-Local-Miner/]
    │
    └── File Audits [Docs_7_Workflow_Canon/Audit/]
        ├── 0-A-ALL-PYTHON-FILES-IN-SRC.md
        ├── 0-B-PYTHON-FILE-LIST.md
        ├── 0-C-AUDIT-FOR-ORPHANS.md
        ├── 1.0-System-Infrastructure-Layer.md
        ├── 1.1-API-Router-Layer.md
        └── 1.2-Background Processing Layer.md
```

## Document Authority Hierarchy

1. **Primary Authority** - Foundational principles that all other documents must respect
   - AI Collaboration Constitution (zero assumptions mandate)
   - Core architectural principles
   - Base workflow pattern definitions

2. **Secondary Authority** - Architectural standards derived from primary documents
   - All AI guides covering database, API, scheduler standards
   - Architecture status documents

3. **Tertiary Authority** - Implementation patterns/templates
   - Workflow builder cheat sheets
   - Session context documents
   - Canonical workflow definitions

4. **Quaternary Authority** - Reference implementations
   - Workflow dependency traces
   - Linear step documents

5. **Implementation Specific** - Project-specific work orders and audits
   - Working implementation plans
   - File audits and cleanup plans

## Key Dependency Relationships

### Critical Path Dependencies

1. All implementation flows from the **Producer-Consumer Workflow Pattern**
   - Defines status-driven workflow
   - Enforces async processing model
   - Establishes database structure requirements

2. **AI Collaboration Constitution** governs all AI interactions
   - Zero assumptions mandate
   - Documentation-first implementation
   - Conflict resolution protocols

3. **Workflow Builder Cheat Sheet** dictates implementation phases
   - Each workflow must follow 5 phases
   - Enforcement of naming conventions
   - Required SQL verification queries

4. **Database Standards** enforce transaction patterns
   - Router-owned transactions
   - Service transaction awareness
   - Background task session management

### Cross-Reference Map

- **Canonical YAML Files** (WF*_CANONICAL.yaml)
  - Reference architectural principles from `/Docs/Docs_1_AI_GUIDES/`
  - Define structure for each workflow implementation
  - Link directly to specific cheat sheet phases

- **Session Context Documents**
  - Reference constitution for authority rules
  - Point to current workflow cheat sheet
  - Specify implementation phase to focus on

- **Background Services Architecture**
  - References scheduler patterns from AI guides
  - Provides implementation examples for background services
  - Establishes integration points with main application

## Document Creation Flow

For implementing a new workflow or feature:

1. Start with **30,000-ft Project Overview** [00-30000-FT-PROJECT-OVERVIEW.md] for context
2. Review the **AI Collaboration Constitution** [8.0-AI-COLLABORATION-CONSTITUTION.md] for rules of engagement
3. Reference **Core Architectural Principles** [17-CORE_ARCHITECTURAL_PRINCIPLES.md] for non-negotiable requirements
4. Study the **Producer-Consumer Pattern** [32-PRODUCER_CONSUMER_WORKFLOW_PATTERN.md] for workflow structure
5. Use **Workflow Builder Cheat Sheet** for implementation phases
6. Follow **Domain Content Constitution** structure for documentation standards
7. Create a **Launch Checklist** for implementation verification
8. Consult relevant **AI Guides** for specific implementation patterns

## Implemented Recommended Documents

The following previously identified documentation gaps have been addressed:

1. ✅ **30,000-ft Project Overview** - Now available at [00-30000-FT-PROJECT-OVERVIEW.md]
2. ✅ **Workflow Documentation Example** - Provided by Domain Content Constitution

## Remaining Recommended Documents

The following recommended documents would further enhance the documentation ecosystem:

1. **Service/Router Cross-Reference Guide** - Mapping between services, routers, and models
2. **End-to-End Testing Cookbook** - Comprehensive testing guide for workflows
3. **Schema Change Impact Analysis Template** - For evaluating cascade effects of schema changes
4. **Workflow Handoff Points Documentation** - Interfaces between workflows
5. **Data Flow Diagram** - Visual representation of data transformations through workflow stages

---

Document created: May 8, 2025
