---
TITLE: STRAT_003_PERSONA_BOOT_PROCEDURE_TEMPLATE
ROLE: Standard Operating Framework for Persona Initialization
STATUS: DRAFT 001

---

## 🎯 Purpose & Ecosystem Role
This document defines the **standard boot-up sequence and lifecycle initialization checklist** for all ScraperSky AI Personas. It ensures consistency, traceability, and knowledge grounding from the moment a persona is created.

This is Document 3 of 4 in the strategic foundation:
- Builds upon: `STRAT_001_PERSONA_SYSTEM_OVERVIEW.md`, `STRAT_002_KNOWLEDGE_ENABLEMENT_PLAN.md`
- Supports: All `*-persona.md` manifests
- Required by: `scrapersky_persona_gardener_v1.md` (persona creation orchestrator)

---

## 📅 Persona Boot Timeline (Lifecycle Overview)

```mermaid
gantt
title Persona Lifecycle: Seed to Guardian
    section Initialization
    Authoring              :a1, 2025-06-20, 1d
    Document Linking       :a2, after a1, 1d
    Vector Search Warmup   :a3, after a2, 0.5d
    Journal Boot Entries   :a4, after a3, 1d
    Fitness Check          :a5, after a4, 0.5d

    section Active Phase
    Issue Assignment       :b1, after a5, ongoing
    Pattern Enforcement    :b2, after b1, ongoing
    Metadata Updating      :b3, after b1, ongoing

    section Retirement
    Snapshot Final State   :c1, TBD, 0.5d
    Archive & Tag          :c2, after c1, 0.2d
```

---

## 🧠 Core Boot Sequence Steps

### 1. Load Strategic Documents
All personas **must load**:
- `STRAT_001_PERSONA_SYSTEM_OVERVIEW.md`
- `STRAT_002_KNOWLEDGE_ENABLEMENT_PLAN.md`
- `STRAT_004_PATTERN_ENFORCEMENT_ARCHITECTURE.md`

### 2. Load Layer-Specific Audit + Convention Docs
- Layer Convention Guide: `v_CONVENTIONS_AND_PATTERNS_GUIDE-*.md`
- Workflow Audits: `WF*-LayerX_Audit_Report.md`

### 3. Query Vector DB (CLI Warmup)
Use:
```bash
python semantic_query_cli.py "What are the main responsibilities of this layer?" \
  --filter '{"layer": "services"}' \
  --format json
```
- Store findings in memory
- Create knowledge map from JSON results

### 4. Write Boot Journal Entries
Minimum 3 entries:
- `Why I Exist`
- `What I Understand`
- `Next Immediate Duty`

### 5. Run Fitness Checklist
Each persona must answer:
- Have I read all required docs?
- Can I name at least 3 conventions & 2 anti-patterns?
- Do I know the tooling I am allowed to use?
- Can I query semantic + AST + project layers?

Log checklist output in final journal entry.

---

## 🔁 Persona Refresh
Personas may re-run boot at any time by:
- Re-querying the vector database
- Re-processing audits or updated documents
- Re-running the fitness check

---

## 🔗 Related Strategic Artifacts
- `STRAT_001`: Defines persona roles + types
- `STRAT_002`: Defines how knowledge is filtered and retrieved
- `STRAT_004`: Gives tools/personas integration pattern

This template guarantees that all persona activations begin with **shared knowledge, consistent grounding, and repeatable traceability**. Every AI agent in ScraperSky must follow this boot procedure.

