# ScraperSky Service Inventory Matrix

This document provides a comprehensive inventory of all services in the ScraperSky backend, their current implementation status, and modernization priorities.

## Service Classification

Services are classified based on their implementation status:

| Status                | Description                                                  |
| --------------------- | ------------------------------------------------------------ |
| ✅ Full SQLAlchemy    | Service fully implements SQLAlchemy ORM patterns             |
| 🟨 Partial SQLAlchemy | Service uses both SQLAlchemy and legacy patterns             |
| ❌ Legacy             | Service uses only legacy patterns (raw SQL, in-memory state) |
| 🔄 In Transition      | Service is currently being modernized                        |

## Core Services

| Service Name         | Location                                  | Status    | Dependencies  | Purpose                                     |
| -------------------- | ----------------------------------------- | --------- | ------------- | ------------------------------------------- |
| auth_service         | services/core/auth_service.py             | ❌ Legacy | db_service    | Authentication and authorization management |
| user_context_service | services/core/user_context_service.py     | ❌ Legacy | auth_service  | User context and permissions management     |
| db_service           | services/db_service.py                    | ❌ Legacy | None          | Database connection and query execution     |
| error_service        | services/error/error_service.py           | ❌ Legacy | None          | Error handling and standardization          |
| validation_service   | services/validation/validation_service.py | ❌ Legacy | error_service | Input validation and standardization        |

## Domain Services

| Service Name    | Location                            | Status                | Dependencies | Purpose                          |
| --------------- | ----------------------------------- | --------------------- | ------------ | -------------------------------- |
| domain_service  | services/domain_service.py          | ✅ Full SQLAlchemy    | None         | Domain management and operations |
| job_service     | services/job_service.py             | 🟨 Partial SQLAlchemy | None         | Job tracking and management      |
| storage_service | services/storage/storage_service.py | ❌ Legacy             | db_service   | File storage and retrieval       |
| sitemap_service | services/sitemap/sitemap_service.py | ❌ Legacy             | db_service   | Sitemap parsing and processing   |

## Process Services

| Service Name            | Location                                   | Status                | Dependencies                | Purpose                          |
| ----------------------- | ------------------------------------------ | --------------------- | --------------------------- | -------------------------------- |
| batch_processor_service | services/batch/batch_processor_service.py  | 🟨 Partial SQLAlchemy | job_service, domain_service | Batch processing of domains      |
| scrape_executor_service | services/scrape/scrape_executor_service.py | ❌ Legacy             | job_service                 | Execution of scraping operations |
| analytics_service       | services/analytics/analytics_service.py    | ❌ Legacy             | db_service                  | Analytics data processing        |
| export_service          | services/export/export_service.py          | ❌ Legacy             | db_service                  | Data export operations           |
| report_service          | services/report/report_service.py          | ❌ Legacy             | db_service                  | Report generation                |

## API Services

| Service Name         | Location                                      | Status    | Dependencies | Purpose                   |
| -------------------- | --------------------------------------------- | --------- | ------------ | ------------------------- |
| api_service          | services/api/api_service.py                   | ❌ Legacy | auth_service | External API integrations |
| webhook_service      | services/api/webhook_service.py               | ❌ Legacy | db_service   | Webhook management        |
| notification_service | services/notification/notification_service.py | ❌ Legacy | db_service   | User notifications        |

## Service Usage Matrix

The following matrix shows which services are used by key routers and other components:

| Service \ Component     | sitemap_scraper.py | domain_manager.py | batch_processor.py | analytics.py | export.py   |
| ----------------------- | ------------------ | ----------------- | ------------------ | ------------ | ----------- |
| auth_service            | ✅ Used            | ✅ Used           | ✅ Used            | ✅ Used      | ✅ Used     |
| user_context_service    | ✅ Used            | ✅ Used           | ✅ Used            | ✅ Used      | ✅ Used     |
| db_service              | ✅ Used            | ✅ Used           | ✅ Used            | ✅ Used      | ✅ Used     |
| error_service           | ✅ Used            | ✅ Used           | ✅ Used            | ✅ Used      | ✅ Used     |
| validation_service      | ✅ Used            | ✅ Used           | ✅ Used            | ❌ Not Used  | ✅ Used     |
| domain_service          | ✅ Used            | ✅ Used           | ✅ Used            | ✅ Used      | ✅ Used     |
| job_service             | ✅ Used            | ✅ Used           | ✅ Used            | ❌ Not Used  | ❌ Not Used |
| storage_service         | ❌ Not Used        | ❌ Not Used       | ❌ Not Used        | ❌ Not Used  | ✅ Used     |
| sitemap_service         | ✅ Used            | ❌ Not Used       | ✅ Used            | ❌ Not Used  | ❌ Not Used |
| batch_processor_service | ✅ Used            | ✅ Used           | ✅ Used            | ❌ Not Used  | ❌ Not Used |
| scrape_executor_service | ✅ Used            | ❌ Not Used       | ✅ Used            | ❌ Not Used  | ❌ Not Used |
| analytics_service       | ❌ Not Used        | ❌ Not Used       | ❌ Not Used        | ✅ Used      | ✅ Used     |
| export_service          | ❌ Not Used        | ❌ Not Used       | ❌ Not Used        | ❌ Not Used  | ✅ Used     |
| report_service          | ❌ Not Used        | ❌ Not Used       | ❌ Not Used        | ✅ Used      | ✅ Used     |
| api_service             | ❌ Not Used        | ✅ Used           | ❌ Not Used        | ✅ Used      | ❌ Not Used |
| webhook_service         | ❌ Not Used        | ✅ Used           | ❌ Not Used        | ❌ Not Used  | ❌ Not Used |
| notification_service    | ❌ Not Used        | ✅ Used           | ✅ Used            | ❌ Not Used  | ✅ Used     |

## Modernization Priorities

Based on usage patterns and dependencies, we recommend the following modernization priorities:

### Highest Priority (Phase 1)

1. **job_service** - Currently in partial SQLAlchemy state, heavily used across the application
2. **batch_processor_service** - Partial SQLAlchemy implementation, critical for batch operations
3. **db_service** - Legacy service with many dependents, core to all database operations

### Medium Priority (Phase 2)

4. **auth_service** - Used by all components, but complex to modernize
5. **user_context_service** - Depends on auth_service, should be modernized together
6. **error_service** - Used throughout codebase
7. **validation_service** - Used throughout codebase

### Lower Priority (Phase 3)

8. Remaining domain-specific services
9. Process services
10. API integration services

## Implementation Recommendations

### Phase 1 Strategy

1. **job_service**:

   - Remove in-memory job tracking
   - Standardize SQLAlchemy job operations
   - Add comprehensive job relationship loading

2. **batch_processor_service**:

   - Complete SQLAlchemy implementation
   - Remove direct database operations
   - Standardize error handling

3. **db_service**:
   - Create transition plan to phase out usage
   - Add deprecation warnings
   - Begin replacing in highest-usage files

### Phase 2 Strategy

1. **auth_service**:

   - Design SQLAlchemy models for permissions
   - Implement caching strategy
   - Test thoroughly with existing consumers

2. **user_context_service**:

   - Move to SQLAlchemy models
   - Integrate with auth_service changes

3. **error_service** and **validation_service**:
   - Standardize interfaces
   - Add SQLAlchemy integration for error tracking

### Phase 3 Strategy

1. Complete modernization of remaining services
2. Remove all direct database operations
3. Standardize service interfaces
4. Comprehensive testing

## Migration Risks

1. **job_service** - In-memory tracking still used by some parts of the application
2. **db_service** - Heavy dependencies throughout codebase
3. **auth_service** - Complex permissions logic with caching

## Conclusion

The service inventory shows a mix of modern SQLAlchemy implementations and legacy patterns. Prioritizing the modernization of core services like job_service, batch_processor_service, and db_service will provide the greatest impact while minimizing risk. The migration should be performed in phases with comprehensive testing between each phase.
