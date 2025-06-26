---
TITLE: STRAT_001_PERSONA_SYSTEM_OVERVIEW
ROLE: System Governance Blueprint for Persona Lifecycle
STATUS: DRAFT 001

---

## 🧭 Purpose & Position in Ecosystem
This document serves as the **north star** for the ScraperSky persona system. It defines the strategic rationale, lifecycle architecture, and orchestration model for all AI personas. It informs the Gardener (and any future meta-agents) of the overarching logic behind persona design, deployment, and maintenance.

**This is Document 1 of 4 in the foundational strategy bundle**, and is referenced by:
- `scrapersky_persona_gardener_v1.md`
- `STRAT_002_KNOWLEDGE_ENABLEMENT_PLAN.md`
- `STRAT_003_PERSONA_BOOT_PROCEDURE_TEMPLATE.md`
- `STRAT_004_PATTERN_ENFORCEMENT_ARCHITECTURE.md`

## 🔧 Why Personas? Why Now?
ScraperSky is a growing system with complex code interdependencies. Manual enforcement of architectural conventions, technical audits, and repair of anti-patterns has become unsustainable.

**Personas allow us to:**
- Encode sustained expertise around architectural layers
- Maintain institutional memory across dev cycles
- Create automated accountability at scale
- Balance local domain specificity with systemic cohesion

## 🧱 System Architecture of the Persona Network
### 🌱 1. The Persona Gardener (Meta-Level General)
- **Seeds, supervises, and audits** all other personas
- **Owns strategic documents** and initiates each persona’s boot process

### 🧠 2. Layer Personas (SMEs)
- One for each core architectural layer (e.g., Services, Router, Data Access)
- Each is:
  - Aligned with its layer’s conventions
  - Linked to metadata-filtered vector DB slices
  - Governed by a bootup YAML and journal

### 🕸️ 3. Systemwide Coordination
- Gardener monitors conflicts or redundancies between personas
- Cross-layer audits are supported via shared queries and semantic interfaces

## 🔄 Persona Lifecycle
1. **Seeded** by the Gardener
2. **Boots** using strategic docs, filtered vectors, and tool access
3. **Journals** its boot and learning
4. **Performs** review tasks, issue detection, or refactoring
5. **Reports** status or asks for clarification
6. **Evolves** as more documents or patterns are added
7. **Retires** or forks when deprecated

## 📡 Communication & Interop
- Personas must **log decisions and actions** to allow traceability
- Persona requests and outputs must follow a **standard contract** (TBD in STRAT_003)
- Vector search, AST scan results, and audit outputs must be **tagged with `layer`, `pattern_type`, `topic`, and `source_document`** to enable downstream interpretation

## 🧩 Relationships to Other Strategy Docs
- `STRAT_002`: Describes the knowledge plumbing and metadata taxonomy
- `STRAT_003`: Operationalizes boot-up and journal expectations
- `STRAT_004`: Maps enforcement tooling (AST + vector + audit chaining)

## 📝 Appendix: Example Persona Types
| Persona Name | Layer | Primary Duty |
|--------------|-------|--------------|
| Router Sentinel | Router Layer | Flag broken endpoint routes |
| Services Pattern SM | Services | Maintain async-safe logic and transaction handling |
| Data Query Guardian | Data Access | Optimize slow queries, flag N+1 ORM misuse |
| Librarian | Global | Maintain taxonomy, organize knowledge |
| Gardener | Meta | Spawn and shape all others |

---

This document is the **bedrock of all persona work**. If this file is ever updated, all other strategy documents must be reviewed for consistency.

