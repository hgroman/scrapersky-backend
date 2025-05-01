# SQLAlchemy Migration Cleanup Tracker

This document tracks code, files, and patterns that can be removed or simplified as we migrate to SQLAlchemy. We'll update this document as we progress through the migration to ensure we're continuously improving code quality and reducing technical debt.

## 1. Files to Remove

Once migration is complete, we can remove these files:

| File Path                       | Current Purpose                  | Replacement                         | Status           |
| ------------------------------- | -------------------------------- | ----------------------------------- | ---------------- |
| `src/db/sb_connection.py`       | Main psycopg2 connection handler | SQLAlchemy engine and session       | Pending          |
| `src/db/sb_connection copy.py`  | Backup/older connection handler  | SQLAlchemy engine and session       | Pending          |
| `src/db/async_sb_connection.py` | Async connection handler         | SQLAlchemy async engine and session | Pending          |
| Custom SQL query files          | Raw SQL queries                  | SQLAlchemy ORM queries              | To be identified |

## 2. Code Patterns to Clean Up

These code patterns should be systematically replaced:

### 2.1. Raw SQL Queries

| Pattern                                       | Replacement                                        | Notes                                     | Status  |
| --------------------------------------------- | -------------------------------------------------- | ----------------------------------------- | ------- |
| `db_service.fetch_all(query, params)`         | `session.execute(select(Model))`                   | Replace with type-safe SQLAlchemy queries | Pending |
| `db_service.fetch_one(query, params)`         | `session.execute(select(Model).limit(1))`          | Replace with type-safe SQLAlchemy queries | Pending |
| `db_service.execute_returning(query, params)` | `session.add(model)` with `session.refresh(model)` | Use ORM objects instead of raw queries    | Pending |
| String concatenation in SQL                   | SQLAlchemy expressions                             | Eliminates SQL injection risks            | Pending |
| Manual transaction management                 | SQLAlchemy transaction context                     | `async with session.begin()`              | Pending |

### 2.2. Service Simplifications

| Current Pattern               | Replacement           | Benefits                        | Status      |
| ----------------------------- | --------------------- | ------------------------------- | ----------- |
| Custom job status tracking    | SQLAlchemy models     | Persistent storage, type safety | Completed   |
| In-memory state management    | Database-backed state | Reliability, consistency        | In Progress |
| Manual error classification   | SQLAlchemy exceptions | Better error handling           | Pending     |
| String-based tenant filtering | Model-based filtering | Type safety, performance        | Completed   |
| Custom pagination logic       | SQLAlchemy pagination | Standardization, performance    | Pending     |

## 3. Architecture Improvements

These architectural elements can be improved:

| Current Approach                    | Target Architecture          | Benefits                       | Status      |
| ----------------------------------- | ---------------------------- | ------------------------------ | ----------- |
| Service-based with raw SQL          | Model-driven with SQLAlchemy | Simpler, more maintainable     | In Progress |
| Inconsistent transaction boundaries | Explicit transaction scopes  | Data integrity                 | Pending     |
| Manual relationship handling        | SQLAlchemy relationships     | Automatic joins, eager loading | Completed   |
| String-based query building         | Type-safe query building     | Compile-time checking          | In Progress |
| Custom connection pooling           | SQLAlchemy connection pool   | Better reliability             | Completed   |

## 4. Migration Progress Tracking

### 4.1. Services Migration

| Service                 | Status      | Notes                                           |
| ----------------------- | ----------- | ----------------------------------------------- |
| db_service              | In Progress | Partial replacement with SQLAlchemy session     |
| job_service             | Completed   | Replaced with SQLAlchemy models and service     |
| batch_processor_service | In Progress | Partial replacement with BatchJob functionality |
| error_service           | Pending     | Update for SQLAlchemy exceptions                |
| validation_service      | Pending     | Integrate with SQLAlchemy validators            |
| auth_service            | Pending     | Update for SQLAlchemy models                    |
| user_context_service    | Pending     | Integrate with SQLAlchemy                       |

### 4.2. Endpoint Migration

| Endpoint                          | Status           | Notes                     |
| --------------------------------- | ---------------- | ------------------------- |
| `/api/v1/scrapersky`              | Pending          | Sitemap scanner endpoint  |
| `/api/v1/batch`                   | Pending          | Batch processing endpoint |
| `/api/v1/status/{job_id}`         | Pending          | Job status endpoint       |
| `/api/v1/batch/status/{batch_id}` | Pending          | Batch status endpoint     |
| Other endpoints                   | To be identified |                           |

## 5. Documentation Updates Needed

| Document              | Update Required                       | Status  |
| --------------------- | ------------------------------------- | ------- |
| API Documentation     | Update for SQLAlchemy patterns        | Pending |
| Developer Guidelines  | Add SQLAlchemy best practices         | Pending |
| Service Documentation | Replace with SQLAlchemy documentation | Pending |
| Testing Guidelines    | Update for SQLAlchemy testing         | Pending |

## 6. Performance Opportunities

| Current Issue                  | SQLAlchemy Improvement         | Expected Benefit             | Status    |
| ------------------------------ | ------------------------------ | ---------------------------- | --------- |
| N+1 Query Problems             | Eager loading with joinedload  | Reduced database round trips | Pending   |
| Inefficient queries            | SQLAlchemy optimized queries   | Better performance           | Pending   |
| Connection management overhead | SQLAlchemy connection pool     | Reduced overhead             | Completed |
| Missing indices                | SQLAlchemy declarative indices | Better query performance     | Completed |
| Large result sets              | Stream results with yield_per  | Memory efficiency            | Pending   |

## 7. Technical Debt Items

| Item                          | Priority | Notes                                  | Status    |
| ----------------------------- | -------- | -------------------------------------- | --------- |
| Inconsistent error handling   | Medium   | Standardize with SQLAlchemy            | Pending   |
| Duplicated validation logic   | Medium   | Consolidate with SQLAlchemy validators | Pending   |
| Manual JSON serialization     | Low      | Use SQLAlchemy serialization helpers   | Pending   |
| Hardcoded SQL strings         | High     | Replace with SQLAlchemy queries        | Pending   |
| Lack of transaction isolation | High     | Implement with SQLAlchemy transactions | Pending   |
| Batch processing consistency  | High     | Ensure consistent metadata extraction  | Completed |

## 8. Completed Migrations

1. **Enhanced Domain and Job Models (2023-11-20)**

   - Added all metadata fields to Domain model
   - Created relationship between Domain and Job models
   - Ensured proper handling of all metadata from extraction

2. **Created BatchJob Model (2023-11-20)**

   - Implemented BatchJob model for tracking batch operations
   - Created relationships between BatchJob, Job, and Domain models
   - Added utility methods for calculating progress

3. **Implemented Domain and Job Services (2023-11-20)**

   - Created domain_service with comprehensive CRUD operations
   - Created job_service with job tracking and batch support
   - Implemented standardized metadata processing

4. **Fixed Database Connection (2023-11-20)**
   - Created proper async engine with connection pooling
   - Implemented session management for both async and sync operations
   - Ensured compatibility with pgbouncer through connection args

## 9. Additional Technical Debt (June 24, 2024)

The following technical debt items were identified during the implementation of SQLAlchemy endpoints:

### 9.1. FastAPI and Uvicorn Updates

| Item                             | Priority | Description                                                                                    | Status  |
| -------------------------------- | -------- | ---------------------------------------------------------------------------------------------- | ------- |
| Deprecated `on_event` handlers   | Medium   | Replace with lifespan event handlers per FastAPI docs                                          | Pending |
| Port conflict management         | Medium   | Implement more robust port selection mechanism                                                 | Pending |
| Standardize app creation pattern | Low      | Create consistent pattern for app creation between main and standalone apps                    | Pending |
| Consolidate test app files       | Medium   | Unify or properly document multiple test app files (sqlalchemy_app.py, test_sqlalchemy_app.py) | Pending |

### 9.2. Pydantic and Configuration

| Item                                | Priority | Description                                                                                 | Status  |
| ----------------------------------- | -------- | ------------------------------------------------------------------------------------------- | ------- |
| Missing settings attributes         | High     | Add db_min_pool_size, db_max_pool_size, db_connection_timeout to Settings class             | Pending |
| Extra fields validation errors      | High     | Fix setting validation to handle environment variables with `extra="allow"` in model_config | Pending |
| Default settings values             | Medium   | Ensure sensible default values for all settings                                             | Pending |
| Hardcoded values in `getattr` calls | Medium   | Consolidate default values to avoid duplication in multiple `getattr` calls                 | Pending |

### 9.3. Import and Dependency Issues

| Item                         | Priority | Description                                                                      | Status      |
| ---------------------------- | -------- | -------------------------------------------------------------------------------- | ----------- |
| Missing model imports        | High     | Implement or properly stub ChatRequest, ChatResponse, PlacesSearchRequest models | Pending     |
| Circular dependencies        | Medium   | Resolve circular imports between routers and database modules                    | In Progress |
| Module-level dependencies    | Medium   | Reduce module-level dependencies that cause import errors                        | Pending     |
| Inconsistent import patterns | Low      | Standardize between absolute (src.\*) and relative (..) import patterns          | Pending     |

### 9.4. URL and String Handling

| Item                               | Priority | Description                                                 | Status  |
| ---------------------------------- | -------- | ----------------------------------------------------------- | ------- |
| Inconsistent quote_plus usage      | Medium   | Standardize URL encoding approach across the codebase       | Pending |
| None handling in string operations | Medium   | Ensure consistent handling of None values in URL formatting | Pending |
| String encoding in URL parameters  | Low      | Review encoding/decoding of special characters in URLs      | Pending |

## Next Steps

1. As we migrate each component, we'll update this document to track progress
2. We'll add new items as they're identified during migration
3. We'll mark items as complete as we implement the replacements
4. We'll periodically review this document to ensure we're addressing technical debt

This document serves as both a cleanup checklist and a progress tracker for our SQLAlchemy migration efforts.
