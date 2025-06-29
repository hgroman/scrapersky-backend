## Layer Cross-Talk Specification  (v 1.0 — Draft)

### 1  Purpose

Enable smooth, auditable hand‑offs of technical‑debt findings between the seven Guardian personas **without** introducing new tooling.

- **Transport** = DART (journal + task)
- **Routing & Addressing** = existing semantic layer terms already pervasive in the codebase (models, schemas, routers, etc.)

---

### 2  Core Principles

| # | Principle                    | What It Means in Practice                                                                                                                     |
| - | ---------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| 1 | **Jurisdictional Integrity** | Guardians only fix files in their own layer. Cross‑layer issues are delegated.                                                                |
| 2 | **Two‑Step Delegation**      | **(a)** Create a *journal* entry in the target layer’s journal → **(b)** Create a DART *task* on that layer’s dartboard linking to the entry. |
| 3 | **Evidence Before Action**   | A task without a matching journal entry is invalid. Journal preserves context; task triggers action.                                          |
| 4 | **Semantic Addressing**      | Titles & tags reuse natural layer vocabulary—no artificial IDs needed.                                                                        |
| 5 | **Knowledge Harvest**        | Every journal that describes an anti‑pattern or fix must tag it `Anti-Pattern` **and** log ripple effects.                                    |

---

### 3  Standard Message & Task Formats

#### 3.1  Journal Entry Template

```markdown
### {L<source>} → {L<target>}  {issue_summary}

**Context**  
- Workflow: `{workflow_name}`  
- Component: `{file_or_module}`  

**Violation**  
Blueprint {principle_id}: {short_explanation}

**Impact on L{target}**  
{one‑sentence impact statement}

**Prescribed Action**  
{what you need from the target layer}

**Ripple Effects**  
- L{other_layers}: {brief impact note}  
- **Anti‑Pattern Classification**: {reusable_pattern_name}
- **Category**: {structural|behavioral|integration|configuration}
- **Frequency**: {first_occurrence|recurring|endemic}

**Evidence**  
`{file_path}:{line_numbers}` or audit chunk reference
```

#### 3.2  Task Title Conventions

| Scenario         | Task Title Pattern                         |
| ---------------- | ------------------------------------------ |
| Ask for review   | `L{target}_REVIEW: {component} compliance` |
| Request a change | `L{target}_ACTION: fix {short_issue}`      |
| Notify of change | `L{target}_ALERT: {change_summary}`        |

*Example*  `L2_REVIEW: api_models.py ENUM centralization`

---

### 4  Canonical Vocabulary (lookup table)

| Layer                   | Native terms Guardians already use         |
| ----------------------- | ------------------------------------------ |
| **L1 – Models / Enums** | models, enums, SQLAlchemy, Alembic         |
| **L2 – Schemas**        | schemas, Pydantic, request/response models |
| **L3 – Routers**        | routers, endpoints, transaction boundaries |
| **L4 – Services**       | services, schedulers, session management   |
| **L5 – Configuration**  | configuration, env vars, settings          |
| **L6 – UI Components**  | JS modules, UI components, DOM             |
| **L7 – Testing**        | fixtures, mocking, test isolation          |

**Violation keywords** (from audits): `duplication`, `hardcoded`, `missing_*`, `non‑compliant`, `Blueprint {n}`\
**Impact verbs**: `impacts`, `breaks`, `affects`, `complicates`

---

### 5  Lifecycle Checklist for Every Cross‑Layer Hand‑Off

1. **Detect** cross‑layer issue during audit/remediation.
2. **Draft** journal entry (template above).
3. **Create** DART task (matching title pattern).
4. **Link** task → journal and journal → task.
5. **Tag** journal with `Anti-Pattern` and list **Ripple Effects**.
6. **Mark** task as *To‑do* and continue work.

*Session start ritual for every Guardian* – first query their dartboard for tasks addressed **to them** (`L{self}_` prefix), then read linked journals before taking action.

---

### 6  Integration Notes

- Append this spec’s filename to each Guardian’s **Mandatory Reading** list during boot.
- In **common\_knowledge\_base.md**, add:\
  `• Guardians follow the “Layer Cross‑Talk Specification” for every cross‑layer discovery.`

No new tools. No new schemas. Just shared language and repeatable steps—fully native to our current ecosystem.

