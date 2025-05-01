# ScraperSky sitemap_scraper.py Service Usage Analysis

This document provides a detailed analysis of service usage in the sitemap_scraper.py file, identifying patterns, inconsistencies, and areas for improvement.

## 1. Service Import Analysis

The sitemap_scraper.py file imports multiple services from different locations:

```python
from ..services.core.auth_service import auth_service
from ..services.core.user_context_service import user_context_service
from ..services.error.error_service import error_service
from ..services.validation.validation_service import validation_service
from ..services.batch.batch_processor_service import batch_processor_service
from ..services.db_service import db_service
from ..services.domain_service import domain_service
from ..services.job_service import job_service
```

### Observations:

1. **Inconsistent Import Paths**:

   - Some services are imported from subdirectories (core/, error/, validation/, batch/)
   - Others are imported from the root services directory (db_service, domain_service, job_service)

2. **Mixing of Service Patterns**:
   - Some services use the SQLAlchemy pattern (domain_service, job_service)
   - Others use the legacy pattern (auth_service, error_service)

## 2. Service Usage Analysis

### 2.1 Domain Service

The domain_service is properly used for domain-related operations:

```python
# Creating a domain
domain = await domain_service.create(session, {
    "domain": standardized_domain,
    "tenant_id": tenant_id,
    "status": "pending",
    "created_by": user_id
})

# Getting a domain by ID
domain = await domain_service.get_by_id(session, domain_id, tenant_id)
```

### 2.2 Job Service

The job_service is properly used for job operations, but has mixed patterns:

```python
# Modern SQLAlchemy usage
job = await job_service.create(session, {
    "job_type": "domain_scan",
    "tenant_id": tenant_id,
    "status": "pending",
    "domain_id": domain.id
})

# Legacy in-memory usage (should be removed)
job_id = job_service.create_job("batch_scan", {"status": "pending"})
job_service.update_job_status(job_id, {"status": "running"})
```

### 2.3 DB Service

The db_service is used for direct SQL queries, which should be replaced with domain_service or model-specific services:

```python
# Direct SQL through db_service
select_result = await db_service.fetch_all(domains_query, {"tenant_id": tenant_id})
```

### 2.4 Batch Processor Service

The batch_processor_service is used properly, but could benefit from full SQLAlchemy integration:

```python
batch_result = await batch_processor_service.process_domains_batch(
    domains=domains,
    processor_type=processor_type,
    tenant_id=tenant_id,
    user_id=user_id,
    options=options
)
```

### 2.5 Other Services

Other services (auth_service, error_service, validation_service) are used consistently for their intended purposes but don't use SQLAlchemy.

## 3. Direct Database Operations

The file contains several instances of direct database operations that bypass service layers:

```python
# Direct session operations
await session.commit()
result = await session.execute(query)
domain_session.add(domain_job)
```

These should be encapsulated in appropriate services.

## 4. SQLAlchemy Usage

The file uses SQLAlchemy in inconsistent ways:

1. **Modern Pattern** (preferred):

```python
# Using service methods that handle SQLAlchemy internally
domain = await domain_service.create(session, {...})
```

2. **Direct SQLAlchemy Usage** (should be encapsulated in services):

```python
# Direct SQLAlchemy queries
query = select(Job).options(selectinload(Job.domain)).where(Job.id == job_id_int)
result = await session.execute(query)
```

3. **Legacy SQL Pattern** (should be replaced):

```python
# Raw SQL through db_service
domains_query = """
    SELECT id, domain, tenant_id, status, last_scan
    FROM domains
    WHERE tenant_id = %(tenant_id)s
"""
select_result = await db_service.fetch_all(domains_query, {"tenant_id": tenant_id})
```

## 5. Function Analysis

### 5.1 scan_domain

**Purpose**: Scans a single domain and extracts metadata
**Services Used**: domain_service, job_service, validation_service, auth_service
**Issues**:

- Uses proper SQLAlchemy session management
- Good example of service usage

### 5.2 batch_scan_domains

**Purpose**: Processes multiple domains in batch mode
**Services Used**: batch_processor_service, auth_service, validation_service
**Issues**:

- Has both a legacy and modern implementation
- Legacy implementation should be removed

### 5.3 process_domain_scan

**Purpose**: Background processing for a single domain scan
**Services Used**: job_service, domain_service
**Issues**:

- Uses proper SQLAlchemy session management
- Some error handling could be improved

### 5.4 process_batch_scan_sqlalchemy

**Purpose**: Background processing for batch domain scans
**Services Used**: job_service, domain_service
**Issues**:

- Proper SQLAlchemy usage
- Some direct session operations that should be encapsulated in services

### 5.5 process_batch_scan_legacy

**Purpose**: Legacy implementation of batch processing
**Services Used**: db_service, job_service (memory-based version)
**Issues**:

- Should be completely removed once migration is complete

## 6. Linter Issues

The file has numerous linter errors, including:

1. **Indentation Issues**:

   - Inconsistent indentation in nested functions
   - Mixed tab and space usage

2. **Unused Variables**:

   - Several variables defined but not used
   - Parameters passed but not utilized

3. **Import Issues**:

   - Duplicate imports
   - Unused imports

4. **Error Handling**:

   - Some nested try/except blocks with broad exception handling
   - Inconsistent error logging patterns

5. **Function Length**:
   - Several functions exceed recommended length
   - Some functions have too many responsibilities

## 7. Recommendations

### 7.1 Service Usage Improvements

1. **Standardize Service Imports**:

   - Use consistent import paths for all services
   - Decide on a modular approach and stick with it

2. **Remove Legacy Patterns**:

   - Remove all in-memory job tracking
   - Remove raw SQL queries

3. **Encapsulate Direct Database Operations**:

   - Move direct session.execute, session.add operations into service methods

4. **Service Conversion Priority**:
   - Convert db_service usage to domain_service or other model-specific services
   - Update job_service to remove legacy patterns
   - Convert raw SQL to SQLAlchemy ORM queries

### 7.2 Code Quality Improvements

1. **Fix Linter Errors**:

   - Address indentation issues
   - Remove unused variables and imports
   - Fix error handling patterns

2. **Refactor Large Functions**:

   - Break down process_domain_scan and process_batch_scan_sqlalchemy
   - Extract common functionality into helper methods

3. **Standardize Error Handling**:
   - Use consistent error service patterns
   - Improve error details and logging

### 7.3 Implementation Strategy

The recommended approach is to:

1. First convert the use of db_service with raw SQL to domain_service with SQLAlchemy
2. Then remove the legacy in-memory job tracking in job_service
3. Next standardize the error handling patterns
4. Finally refactor large functions for better maintainability

## 8. Example Refactoring Patterns

### 8.1 Replace Raw SQL with Domain Service

From:

```python
domains_query = """
    SELECT id, domain, tenant_id, status, last_scan
    FROM domains
    WHERE tenant_id = %(tenant_id)s
"""
select_result = await db_service.fetch_all(domains_query, {"tenant_id": tenant_id})
```

To:

```python
domains = await domain_service.get_all(session, tenant_id=tenant_id)
```

### 8.2 Replace In-Memory Job Tracking

From:

```python
job_id = job_service.create_job("batch_scan", {"status": "pending"})
job_service.update_job_status(job_id, {"status": "running"})
```

To:

```python
job = await job_service.create(session, {
    "job_type": "batch_scan",
    "tenant_id": tenant_id,
    "status": "pending"
})
await job_service.update_status(session, job.id, "running")
```

### 8.3 Encapsulate Direct Database Operations

From:

```python
query = select(Job).options(selectinload(Job.domain)).where(Job.id == job_id_int)
if tenant_id:
    query = query.where(Job.tenant_id == tenant_id)
result = await session.execute(query)
job = result.scalar_one_or_none()
```

To:

```python
job = await job_service.get_by_id(session, job_id, tenant_id)
```

## 9. Conclusion

The sitemap_scraper.py file shows evidence of being in transition from legacy patterns to SQLAlchemy-based services. It has some good examples of proper service usage, but also contains legacy code and inconsistent patterns.

By standardizing service usage, removing legacy patterns, and improving code quality, this file can serve as a model for the rest of the codebase in adopting SQLAlchemy throughout the service layer.
