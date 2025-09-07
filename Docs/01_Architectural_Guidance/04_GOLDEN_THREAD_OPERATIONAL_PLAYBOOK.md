# Golden Thread Operational Playbook

## Mission

**Goal:** Verify before change, in Docker, via health/debug endpoints; codify patterns with explicit anti-patterns; enforce via personas and approval gates for zero-risk compliance and production safety.

**Audience:** All Layer Guardians + Human/AI pairs working on any workflow.

## Non-Negotiables (Constitutional Truth)

- **Naming**: Docs use hyphens; Python files use underscores (e.g., `WF7_V3_L2_1of1_*`).
- **Layer separation**: No inline schemas in routers (L2 extracted).
- **Transactions**: Routers own; services accept.
- **Versioning**: New endpoints use `/api/v3/`; keep V2 active (dual-existence).

## Docker-First Verification Protocol

- Start: `docker compose up --build`
- Health: `curl -f http://localhost:8000/health`
- Optional debug: set `FASTAPI_DEBUG_MODE=true`, then:
  - `/debug/routes` and `/debug/loaded-src-files`

## V2→V3 Migration Protocol

- L2: Extract schemas → `WF7_V3_L2_1of1_*Schemas.py` with `ConfigDict(from_attributes=True)`.
- L3: Create V3 router → `/api/v3/...` + auth dependency; import from L2.
- L5: Include both v2 and v3 routers in `main.py` (dual-existence).
- Verify imports via `python -c "from ... import ..."` before server run.

## Pattern vs Anti-Pattern Quick Reference

- Keep one “Companion” per layer with side‑by‑side examples.
- Example anchors for L2/L3:
  - ✅ Import schemas from dedicated file
  - ❌ Inline schemas in routers
  - ✅ `/api/v3/` prefix + auth
  - ❌ Version drift to `/api/v2/` for new endpoints
**See:** `03_ARCHITECTURAL_PATTERNS_LIBRARY.md` for complete patterns

## AI Partner Safety Protocol (Three Laws)

- Docker First: test in containers before local edits.
- Verification First: prove imports/deps exist before suggesting changes.
- Health First: validate via `/health` and debug endpoints.

## Human/AI Pairing Rhythm

1. Align on “why” (PRD/acceptance) + risks (enforcement gates).
2. Load the right Companion(s) + this checklist.
3. Verify current state in Docker (health, debug, routes).
4. Plan the smallest additive change (dual-existence where relevant).
5. Execute with checklists; verify imports; run health; record evidence.
6. Capture lessons; update Companion if a new pattern/antipattern emerges.

## Six-Tier Validation Protocol

- 1. Server startup 2) Model imports 3) DB connection
- 4. Record creation (schema match) 5) Service integration
- 6. End‑to‑end API→DB proof

## Rapid Commands Reference

- Health: `curl -f http://localhost:8000/health`
- Routes: `curl http://localhost:8000/debug/routes | jq .`
- V3 presence: `curl http://localhost:8000/openapi.json | jq '.paths | keys[]'`
- Import probe: `python -c "from src.schemas.WF7_V3_L2_1of1_PageCurationSchemas import PageCurationBatchStatusUpdateRequest"`

---

## Pre-Flight Checklist for Any Operation

### Before Starting Work
- [ ] Docker environment running
- [ ] Health check passing
- [ ] Correct branch checked out
- [ ] Dependencies up to date

### Before Code Changes
- [ ] Building blocks triggers scanned in `09_BUILDING_BLOCKS_MENU.yaml`
- [ ] Pattern verified in `03_ARCHITECTURAL_PATTERNS_LIBRARY.md`
- [ ] No STOP conditions triggered (check `01_STOP_SIGNS_CRITICAL_OPERATIONS.md`)
- [ ] Layer Guardian consulted if needed
- [ ] Naming convention followed

### Before Committing
- [ ] Import chains verified
- [ ] Docker test successful
- [ ] Six-tier validation complete
- [ ] No anti-patterns introduced

### Before Deployment
- [ ] V2/V3 dual existence maintained
- [ ] All tests passing
- [ ] Documentation updated
- [ ] Rollback plan defined

---

**Authority:** Derived from WF7 crisis recovery experience
**Application:** Universal for all workflows
**Updates:** Living document - update with new operational wisdom


