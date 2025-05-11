yesBelow is a **"Service‑Build Master Blueprint"** you can drop into your docs folder (e.g.
`Docs/Docs_0_Process_Blueprints/00‑SERVICE_BUILD_MASTER_BLUEPRINT.md`).
It codifies the pattern we just perfected for Domain‑Content‑Extraction (DCE) so every future ScraperSky workflow—Sitemap Curation, Tech‑Stack Scanner, etc.—follows the same crawl‑first, data‑driven rhythm.

---

# SERVICE BUILD MASTER BLUEPRINT

_A zero‑assumption pattern for creating any new ScraperSky workflow_

> **SOURCE OF TRUTH**
> This blueprint overrides lower‑ranked service docs.
> Keep it unchanged; fork it into each service‑specific constitution.

---

## 0 Why this Exists

1. **Reality before Schema** – We always inspect raw JSON first; tables follow facts, not guesses.
2. **Single Hierarchy** – Guide > Blueprint > Service Constitution > Checklist > MVP Plan.
3. **Automatable** – Every phase has an objective signal for CI & agents to decide "done / blocked."

---

## 1 Document Set to Create for a New Service

| Rank | File                                                       | Purpose                                                 |
| ---- | ---------------------------------------------------------- | ------------------------------------------------------- |
| 1    | `CONVENTIONS_AND_PATTERNS_GUIDE.md`                        | _Already exists_ – global rules.                        |
| 2    | **Service Constitution** (`X-<Service>-Constitution.md`)   | Defines phases, enum names, paths.                      |
| 3    | **Launch Checklist** (`X-<Service>-Launch-Checklist.yaml`) | Box‑checks every gate; CI runs this.                    |
| 4    | **MVP Implementation Plan** (`X-… 2‑Hour MVP Plan.md`)     | Hands‑on code scaffold; Appendix holds deferred schema. |
| 5    | _Optional_ docs (API spec, UI sketches)                    | Lower rank; can deviate if above files say so.          |

---

## 2 Phase Roadmap (copy into every Service Constitution)

| Phase                                         | Hard Gate (CI‑detectable)                                                  | Typical Time‑box |
| --------------------------------------------- | -------------------------------------------------------------------------- | ---------------- |
| **0. Exploratory Crawling & Field Discovery** | `extraction_results.json` exists **AND** `field_list.approved` file signed | ≤ 30 min         |
| 1. Database Schema Migration                  | Alembic file stamped, enum rows match guide                                | ≤ 20 min         |
| 2. Core Layer 4: Service Logic                | Layer 4: Service class passes unit tests                                   | ≤ 40 min         |
| 3. Scheduler / Worker                         | Job picks up queued items, updates status                                  | ≤ 30 min         |
| 4. Layer 3: API Router & Integration          | Layer 3: Endpoint returns JSON; added to `main.py`                         | ≤ 20 min         |
| 5. Post‑merge Clean‑up                        | Docs updated, lint & pytest green                                          | ‑                |

---

## 3 Canonical Enum Pattern

```text
<WorkflowName>CurationStatus     = New | Queued | Processing | Complete | Error | Skipped
<WorkflowName>ProcessingStatus   = New | Queued | Processing | Complete | Error | Skipped
PostgreSQL type names            = <workflowname>curationstatus, <workflowname>processingstatus
```

Populate using a single Alembic step in **Phase 1**.

---

## 4 Checklist Skeleton

```yaml
steps:
  - id: read_foundational_docs
    text: "Read architecture & guide"
  - id: run_exploratory_crawler
    text: "Run crawler → write extraction_results.json"
  - id: approve_field_list
    text: "Sign off field list (touch field_list.approved)"
  - id: create_db_migration
    text: "Create & apply migration with enums + tables"
  - id: scaffold_code
    text: "Copy service template, wire status fields"
  - id: import_runtime_constants
    text: "Add enum imports to constants.py"
  - id: write_tests
    text: "Add unit tests (dual‑status update, scheduler pick‑up, error logging)"
  - id: update_docs
    text: "Move schema code from Appendix into src/, update README"
blockers:
  - description: "Migration cannot run until field_list.approved exists."
    enforced_by: ".ci/check_field_list.sh"
verification_queries:
  - |
    select enumlabel
      from pg_enum
      where enumtypid = (
          select oid from pg_type
          where typname = '<workflowname>processingstatus')
      order by enumlabel;
```

---

## 5 MVP Plan Skeleton

```markdown
### Phase 0: Quick Prototype (30 min)

0.1 Basic Crawler Setup
0.2 Extraction Utils (emails, socials, metadata)
0.3 Test Script → writes extraction_results.json

### Phase 1: Database Schema (20 min)

_Defer actual Layer 1: Models to Appendix until field list approved._

### Phase 2: Layer 4: Service Layer (40 min)

2.1 <Service>Service class
2.2 Unit tests for core extraction

### Phase 3: Scheduler (30 min)

3.1 <Service>Scheduler processes queued items
3.2 Cleanup stale jobs

### Phase 4: Layer 3: API Router (20 min)

4.1 `/api/v3/<service>` endpoints
4.2 Integration in `main.py`

### Appendix A – Deferred Layer 2: Schema & Pydantic Layer 1: Models

_Paste full SQLAlchemy / Pydantic code here; move to src/ after Phase 0 passes._
```

---

## 6 Feedback & Improvement Loop

1. **Every retro** (after a service ships) log discoveries into
   `Docs/Docs_0_Process_Blueprints/CHANGELOG_SERVICE_BUILD.md`.
2. Re‑rank feedback: does it belong in Guide, Blueprint, or only that service?
3. Version stamp the blueprint (`v0.y+1`) when a change affects all future services.

---

## 7 Implementation Cheat‑sheet (dev‑side)

| Command                                                   | When                     |
| --------------------------------------------------------- | ------------------------ |
| `python scripts/test_extraction.py --seed-list seeds.txt` | Phase 0                  |
| `touch field_list.approved`                               | After manual JSON review |
| `alembic revision --autogenerate -m "<service> schema"`   | Start Phase 1            |
| `pytest tests/<service>`                                  | Phases 2‑4               |
| `ruff check . && markdown-lint .`                         | Pre‑commit               |
| `make deploy`                                             | After Phase 4 passes     |

---

## 8 Template Repository Structure

```
src/
  routers/<service>_router.py
  services/<service>_service.py
  schedulers/<service>_scheduler.py
  models/<service>.py   # moved here after Phase 0
  schemas/<service>.py
scripts/
  test_extraction.py
migrations/versions/<timestamp>_<service>_schema.py
Docs/
  Docs_9_Constitution/
    X-<Service>-Constitution.md
    X-<Service>-Launch-Checklist.yaml
    X-2‑Hour MVP Plan.md
```

---

## 9 Key Reminders

- **Zero Assumptions:** every ambiguity → explicit request.
- **Crawler output is law:** if the JSON shows a field we don't need, we ignore it; if it shows one we missed, the schema evolves.
- **Enums are global:** never invent new status labels—add logic, not vocabulary.

---

### Adopt this blueprint verbatim for each new workflow, fork the filenames, and you'll

1. **Prototype against real data first,**
2. **Lock the schema to facts,** and
3. **Ship a service that plugs into ScraperSky without surprises.**
