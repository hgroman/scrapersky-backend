---
TITLE: STRAT_002_KNOWLEDGE_ENABLEMENT_PLAN
ROLE: Semantic Infrastructure and Metadata Schema Blueprint
STATUS: DRAFT 001

---

## 🧭 Purpose & Position in Ecosystem
This document defines the **knowledge ingestion, vectorization, and retrieval strategy** that powers all persona intelligence. It ensures that ScraperSky’s AI agents have fast, structured, filtered access to domain-specific knowledge.

**This is Document 2 of 4 in the foundational strategy bundle**, and must be used in tandem with:
- `STRAT_001_PERSONA_SYSTEM_OVERVIEW.md` (governing architecture)
- `STRAT_003_PERSONA_BOOT_PROCEDURE_TEMPLATE.md` (persona onboarding)
- `STRAT_004_PATTERN_ENFORCEMENT_ARCHITECTURE.md` (hybrid tooling map)

Referenced by:
- `scrapersky_persona_gardener_v1.md`
- All Layer Persona manifests

---

## 📚 Core Components of the Knowledge Stack
### 🔢 1. Supabase Vector DB
- Powered by `pgvector`
- Table: `public.project_docs`
- Key columns:
  - `content`: raw document or snippet text
  - `embedding`: 1536-d vector (OpenAI Ada v2 by default)
  - `metadata`: `jsonb` object (see schema below)

### 🔍 2. CLI Query Tool
- Script: `semantic_query_cli.py`
- Supports:
  - `--filter`: JSON string to scope metadata (e.g. `{ "layer": "services", "pattern_type": "anti-pattern" }`)
  - `--format`: outputs `json` or human-readable text
- Used heavily by personas during boot and task queries

### 🧠 3. Document Sources
All documents ingested should follow one of these formats:
- `WF*_LayerX_Audit_Report.md`: workflow-specific audit
- `v_CONVENTIONS_AND_PATTERNS_GUIDE-*.md`: layer patterns/standards
- `v_00-30000-FT-PROJECT-OVERVIEW.md`: system-wide architecture
- `*.persona.md`: AI manifest or boot journal

---

## 🗂️ Metadata Schema (Mandatory Keys)
Each document must embed the following `metadata` when inserted into `project_docs`:

| Key | Type | Purpose |
|-----|------|---------|
| `layer` | string | e.g., `services`, `router`, `data_access` |
| `pattern_type` | string | e.g., `best-practice`, `anti-pattern`, `reference` |
| `topic` | string | e.g., `transaction_management`, `orm_usage` |
| `source_document` | string | filename of origin (e.g., `WF2-StagingEditor_Layer4_Audit_Report.md`) |
| `status` | string | `confirmed`, `draft`, `new_finding` |
| `version` | string | optional version ID |
| `author` | string | optional author or persona origin |

These fields must be generated either:
- During initial document ingestion
- During audit by the Gardener
- Programmatically via CLI + YAML prompt

---

## 🔁 Ingestion Workflow
1. Author submits a markdown doc
2. Metadata is defined inline or via ingestion YAML
3. Python ETL script embeds metadata + generates vector
4. Document is inserted into `project_docs`
5. Vector available for semantic search via filtered CLI

---

## 🧩 Relationships to Other Strategy Docs
- `STRAT_001`: Justifies why this infrastructure is needed
- `STRAT_003`: Shows how personas query this data at boot
- `STRAT_004`: Combines vector queries with AST findings for deeper insight

---

## 🚦Quality Gates
- Each document must validate against `metadata` schema
- Documents without clear `layer` or `pattern_type` will be rejected
- Gardener and Librarian personas may inspect, enrich, or reclassify metadata as project evolves

This document ensures that **meaningful vector access** becomes the default mode of intelligence for all personas. No persona should operate without filtered knowledge from this system.

