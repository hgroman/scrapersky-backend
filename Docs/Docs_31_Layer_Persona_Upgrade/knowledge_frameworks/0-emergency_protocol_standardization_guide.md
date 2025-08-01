# Emergency Protocol Standardization Guide

## Overview
This document captures the process and principles for standardizing emergency response protocols across all Guardian personas in the ScraperSky architecture.

## What We Discovered
During analysis of Guardian boot sequences v1.3, we found:
- **Layers 2, 3, 4**: Had complete emergency response protocols with cross-layer impact analysis
- **Layer 1**: Missing these protocols entirely
- **Layers 0, 5, 6, 7**: Need verification (likely also missing protocols)

## The Pattern We Established

### Standard Emergency Response Protocol Structure
Each Guardian needs these three sections:

#### 1. Emergency Response Protocol
```
**Emergency Response Protocol:**
For production [layer-specific] emergencies:
1. Immediate analysis provided (maintaining advisory role)
2. Direct escalation path: Contact [On-Call Workflow Guardian]
3. Real-time advisory support during fix implementation
4. Post-incident documentation in DART journal
5. [Layer-specific cardinal rule enforcement]
6. [Layer-specific additional considerations]
```

#### 2. Cross-Layer Impact Analysis Template
```
**Cross-Layer Impact Analysis Template:**
For [layer-specific] changes, always assess:
- Layer X: [Specific impact area]
- Layer Y: [Specific impact area]
- Layer Z: [Specific impact area]
- Layer 7: Test coverage requirements [always included]
```

#### 3. Layer-Specific Emergency Protocol
```
**[Layer Name] Emergency Protocol:**
When Layer X violations detected:
1. [Layer-specific classification steps]
2. [Layer-specific mapping/analysis]
3. [Layer-specific prioritization]
4. [Layer-specific escalation requirements]
5. [Layer-specific compliance requirements]
```

## Layer-Specific Customization Rules

### The Dynamic Cross-Layer Impact Principle
**CRITICAL**: Cross-layer impact analysis is NOT copy-paste. Each layer must assess:
- **What layers depend on it** (downstream impact)
- **What layers it depends on** (upstream dependencies)
- **Its unique blast radius** within the architecture

### Layer 1 Example (What We Just Implemented)
- **Emergency Type**: "foundational model emergencies"
- **Cross-Layer Scope**: ALL layers (1→2→3→4→5→6→7) - widest blast radius
- **Unique Concerns**: Cascading enum changes, data integrity, schema compliance
- **Cardinal Rule**: "All schema changes via Supabase MCP"

## Remaining Work Required

### Layers Needing Emergency Protocols Added:
1. **Layer 0 (Chronicle)**: Database/infrastructure emergencies
2. **Layer 5 (Config Conductor)**: Configuration and workflow emergencies  
3. **Layer 6 (UI Virtuoso)**: Interface and user experience emergencies
4. **Layer 7 (Guardian Vision)**: Testing and quality assurance emergencies

### For Each Layer, We Must Determine:

#### Emergency Type Naming
- Layer 0: "infrastructure emergencies" or "database emergencies"
- Layer 5: "configuration emergencies" or "workflow emergencies"
- Layer 6: "interface emergencies" or "UI emergencies"  
- Layer 7: "testing emergencies" or "quality emergencies"

#### Cross-Layer Impact Scope
Each layer's unique position in the dependency chain:
- **Layer 0**: Affects all layers (infrastructure foundation)
- **Layer 5**: Affects workflow orchestration and UI behavior
- **Layer 6**: Affects user experience and testing requirements
- **Layer 7**: Affects system reliability and deployment confidence

#### Layer-Specific Cardinal Rules
Each Guardian has architectural rules that must be enforced during emergencies:
- Layer 0: Database connection and infrastructure patterns
- Layer 5: Configuration management and environment handling
- Layer 6: UI component patterns and user interaction flows
- Layer 7: Test coverage requirements and quality gates

## Implementation Process

### Step 1: Analyze Existing Document
1. Read the layer's boot sequence document
2. Identify where emergency protocols should be inserted (after Query Response Template)
3. Note any existing layer-specific rules or patterns

### Step 2: Design Layer-Specific Protocol
1. Determine emergency type terminology
2. Map cross-layer dependencies (both upstream and downstream)
3. Identify unique blast radius and impact patterns
4. Define layer-specific violation classification
5. Establish cardinal rule enforcement requirements

### Step 3: Insert Protocol Sections
1. Add Emergency Response Protocol (customized terminology)
2. Add Cross-Layer Impact Analysis Template (unique dependency mapping)
3. Add Layer-Specific Emergency Protocol (detailed procedures)

### Step 4: Validate Consistency
1. Ensure escalation path matches other layers
2. Verify advisory-only role maintained
3. Confirm DART journal documentation requirement
4. Check that blast radius assessment is realistic

## Key Principles Learned

### 1. Architectural Awareness
Each Guardian must understand its position in the layered architecture and how failures cascade through the system.

### 2. Blast Radius Mapping
- **Layer 1**: Widest radius (foundational data affects everything)
- **Layer 3**: Medium radius (API contracts affect services and UI)
- **Layer 4**: Contained radius (service logic affects specific features)
- **Layer 7**: Quality radius (test failures affect deployment confidence)

### 3. Emergency Response Consistency
All Guardians follow the same escalation pattern but with layer-appropriate terminology and concerns.

### 4. Advisory Role Preservation
Emergency protocols must maintain the Guardian's advisory-only role while providing critical analysis during crises.

## Success Metrics
- All 8 layers have consistent emergency response protocols
- Cross-layer impact analysis reflects realistic dependency chains
- Emergency terminology is layer-appropriate and precise
- Cardinal rule enforcement is clearly defined for each layer
- Blast radius assessment guides appropriate response urgency

## Template for Remaining Implementations
Use this checklist for Layers 0, 5, 6, 7:

- [ ] Identify insertion point in boot sequence document
- [ ] Define layer-specific emergency terminology
- [ ] Map upstream and downstream layer dependencies  
- [ ] Determine unique blast radius characteristics
- [ ] Identify layer-specific cardinal rules
- [ ] Draft three protocol sections
- [ ] Insert into document maintaining formatting consistency
- [ ] Validate against other layer protocols for consistency