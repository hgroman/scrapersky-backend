# Workflows: Source of Truth

This directory contains the canonical, code-verified YAML representations of all major workflows in the ScraperSky backend. Each file is the authoritative, step-by-step trace of a workflow from UI to API to database, including explicit model and enum dependencies.

## Naming Convention
- All files are named `WF-<WorkflowName>_CANONICAL.yaml`.
- Each YAML includes:
  - `depends_on_models:` (list of SQLAlchemy models used)
  - `depends_on_enums:` (list of enums used)
  - `architecture_reference:` (relevant architectural doc)

## How to Use
- Treat these as the source of truth for onboarding, debugging, and audits.
- Update these YAMLs whenever workflows or dependencies change.
- Cross-reference with `/Docs/Docs_0_Architecture_and_Status` for deeper context.

## Current Canonical Workflows

- WF-SingleSearch_CANONICAL.yaml
- WF-StagingEditor_CANONICAL.yaml
- WF-LocalBusiness_CANONICAL.yaml
- WF-DomainCuration_CANONICAL.yaml
- WF-SitemapCuration_CANONICAL.yaml
- WF-Sitemap-Import_CANONICAL.yaml

---

For questions or improvements, see the architecture doc or contact the maintainers.
