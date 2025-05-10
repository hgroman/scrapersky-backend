# Workflows: Source of Truth

This directory contains the canonical, code-verified YAML representations of all major workflows in the ScraperSky backend. Each file is the authoritative, step-by-step trace of a workflow from UI to API to database, including explicit Layer 1: Models & ENUMs dependencies.

## Naming Convention

- All files are named `WF-<WorkflowName>_CANONICAL.yaml`.
- Each YAML includes:
  - `depends_on_models:` (list of SQLAlchemy Layer 1: Models & ENUMs used)
  - `depends_on_enums:` (list of Layer 1: Models & ENUMs used)
  - `architecture_reference:` (relevant architectural doc)

## How to Use

- Treat these as the source of truth for onboarding, debugging, and audits.
- Update these YAMLs whenever workflows or dependencies change.
- Cross-reference with `/Docs/Docs_0_Architecture_and_Status` for deeper context.

## Current Canonical Workflows

- WF1-SingleSearch_CANONICAL.yaml
- WF2-StagingEditor_CANONICAL.yaml
- WF3-LocalBusinessCuration_CANONICAL.yaml
- WF4-DomainCuration_CANONICAL.yaml
- WF5-SitemapCuration_CANONICAL.yaml
- WF6-SitemapImport_CANONICAL.yaml

---

For questions or improvements, see the architecture doc or contact the maintainers.
