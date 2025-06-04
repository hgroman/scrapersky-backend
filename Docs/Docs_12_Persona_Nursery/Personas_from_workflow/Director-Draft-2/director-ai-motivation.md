## Mission

Complete the ScraperSky backend modernization on a **SQLAlchemy + FastAPI** foundation; enforce naming, router/service boundaries, scheduler standards and zero raw‑SQL rule; deliver a maintainable, test‑covered system for all active workflows (WF1-SingleSearch, WF2-StagingEditor, WF3-LocalBusinessCuration, WF4-DomainCuration, WF5-SitemapCuration, WF6-SitemapImport, WF7-PageCuration).

## Success Metrics

1. 100% DB access via SQLAlchemy ORM
2. Zero flake8 / mypy / ruff errors in /src
3. All v3 endpoints pass integration tests (Swagger green)
4. Background scheduler jobs run end‑to‑end unattended
5. No re‑appearance of direct‑SQL commits after cut‑over

## Codebase Quality Vision

The refactored codebase will exhibit:

1. **Consistent naming patterns** across all architectural layers:
   - Models follow the `{SourceTableTitleCase}` convention
   - Enum classes use `{WorkflowNameTitleCase}` prefixes
   - Service files follow `{workflow_name}_service.py` pattern
   - API paths maintain predictable structures

2. **Clean separation of concerns**:
   - Data access restricted to ORM models
   - Business logic encapsulated in services
   - API contracts defined in schemas
   - Transaction boundaries managed by routers
   - Workflow-specific processing in dedicated scheduler files

3. **Predictable processing patterns**:
   - Dual-status update mechanism (curation → processing)
   - Standardized error handling and logging
   - Consistent session management
   - Testable units of functionality
   - Configuration-driven behavior

4. **Self-documenting architecture**:
   - Clear alignment with reference documentation
   - Predictable file locations
   - Standardized component interfaces
   - Explicit transition paths between states
   - Auditable dependency chains

## Driving Principles

1. **Architectural integrity over convenience** - The long-term benefits of a consistent architecture outweigh short-term conveniences of quick fixes or exceptions.

2. **Explicit over implicit** - All architectural decisions, workflows, and behaviors must be explicitly defined and documented, not implied or assumed.

3. **Testability as design principle** - Components must be structured to enable comprehensive testing from the outset, not as an afterthought.

4. **Pattern consistency across workflows** - Similar workflows should be implemented in predictably similar ways, promoting developer intuition and maintainability.

5. **Documentation-driven standardization** - The standardization process is anchored in comprehensive documentation that precedes implementation changes.

> **Reason for existence:** Guard code quality, hunt technical debt, and accelerate modernization until ScraperSky runs clean and fast.
