## Mission

Complete the ScraperSky backend modernization on a **SQLAlchemy + FastAPI** foundation; enforce naming, router/service boundaries, scheduler standards and zero raw‑SQL rule; deliver a maintainable, test‑covered system for all active workflows (WF1-SingleSearch, WF2-StagingEditor, WF3-LocalBusinessCuration, WF4-DomainCuration, WF5-SitemapCuration, WF6-SitemapImport, WF7-PageCuration).

## Success Metrics

1. 100 % DB access via SQLAlchemy ORM
2. Zero flake8 / mypy / ruff errors in /src
3. All v3 endpoints pass integration tests (Swagger green)
4. Background scheduler jobs run end‑to‑end unattended
5. No re‑appearance of direct‑SQL commits after cut‑over

> **Reason for existence:** Guard code quality, hunt technical debt, and accelerate modernization until ScraperSky runs clean and fast.
