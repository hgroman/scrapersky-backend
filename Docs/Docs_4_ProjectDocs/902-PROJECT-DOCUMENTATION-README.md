# ScraperSky Backend Project Documentation

This directory contains critical documentation for the ScraperSky Backend project. It is organized chronologically and by topic to provide a comprehensive view of the project's evolution, current status, and planned improvements.

## Key Documents

- [**950-NEXT-STEPS-2025-03-25.md**](./950-NEXT-STEPS-2025-03-25.md) - **NEW** Comprehensive outline of current state and prioritized next actions for the project
- [**951-ARCHITECTURAL-PRINCIPLES.md**](./951-ARCHITECTURAL-PRINCIPLES.md) - Core architectural principles guiding all development

## Directory Structure

### Chronological Assessment and Planning

1. [**910-INITIAL-ASSESSMENT-PHASE**](./910-INITIAL-ASSESSMENT-PHASE.md) - Initial codebase review and structure analysis
2. [**915-DATABASE-CONSOLIDATION-PHASE**](./915-DATABASE-CONSOLIDATION-PHASE.md) - Database access standardization efforts
3. [**920-AUTH-SERVICE-PHASE**](./920-AUTH-SERVICE-PHASE.md) - Authentication service consolidation
4. [**925-ERROR-HANDLING-PHASE**](./925-ERROR-HANDLING-PHASE.md) - Error handling standardization
5. [**930-API-STANDARDIZATION-PHASE**](./930-API-STANDARDIZATION-PHASE.md) - API endpoint standardization
6. [**935-TENANT-ISOLATION-PHASE**](./935-TENANT-ISOLATION-PHASE.md) - Tenant isolation removal and simplification
7. [**940-DATABASE-CONNECTION-AUDIT-PHASE**](./940-DATABASE-CONNECTION-AUDIT-PHASE.md) - Connection pooling and session management
8. [**945-CLEANUP-PHASE**](./945-CLEANUP-PHASE.md) - Post-implementation cleanup and consolidation
9. [**955-TESTING-PHASE**](./955-TESTING-PHASE.md) - Testing strategy and implementation
10. [**960-MASTER-DOCUMENTS**](./960-MASTER-DOCUMENTS.md) - High-level project status and reference materials

## Global Reference Documents

- [**901-PROJECT-TIMELINE.md**](./901-PROJECT-TIMELINE.md) - Key milestones and chronological development
- [**900-FILE-MAPPING.md**](./900-FILE-MAPPING.md) - Directory and file structure reference

## Current Project Focus

The project is currently focused on:

1. **Authentication Boundary Enforcement**: Ensuring JWT authentication happens ONLY at the API router level
2. **UUID Standardization**: Converting all job_id fields to proper UUID format
3. **Test Script Development**: Creating comprehensive test scripts for core services
4. **Documentation Improvement**: Maintaining up-to-date project documentation

See [**950-NEXT-STEPS-2025-03-25.md**](./950-NEXT-STEPS-2025-03-25.md) for detailed information on the current focus and prioritized tasks.

## For New Developers

1. Start by reviewing the [**901-PROJECT-TIMELINE.md**](./901-PROJECT-TIMELINE.md) to understand project evolution
2. Review the [**951-ARCHITECTURAL-PRINCIPLES.md**](./951-ARCHITECTURAL-PRINCIPLES.md) document
3. Check [**950-NEXT-STEPS-2025-03-25.md**](./950-NEXT-STEPS-2025-03-25.md) for current priorities
4. See [AI_GUIDES](../Docs_1_AI_GUIDES/) directory for development guidance and patterns

## Contributing

When adding to this documentation:

1. Use the appropriate directory for the topic
2. Follow the established numbering scheme
3. Include the date in filenames (YYYY-MM-DD format)
4. Cross-reference related documents
5. Update this README.md when adding significant new documentation

## File Cleanup Plan

The project includes several documents related to cleaning up the codebase:

- [945-CLEANUP-PLAN-2025-03-24.md](./945-CLEANUP-PLAN-2025-03-24.md): General cleanup strategies
- [946-CONTINUE-CONSOLIDATION-2025-03-23.md](./946-CONTINUE-CONSOLIDATION-2025-03-23.md): Continuation of service consolidation
- [947-CONTINUE-AFTER-COMPACT-2025-03-23.md](./947-CONTINUE-AFTER-COMPACT-2025-03-23.md): Post-compaction next steps
- [948-FILE-CLEANUP-PLAN-2025-03-24.md](./948-FILE-CLEANUP-PLAN-2025-03-24.md): Detailed plan for removing backup files and duplicate services
- [949-DEPENDENCY-MATRIX-2025-03-24.md](./949-DEPENDENCY-MATRIX-2025-03-24.md): Matrix showing which files are actively used and which can be safely removed

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

- [02-ARCHITECTURE_QUICK_REFERENCE.md](../Docs_1_AI_GUIDES/02-ARCHITECTURE_QUICK_REFERENCE.md): High-level overview of the system architecture
- [05-IMMEDIATE_ACTION_PLAN.md](../Docs_1_AI_GUIDES/05-IMMEDIATE_ACTION_PLAN.md): Current priorities and action items
- [960-PROJECT-STATUS-UPDATE-2025-03-23.md](./960-PROJECT-STATUS-UPDATE-2025-03-23.md): Latest project status update

#### Key AI Guide Documents

1. See [00-INDEX.md](../Docs_1_AI_GUIDES/00-INDEX.md) for Master Index of AI Guides
2. See [02-ARCHITECTURE_QUICK_REFERENCE.md](../Docs_1_AI_GUIDES/02-ARCHITECTURE_QUICK_REFERENCE.md) for architecture details.
3. See [17-CORE_ARCHITECTURAL_PRINCIPLES.md](../Docs_1_AI_GUIDES/17-CORE_ARCHITECTURAL_PRINCIPLES.md) for detailed core principles.
4. See [AI_GUIDES](../Docs_1_AI_GUIDES/) directory for development guidance and patterns

#### Key Workflow Documents
