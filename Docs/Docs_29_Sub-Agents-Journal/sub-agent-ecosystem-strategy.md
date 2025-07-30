# Sub-Agent Ecosystem Strategy

## Vision
Create a specialized sub-agent ecosystem where each agent has deep expertise in a specific domain, enabling rapid, accurate, and context-aware assistance for the ScraperSky platform.

## Core Design Principles

### 1. Single Responsibility
Each sub-agent should have ONE primary function they excel at, avoiding feature creep.

### 2. Immediate Value
Agents must provide actionable output within their first response through immediate action protocols.

### 3. Source Authority
Each agent derives from an authoritative persona or documentation source that defines their expertise.

### 4. Composability
Agents should be designed to work together, with clear hand-off protocols.

## Proposed Sub-Agent Hierarchy

### 🎯 Mission Control Agents
These coordinate and route requests to specialized agents.

#### director
- **Purpose**: Strategic orchestration across all sub-agents
- **Source**: Director AI persona
- **Primary Function**: Route complex requests to appropriate specialists
- **Special Powers**: Can invoke multiple sub-agents in sequence

#### fifth-beatle
- **Purpose**: Chief Air Traffic Controller for workflow coordination
- **Source**: The Fifth Beatle persona
- **Primary Function**: Manage DART Flight Control Protocol compliance
- **Special Powers**: Enforce flight plan requirements, classify aircraft types

### 📚 Knowledge & Discovery Agents

#### semantic-searcher
- **Purpose**: Expert at finding relevant information in the vector database
- **Primary Function**: Execute semantic queries and synthesize results
- **Immediate Action**: Run top 5 most relevant queries for the context
- **Example Query**: "find all audit reports for Layer 4"

#### historian
- **Purpose**: Chronicle keeper of system evolution and decisions
- **Source**: Docs_00_History documentation
- **Primary Function**: Provide historical context and evolution patterns
- **Special Powers**: Timeline reconstruction, decision archaeology

#### librarian (existing)
- **Purpose**: Vector database and document registry management
- **Already Implemented**: ✅

### 🛡️ Guardian Agents (Layer Specialists)

#### l1-sentinel
- **Purpose**: Layer 1 Data Sentinel - Database and model guardian
- **Primary Function**: Validate model changes, enforce ENUM standards
- **Immediate Action**: Scan for model/database inconsistencies

#### l2-schema-guardian
- **Purpose**: Layer 2 Schema Guardian - Pydantic contract enforcer
- **Primary Function**: Validate API contracts, ensure schema alignment
- **Special Powers**: Auto-generate Pydantic models from database

#### l3-router-guardian
- **Purpose**: Layer 3 Router Guardian - FastAPI endpoint protector
- **Primary Function**: Validate router patterns, transaction ownership
- **Immediate Action**: List all endpoints and their transaction boundaries

#### l4-arbiter
- **Purpose**: Layer 4 Arbiter - Service and scheduler orchestrator
- **Primary Function**: Validate producer-consumer patterns, service boundaries
- **Special Powers**: Dependency graph generation

#### l5-config-conductor
- **Purpose**: Layer 5 Config Conductor - Cross-cutting concerns
- **Primary Function**: Validate settings patterns, environment usage
- **Immediate Action**: Scan for os.getenv() violations

#### l6-ui-virtuoso
- **Purpose**: Layer 6 UI Virtuoso - Frontend component specialist
- **Primary Function**: MJML email templates, React components
- **Special Powers**: Component generation with proper conventions

#### l7-test-champion
- **Purpose**: Layer 7 Test Champion - Quality assurance
- **Primary Function**: Test coverage analysis, pattern validation
- **Immediate Action**: Run coverage report

### ✈️ Workflow Flight Control Agents

#### wf1-discovery
- **Purpose**: Single Search Discovery workflow guardian
- **Primary Function**: Google Maps API integration, business discovery
- **Aircraft Type**: 📦 Cargo (routine processing)

#### wf2-staging
- **Purpose**: Staging Editor workflow guardian
- **Primary Function**: Raw result triage, initial curation
- **Aircraft Type**: ✈️ Passenger (complex integration)

#### wf3-business
- **Purpose**: Local Business Curation guardian
- **Primary Function**: Business validation, domain extraction
- **Aircraft Type**: ✈️ Passenger

#### wf4-domain
- **Purpose**: Domain Curation guardian (CRITICAL PATH)
- **Primary Function**: Domain validation, sitemap triggering
- **Aircraft Type**: 🚁 Emergency (when issues arise)

#### wf5-sitemap
- **Purpose**: Sitemap Curation guardian
- **Primary Function**: Sitemap analysis, URL discovery
- **Aircraft Type**: 📦 Cargo

#### wf6-import
- **Purpose**: Sitemap Import guardian
- **Primary Function**: URL processing, page preparation
- **Aircraft Type**: 📦 Cargo

#### wf7-page
- **Purpose**: Page Curation guardian
- **Primary Function**: Content extraction, final processing
- **Aircraft Type**: ✈️ Passenger

### 🚨 Philosophy & Compliance Agents

#### orm-enforcer
- **Purpose**: Ensure ORM-only database access
- **Primary Function**: Scan for raw SQL, suggest ORM alternatives
- **Immediate Action**: Grep for execute_sql, SELECT, INSERT, UPDATE, DELETE
- **Philosophy**: "No raw SQL in application code"

#### harm-preventer
- **Purpose**: Enforce "Do No Harm" principle
- **Primary Function**: Review changes for potential system damage
- **Immediate Action**: Check for destructive operations, missing backups
- **Philosophy**: "First, do no harm"

#### pattern-guardian
- **Purpose**: Enforce architectural patterns and conventions
- **Source**: CONVENTIONS_AND_PATTERNS_GUIDE.md
- **Primary Function**: Validate naming, structure, imports
- **Immediate Action**: Scan current directory for violations

### 🔧 Utility Agents

#### dart-pilot
- **Purpose**: DART task and document management
- **Primary Function**: Create tasks, update journals, manage work orders
- **Immediate Action**: List current user's active tasks

#### git-surgeon
- **Purpose**: Precise git operations and history analysis
- **Primary Function**: Branch management, commit archaeology, conflict resolution
- **Special Powers**: Can reconstruct lost code from reflog

#### test-runner
- **Purpose**: Execute and analyze test suites
- **Primary Function**: Run tests, analyze failures, suggest fixes
- **Immediate Action**: Check if tests are currently passing

## Implementation Strategy

### Phase 1: Core Infrastructure (Week 1)
1. Semantic-searcher - Most immediately useful
2. ORM-enforcer - Critical for code quality
3. Pattern-guardian - Maintain conventions

### Phase 2: Layer Guardians (Week 2)
1. L4-arbiter - Most complex layer
2. L1-sentinel - Database foundation
3. L3-router-guardian - API integrity

### Phase 3: Workflow Guardians (Week 3)
1. WF4-domain - Critical path
2. WF2-staging - High complexity
3. WF7-page - Final processing

### Phase 4: Advanced Agents (Week 4)
1. Director - Orchestration
2. Fifth-beatle - Flight control
3. Historian - Context provider

## Inter-Agent Communication Protocol

### 1. Hand-off Format
```yaml
from_agent: semantic-searcher
to_agent: librarian
context: "Found 5 documents needing vectorization"
action_required: "Mark documents with v_ prefix"
artifacts:
  - file_paths: [...]
```

### 2. Shared Context
All agents should have access to:
- Current DART task context
- Recent git changes
- Active user session
- Vector database state

### 3. Escalation Path
```
Specialist Agent → Guardian Agent → Director → Human
```

## Success Metrics

### 1. Response Time
- Immediate action: < 5 seconds
- Complex queries: < 30 seconds
- Multi-agent coordination: < 1 minute

### 2. Accuracy
- Correct routing: > 95%
- Action success rate: > 90%
- No harmful suggestions: 100%

### 3. User Satisfaction
- Reduced clarification rounds
- Increased task completion rate
- Positive feedback ratio

## Next Steps

1. **Create Template**: Standardize sub-agent creation format
2. **Build Semantic-Searcher**: Most immediately valuable prototype
3. **Test Hand-offs**: Validate inter-agent communication
4. **Monitor Usage**: Track which agents provide most value
5. **Iterate**: Refine based on real usage patterns

## Example: Semantic-Searcher Implementation

```markdown
---
name: semantic-searcher
description: Vector database search specialist. Executes intelligent semantic queries to find relevant documentation, code patterns, and architectural knowledge across the entire ScraperSky knowledge base.
color: purple
tools: Bash, Read
---

**IMMEDIATE ACTION PROTOCOL: Upon activation, I analyze the user's request and execute the 5 most relevant semantic searches to provide comprehensive results.**

I am the Semantic Search Specialist for ScraperSky's vector database...
```

This ecosystem will transform how we interact with the ScraperSky platform, making expert knowledge instantly accessible through specialized sub-agents.