# Service Organization Standard

## Current State Analysis

Our codebase currently has an inconsistent organization of services:

1. **Root-level Services**:

   - `src/services/metadata_service.py`
   - `src/services/domain_service.py`
   - `src/services/job_service.py`
   - `src/services/sitemap_service.py`
   - `src/services/db_service.py`

2. **Domain-specific Subdirectories**:
   - `src/services/core/auth_service.py`
   - `src/services/core/validation_service.py`
   - `src/services/core/error_service.py`
   - `src/services/batch/batch_processor_service.py`
   - `src/services/scraping/scrape_executor_service.py`

This inconsistency makes it difficult to locate services, creates confusion about where new services should be placed, and hinders codebase navigation.

## Standard Going Forward (FINAL DECISION)

**All services MUST be organized in domain-specific subdirectories.**

### Directory Structure

The service directory structure should follow this pattern:

```
src/services/
├── core/                 # Core system services used across the application
│   ├── auth_service.py   # Authentication and authorization
│   ├── validation_service.py  # Input validation
│   ├── error_service.py  # Error handling
│   └── tenant_service.py # Tenant management
├── sitemap/              # Sitemap-related services
│   ├── extraction_service.py  # Metadata extraction
│   └── processing_service.py  # Sitemap processing
├── data/                 # Data handling services
│   ├── storage_service.py  # Data storage
│   └── query_service.py  # Data querying
├── batch/                # Batch processing services
│   └── batch_processor_service.py  # Batch job handling
└── integration/          # External integrations
    └── email_service.py  # Email handling
```

### Implementation Guidelines

1. **New Services**:

   - All new services MUST be created in an appropriate subdirectory.
   - If no appropriate subdirectory exists, create a new one.

2. **Legacy Services**:

   - When making significant modifications to legacy root-level services, gradually migrate them to the appropriate subdirectory.
   - Do not modify working root-level services solely for organizational purposes until scheduled.

3. **Naming Conventions**:

   - All service files should be named with the `_service.py` suffix.
   - Service classes should be named with the `Service` suffix.
   - Singleton instances should be lowercase, e.g., `validation_service`.

4. **Imports**:

   - Services should be imported directly from their module:
     ```python
     from ..services.core.validation_service import validation_service
     ```
   - Avoid importing the parent directory and then accessing the service.

5. **Factories and Non-Services**:
   - Keep factories separate in their own directory: `src/factories/`
   - Models should remain in `src/models/`

## Migration Plan

While we won't refactor everything immediately, follow this guideline for incremental migration:

1. When working on a root-level service file that requires significant changes, move it to the appropriate subdirectory.
2. Update imports in dependent files.
3. Add proper tests for the relocated service.
4. Document the change in the migration tracker.

## Trade-offs and Rationale

This organization provides several benefits:

1. **Discoverability**: Developers can easily locate services by their domain.
2. **Scalability**: As the application grows, new services can be added to the appropriate domain without cluttering the root directory.
3. **Cohesion**: Services with similar concerns are grouped together.
4. **Maintenance**: Easier to maintain and understand the codebase structure.

The primary disadvantage - migration effort - will be mitigated by our incremental approach.

## Examples

### Before (Legacy):

```python
from ..services.metadata_service import metadata_service
```

### After (Standard):

```python
from ..services.sitemap.metadata_service import metadata_service
```

## Migration Tracker

| Date       | Service            | From          | To                                         | PR/Commit                     |
| ---------- | ------------------ | ------------- | ------------------------------------------ | ----------------------------- |
| 2024-07-28 | sitemap_service.py | src/services/ | src/services/sitemap/processing_service.py | Router Factory Implementation |

## Conclusion

This standard represents our FINAL DECISION on service organization. All future development should follow these guidelines without exception to ensure consistency and maintainability of the codebase.
