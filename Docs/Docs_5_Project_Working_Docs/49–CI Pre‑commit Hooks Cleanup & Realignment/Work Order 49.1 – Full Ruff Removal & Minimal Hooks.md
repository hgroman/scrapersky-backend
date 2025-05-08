# Work Order 49.1 – **Full Ruff & Legacy‑Hook Removal, Clean Pass, then Minimal Guard‑Rails**

**Owner:** Hank (solo dev / solarpreneur)

**Context (May 8 2025)**  Two hours burned fighting Ruff + Supavisor pre‑commit hooks. Current pipeline blocks velocity. Goal is *ship first* ➜ *harden later*.

---

## Phase 0   Safety checkpoint

1. **Make sure `main` is green in prod** (Render deployment or other). If current `main` is broken, hot‑patch *first* so we have a safe rollback point.
2. Create a throw‑away branch to execute this work order (recommended):

   ```bash
   git checkout -b chore/remove-ruff-wo49.1
   ```

---

## Phase 1   Rip Ruff & every legacy hook *completely*

| Step                                                                                                                                                                            | Command / Action                                        | Notes                                                                                             |                |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------- | ------------------------------------------------------------------------------------------------- | -------------- |
| 1                                                                                                                                                                               | `pip uninstall -y ruff`                                 | Global env & venv. Repeat in Dockerfile later.                                                    |                |
| 2                                                                                                                                                                               | Delete Ruff artefacts                                   | `rm -rf .ruff_cache` and any hidden caches.                                                       |                |
| 3                                                                                                                                                                               | Remove Ruff config                                      | If present: `pyproject.toml` → delete `[tool.ruff]` section.  Also delete standalone `ruff.toml`. |                |
| 4                                                                                                                                                                               | Nuke entire `.pre-commit-config.yaml`                   | `git rm .pre-commit-config.yaml`                                                                  |                |
| 5                                                                                                                                                                               | Delete any repo‑level git hooks installed by pre‑commit | `find .git/hooks -type f -not -name "*.sample" -delete`                                           |                |
| 6                                                                                                                                                                               | Strip Ruff/Supavisor steps from CI                      | Search `.github/workflows/**`; remove jobs or steps invoking Ruff or `pre-commit`.                |                |
| 7                                                                                                                                                                               | Clean cache directories                                 | \`find . -name "**pycache**" -o -name ".pytest\_cache" -o -name "\*.pyc"                          | xargs rm -rf\` |
| 8                                                                                                                                                                               | Commit → **should succeed with *no* hooks**             | \`\`\`bash                                                                                        |                |
| git add -A                                                                                                                                                                      |                                                         |                                                                                                   |                |
| printf 'Chore: remove Ruff & legacy pre‑commit hooks (WO 49.1)\n\nCompletely deleted Ruff tooling and all pre‑commit hooks to unblock rapid MVP work.\n' > /tmp/wo49.1\_msg.txt |                                                         |                                                                                                   |                |
| git commit -F /tmp/wo49.1\_msg.txt                                                                                                                                              |                                                         |                                                                                                   |                |

````|

✔ **Checkpoint 1:** A plain `git commit` works with zero complaints. If not, stop & fix before Phase 2.

---

## Phase 2   Add _ultra‑minimal_ guard‑rail (optional but recommended)

> Only to stop catastrophic whitespace diffs & keep newlines tidy.  No linting, no DB checks.

1. **Re‑init pre‑commit skeleton**
   ```bash
   cat > .pre-commit-config.yaml <<'YAML'
   repos:
     - repo: https://github.com/pre-commit/pre-commit-hooks
       rev: v4.5.0
       hooks:
         - id: end-of-file-fixer
         - id: trailing-whitespace
   YAML
````

2. Install locally:

   ```bash
   pre-commit install
   pre-commit run --all-files   # should auto-fix, no errors
   git add -A
   git commit -m "Chore: add minimal whitespace hooks (WO 49.1)"
   ```
3. **Do *not*** add Ruff, isort, Supavisor, etc., until explicitly scheduled (see Phase 3).

✔ **Checkpoint 2:** Commit passes with only whitespace hooks active.

---

## Phase 3   (Deferred) Editor‑side real‑time helpers

*Bring back automated formatting **only** inside the IDE, not as a gate.*  Track as **Work Order 50**.

* VS Code → enable `black` or `ruff format` on save (user‑level setting).
* Optionally re‑add Ruff in CI **only** to comment on PRs, not block.

---

## Validation & Closeout

1. `git push --set-upstream origin chore/remove-ruff-wo49.1`
2. Open PR – self‑review, merge squash.
3. Tag release `v0.7.0‑nocreep` once `main` deploys cleanly.
4. Update project README “CI / Tooling” section with new minimal policy.

**Done =** Hank can run `git commit` + `git push` in <15 seconds with no AI fights.

---

## Rollback Plan

`git revert <merge-sha>` restores previous tool‑chain if hidden side‑effects appear.

---

### Author / Timestamp

Generated by ChatGPT o3 • 2025‑05‑08 09:25 America/Los\_Angeles
