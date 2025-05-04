# ScraperSky Backend Project Documentation

This directory contains critical documentation for the ScraperSky Backend project. It is organized chronologically and by topic to provide a comprehensive view of the project's evolution, current status, and planned improvements.

## Key Documents

- [**NEXT_STEPS_2025-03-25.md**](/project-docs/07-database-connection-audit/NEXT_STEPS_2025-03-25.md) - **NEW** Comprehensive outline of current state and prioritized next actions for the project
- [**ARCHITECTURAL_PRINCIPLES.md**](/project-docs/07-database-connection-audit/ARCHITECTURAL_PRINCIPLES.md) - Core architectural principles guiding all development

## Directory Structure

### Chronological Assessment and Planning

1. [**01-initial-assessment/**](./01-initial-assessment/) - Initial codebase review and structure analysis
2. [**02-database-consolidation/**](./02-database-consolidation/) - Database access standardization efforts
3. [**03-auth-service/**](./03-auth-service/) - Authentication service consolidation
4. [**04-error-handling/**](./04-error-handling/) - Error handling standardization
5. [**05-api-standardization/**](./05-api-standardization/) - API endpoint standardization
6. [**06-tenant-isolation/**](./06-tenant-isolation/) - Tenant isolation removal and simplification
7. [**07-database-connection-audit/**](./07-database-connection-audit/) - Connection pooling and session management
8. [**07-cleanup/**](./07-cleanup/) - Post-implementation cleanup and consolidation
9. [**08-testing/**](./08-testing/) - Testing strategy and implementation
10. [**09-master-documents/**](./09-master-documents/) - High-level project status and reference materials

## Global Reference Documents

- [**00-project-timeline.md**](./00-project-timeline.md) - Key milestones and chronological development
- [**00-file-mapping.md**](./00-file-mapping.md) - Directory and file structure reference

## Current Project Focus

The project is currently focused on:

1. **Authentication Boundary Enforcement**: Ensuring JWT authentication happens ONLY at the API router level
2. **UUID Standardization**: Converting all job_id fields to proper UUID format
3. **Test Script Development**: Creating comprehensive test scripts for core services
4. **Documentation Improvement**: Maintaining up-to-date project documentation

See [**NEXT_STEPS_2025-03-25.md**](/project-docs/07-database-connection-audit/NEXT_STEPS_2025-03-25.md) for detailed information on the current focus and prioritized tasks.

## For New Developers

1. Start by reviewing the [**00-project-timeline.md**](./00-project-timeline.md) to understand project evolution
2. Review the [**ARCHITECTURAL_PRINCIPLES.md**](/project-docs/07-database-connection-audit/ARCHITECTURAL_PRINCIPLES.md) document
3. Check [**NEXT_STEPS_2025-03-25.md**](/project-docs/07-database-connection-audit/NEXT_STEPS_2025-03-25.md) for current priorities
4. See [AI_GUIDES](/AI_GUIDES/) directory for development guidance and patterns

## Contributing

When adding to this documentation:

1. Use the appropriate directory for the topic
2. Follow the established numbering scheme
3. Include the date in filenames (YYYY-MM-DD format)
4. Cross-reference related documents
5. Update this README.md when adding significant new documentation

## File Cleanup Plan

The project includes several documents related to cleaning up the codebase:

- [07-01-cleanup-plan-2025-03-24.md](./07-cleanup/07-01-cleanup-plan-2025-03-24.md): General cleanup strategies
- [07-02-continue-consolidation-2025-03-23.md](./07-cleanup/07-02-continue-consolidation-2025-03-23.md): Continuation of service consolidation
- [07-03-continue-after-compact-2025-03-23.md](./07-cleanup/07-03-continue-after-compact-2025-03-23.md): Post-compaction next steps
- [07-04-file-cleanup-plan-2025-03-24.md](./07-cleanup/07-04-file-cleanup-plan-2025-03-24.md): Detailed plan for removing backup files and duplicate services
- [07-05-dependency-matrix-2025-03-24.md](./07-cleanup/07-05-dependency-matrix-2025-03-24.md): Matrix showing which files are actively used and which can be safely removed

## Running the Cleanup Script

A cleanup script has been created to help implement the file cleanup plan. The script can be found at `/scripts/cleanup_files.py`.

Usage:

```bash
# Run in dry-run mode (shows what would be done without making changes)
python scripts/cleanup_files.py --dry-run

# Run the actual cleanup (moves files to archive directory)
python scripts/cleanup_files.py

# Specify a custom archive directory
python scripts/cleanup_files.py --archive-dir=/path/to/archive
```

The script will:

1. Remove backup files (.bak files)
2. Archive duplicate service implementations
3. Archive obsolete code files
4. Print a summary of the actions taken

## Key Architecture Documents

For understanding the overall architecture of the system, refer to these key documents:

- [02-ARCHITECTURE_QUICK_REFERENCE.md](../AI_GUIDES/02-ARCHITECTURE_QUICK_REFERENCE.md): High-level overview of the system architecture
- [05-IMMEDIATE_ACTION_PLAN.md](../AI_GUIDES/05-IMMEDIATE_ACTION_PLAN.md): Current priorities and action items
- [09-01-project-status-update-2025-03-23.md](./09-master-documents/09-01-project-status-update-2025-03-23.md): Latest project status update
