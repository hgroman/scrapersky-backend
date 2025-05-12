# Work Order 49 – CI / Pre‑commit Hooks Cleanup & Realignment

> **Purpose :** eliminate current friction preventing reliable `git commit` / `git push`, by pruning or re‑scoping enforcement tooling (Ruff, custom Supavisor hook, YAML duplicate‑key checker, etc.) so that the **solo‑MVP workflow** is fast, deterministic, and produces *good‑enough* code without blocking progress.

---

## 1 — Background & Problem Statement

1. **Current blockers**

   * `pre‑commit` stack halts commits because of:

     * `ruff` **E501 line‑length** warnings & other style rules.
     * **Custom** `enforce‑supavisor‑params` hook (import usage).
     * `check‑yaml` duplicate‑key failures.
     * `trailing‑whitespace` auto‑fix that leaves unstaged changes.
   * AI helpers inside Windsurf keep generating code that re‑triggers these hooks.
2. **Impact** : zero successful commits without manual `--no‑verify`.  Velocity ↓, frustration ↑.
3. **MVP reality** : solo developer; need only minimal hygiene (syntax correct, basic format) until after launch.

---

## 2 — Goals (Definition of Done)

| # | Goal                                                                                       | Acceptance Test                                            |
| - | ------------------------------------------------------------------------------------------ | ---------------------------------------------------------- |
| 1 | Can `git commit && git push` cleanly on first try with no `--no‑verify`.                   | Local run shows zero failing hooks.                        |
| 2 | Essential hygiene only: Ruff **format + selected async rules**, whitespace fixer.          | `.pre-commit-config.yaml` reflects reduced scope.          |
| 3 | Legacy artefacts, caches & orphaned files removed.                                         | `git status` clean; no `.ruff_cache`, stray `ruff_*`, etc. |
| 4 | Work order documented in `Docs_5_Project_Working_Docs/49…` with success confirmation file. | `49.1-Success-Confirmation.md` present with logs.          |

---

## 3 — Out‑of‑Scope

* Full PEP‑8 compliance.
* Re‑engineering async patterns across entire codebase.
* Company‑scale CI/CD.

---

## 4 — Work Breakdown (Tasks for Local AI)

### 4.1 Inventory & Report

1. **List hooks** active in `.pre-commit-config.yaml` → `49.0-Hook-Audit.txt`.
2. **Run** `ruff check . --output-format=full`; save as `49.0-Ruff-Report.txt`.
3. **Run** `pre-commit run --all-files` (no autofix) & save output `49.0-PreCommit-Current.txt`.

### 4.2 Config Reduction

4. Edit `.pre-commit-config.yaml` so only:

   ```yaml
   repos:
     - repo: https://github.com/charliermarsh/ruff-pre-commit
       rev: v0.3.0
       hooks:
         - id: ruff
           args: ["--select", "ASYNC", "--fix", "--ignore", "E501"]
         - id: ruff-format
     - repo: https://github.com/pre-commit/pre-commit-hooks
       rev: v4.5.0
       hooks:
         - id: trailing-whitespace
         - id: end-of-file-fixer
   ```

   > *No Supavisor custom hook, no YAML duplicate checker for now.*
5. Commit the edited config (`git add .pre-commit-config.yaml`).

### 4.3 Autofix Minimum Violations

6. Run `ruff check . --select ASYNC --ignore E501 --fix`.
7. Stage resulting changes `git add -A`.

### 4.4 Workspace Cleanup

8. Remove caches & artefacts:

   ```bash
   rm -rf .mypy_cache .pytest_cache .ruff_cache
   find . -name "*~" -delete
   ```
9. Stage deletions `git add -A`.

### 4.5 Verification

10. Run `pre-commit run --all-files` → should pass.
11. Run `pytest -q` – must have 0 failures.
12. Bring containers up `docker-compose up -d` and curl health‑check:

    ```bash
    curl -s http://localhost:8000/healthz | grep 'ok'
    ```
13. Capture outputs into `49.1-Success-Confirmation.md`.

### 4.6 Commit & Push

14. Save commit message below to `/tmp/commit_msg_49.txt`.
15. Execute:

    ```bash
    git commit -F /tmp/commit_msg_49.txt
    git push origin main
    ```

---

## 5 — Multi‑line Commit Message

```
Feat: Work Order 49 – CI hooks cleanup & minimal Ruff enforcement

* Replaced aggressive pre‑commit stack with lean config (Ruff async + format, whitespace fixers)
* Removed legacy Supavisor import hook & YAML duplicate checker (will revisit post‑MVP)
* Auto‑fixed async‑only Ruff issues; suppressed E501 for velocity
* Purged cache/artefact dirs and stray temp files
* All tests pass; health‑check endpoint returns ok

Closes #49
```
