# Work Order 50 – Repository Convergence & Progressive Guard‑Rails

> *“A clean main branch is the launch pad; disciplined guard‑rails are the autopilot.”*

## 0  Context & Purpose

For months our code‑base has been caught in a tug‑of‑war between ambitious AI‑driven ‘improvements’ (Ruff, Supavisor enforcement, etc.) and the very real need for uninterrupted shipping velocity.  Work Order 49.1 surgically **removed every legacy lint hook** and reinstated only whitespace janitors, giving us a **green‑field main branch**.

Work Order 50 captures the next evolutionary step:

1. **Merge the Ruff‑removal branch safely** so our baseline is unified.
2. Lay out a **graduated guard‑rail roadmap** that *prevents* future technical debt **without ever blocking a commit again.**
3. Establish the philosophy, cadence, and ownership model for incremental quality gates.

> **Audience** – Solo maintainer (you) and any AI pairing agents granted commit rights.

---

## 1  Phase A – One‑Time Convergence (Immediate)

| 🔢 | Task                      | Detail & Acceptance Criteria                                                                                        |
| -- | ------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| A1 | **Create PR**             | PR from `chore/remove-ruff-wo49.1` → `main`.  Title: `chore: remove Ruff & add minimal whitespace hooks (WO‑49.1)`  |
| A2 | **Attach Checklist**      | Copy Section 1 table into PR body.                                                                                  |
| A3 | **CI passes**             | Only `end‑of‑file` and `trailing‑whitespace` hooks run, zero failures.                                              |
| A4 | **Review diff**           | Confirms: ① deletion of Ruff artefacts & hooks  ② minimal `.pre-commit-config.yaml`  ③ whitespace‑only doc touches. |
| A5 | **Squash & Merge**        | Use “Squash & Merge”, commit message identical to PR title.                                                         |
| A6 | **Local sync & clean‑up** | `git pull`; delete remote & local feature branch; tag `v0.7.0-nocreep`.                                             |

✅ **Exit Gate:** `main` branch builds & runs locally in ≤ 15 s; `git commit` on trivial change succeeds in one shot.

---

## 2  Phase B – Progressive Guard‑Rail Roadmap (Deferred, opt‑in)

The roadmap introduces quality layers **only when they pay for themselves**.  Each layer is:

* *Opt‑in* (branch‑gated);
* *Fast* (≤ 2 s hook runtime);
* *Reversible* (single commit reverts).

| Tier | Guard‑Rail                   | Tooling                                                      | Trigger                           | Definition of Done                                                                  |
| ---- | ---------------------------- | ------------------------------------------------------------ | --------------------------------- | ----------------------------------------------------------------------------------- |
| 0    | **Whitespace only**          | `end‑of‑file‑fixer`, `trailing‑whitespace`                   | **NOW**                           | Already live after WO‑49.1                                                          |
| 1    | **On‑save auto‑format**      | EditorConfig + VS Code “Format on Save” (`black --fast`)     | When two days pass without revert | Saving any `.py` rewrites file to Black style instantly; commit hooks remain NO‑OP. |
| 2    | **Unit test smoke‑suite**    | `pytest -q tests/smoke/` (\~20 s) in **GitHub Actions only** | After MVP alpha                   | PR must pass smoke suite; local commits never blocked.                              |
| 3    | **Static type surface scan** | `pyright --level error` on `src/` (no generics enforcement)  | When >30 PRs merged post‑Tier 2   | Pyright finds 0 errors in CI; warnings allowed.                                     |
| 4    | **Selective lint budget**    | `ruff check src/routers/` ignoring length rules              | Add when router churn slows       | CI budget ≤ 10 lint errors; failing PR must delete more errors than it adds.        |
| 5    | **Security & secrets scan**  | `gitleaks` in CI                                             | Before public beta                | CI blocks secrets; local commits unaffected.                                        |

**Escalation rule:** each tier activates via a *Work Order* and branch, never retroactively on `main`.

---

## 3  Governance & Rituals

* **Weekly “Quality Pulse”** – 5‑minute review of open issues, lint budget, CI timing.
* **AI Guard‑Rail Compliance** – The `.ai_prompt_guide.md` **must** be updated whenever a new tier is adopted so that AI code generation stays in sync.
* **Rollback Safety** – Any guard‑rail may be disabled via `git revert` of its enabling commit; include this note in the commit body.

---

## 4  Why This Matters  (⛰️ Pontification)

The last sprint proved that ungoverned AI enthusiasm snowballs into a Kafka‑esque commit hell.  By wiping the slate and *re‑earning* each safeguard, we:

1. **Re‑assert human agency** – The maintainer, not a tool, decides the friction budget.
2. **Create psychological safety** – No change will ever be trapped behind a 300‑line lint rant again.
3. **Keep optionality** – Each tier is modular; future you can dial quality up or down depending on runway, customers, or caffeine.

*In the dawn of this new age, the worth of a tool is measured not by the warnings it can shout, but by the flow state it lets you keep.*

---

## 5  Sign‑Off

| Role       | Name          | Date       |
| ---------- | ------------- | ---------- |
| Maintainer | **Hank Groman** | 2025‑05‑08 |
