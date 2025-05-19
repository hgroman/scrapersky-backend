## Mission

Ensure the ScraperSky data foundation follows rigorous SQLAlchemy ORM patterns; audit and refactor all model classes to enforce consistent naming, proper ENUM implementation, standardized status columns, and complete removal of tenant isolation; deliver a type-safe, relationship-rich model layer that powers all workflows (WF1-SingleSearch, WF2-StagingEditor, WF3-LocalBusinessCuration, WF4-DomainCuration, WF5-SitemapCuration, WF6-SitemapImport, WF7-PageCuration).

## Success Metrics

1. 100% of models follow naming convention: `{SourceTableTitleCase}`
2. 100% of ENUM classes follow naming convention: `{WorkflowNameTitleCase}CurationStatus`
3. 100% of status columns follow convention: `{workflow_name}_curation_status`
4. Zero remnants of tenant_id in any model file
5. All model relationships properly defined with backrefs
6. Zero raw SQL queries anywhere in the codebase

## Data Foundation Quality Vision

The refactored Layer 1 (Models) will exhibit:

1. **Consistent type safety** across all model classes:
   - String-based ENUMs with Title Case values
   - UUID primary keys with proper implementation
   - Explicit nullable constraints where appropriate
   - PostgreSQL ENUMs for all status fields

2. **Clear relationship patterns**:
   - Explicit relationship() declarations
   - Appropriate backref definitions
   - Proper cascade rules for dependencies
   - Foreign keys with correct references

3. **Standardized status implementation**:
   - Dual-status pattern in all workflow models
   - Proper default values and constraints
   - Status transitions controlled by services
   - Error status tracking and column definitions

4. **Modern SQLAlchemy patterns**:
   - Hybrid properties where appropriate
   - Index definitions for performance
   - Server defaults for critical fields
   - Type-compatible annotations

## Driving Principles for Layer 1

1. **Type safety over convenience** - Using ENUMs and strong typing patterns consistently, even when simpler string approaches might seem easier.

2. **Explicit relationships over implicit** - All model relationships must be explicitly defined, with no reliance on naming conventions or implicit joins.

3. **Documentation in code** - Model fields and relationships should have clear docstrings explaining their purpose and constraints.

4. **Migration-aware modeling** - All model changes must consider the migration path and backward compatibility.

5. **Domain integrity enforcement** - Constraints and validation should be at the model level where possible, not relegated to application code.

> **Reason for existence:** Establish the unshakable data foundation upon which all other architectural layers depend.
