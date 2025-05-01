# Sitemap Scraper SQLAlchemy Migration Plan

This document outlines the comprehensive plan for migrating the sitemap scraper functionality from raw SQL to SQLAlchemy ORM. This migration is part of the larger modernization effort to standardize the codebase around SQLAlchemy as detailed in our earlier documents.

## 1. Database Tables and Models Analysis

Based on the sitemap_scraper.py code, we need to ensure we have SQLAlchemy models for the following tables:

### 1.1 Core Tables Requiring Models

| Table Name | Current Status | Required Fields                                                                                                                                                                                                         | Notes                                      |
| ---------- | -------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------ |
| domains    | Model created  | id, domain, tenant_id, status, last_scan, meta_json, title, description, favicon_url, logo_url, language, is_wordpress, wordpress_version, has_elementor, email_addresses, phone_numbers, social media URLs, tech_stack | Primary entity storing domain scan results |
| jobs       | Model created  | id, job_type, domain_id, tenant_id, status, created_at, completed_at, result, error, progress, metadata                                                                                                                 | Tracks background job status               |
| batch_jobs | Needs model    | id, batch_id, status, total_domains, completed_domains, failed_domains, tenant_id, created_at, completed_at                                                                                                             | Tracks batch processing jobs               |

### 1.2 Model Enhancements Needed

1. **Domain Model Enhancements**:

   - Ensure all fields from raw SQL queries are represented
   - Add proper relationships to Job model
   - Implement to_dict/serialization methods

2. **Job Model Enhancements**:

   - Add relationship to Domain model
   - Add progress tracking fields
   - Add metadata JSON field

3. **BatchJob Model (New)**:
   - Create model for tracking batch operations
   - Define relationships to individual job records

## 2. Service Layer Migration

We need to implement SQLAlchemy versions of these services:

### 2.1 Core Service Replacements

| Current Service         | SQLAlchemy Replacement                   | Status                | Priority |
| ----------------------- | ---------------------------------------- | --------------------- | -------- |
| db_service              | SQLAlchemy session management            | Partially Implemented | High     |
| job_service             | job_service using SQLAlchemy models      | Not Started           | High     |
| error_service           | error_service adapted for SQLAlchemy     | Not Started           | Medium   |
| validation_service      | validation_service with model validation | Not Started           | Medium   |
| batch_processor_service | batch_processor_service using SQLAlchemy | Not Started           | High     |
| auth_service            | auth_service integrated with SQLAlchemy  | Not Started           | Medium   |
| user_context_service    | user_context_service with SQLAlchemy     | Not Started           | Low      |

### 2.2 New Service Implementations

1. **SQLAlchemy Session Service**:

   - Manage async session creation/management
   - Handle transaction boundaries
   - Provide session dependency injection

2. **Domain Service**:

   - CRUD operations for domains
   - Domain metadata processing
   - Tenant isolation enforcement

3. **Job Service**:

   - Job tracking with SQLAlchemy
   - Status updates
   - Background processing integration

4. **Batch Service**:
   - Batch job tracking
   - Concurrency management
   - Progress tracking

## 3. Migration Strategy for sitemap_scraper.py

### 3.1 Pre-Migration Preparation

1. **Complete SQLAlchemy Models**:

   - Ensure Domain and Job models are complete
   - Create BatchJob model if needed
   - Test model CRUD operations

2. **Implement Core Service Replacements**:
   - Complete domain_service
   - Complete job_service

### 3.2 Iterative Migration Approach

Rather than migrating the entire file at once, we'll take an iterative approach:

1. **Phase 1: Domain Operations**

   - Migrate domain creation and updates to use SQLAlchemy
   - Keep job tracking as-is temporarily

2. **Phase 2: Job Management**

   - Migrate job creation and status updates to use SQLAlchemy
   - Implement transaction management

3. **Phase 3: Background Processing**

   - Update background task functions to use SQLAlchemy
   - Maintain existing concurrency patterns

4. **Phase 4: Batch Processing**

   - Migrate batch processing to use SQLAlchemy
   - Ensure proper transaction isolation

5. **Phase 5: Status Endpoints**
   - Update status check endpoints to use SQLAlchemy queries
   - Maintain API compatibility

### 3.3 Specific Function Migrations

For each function in sitemap_scraper.py:

1. **scan_domain**:

   - Replace direct SQL with domain_service.create()
   - Replace job creation with job_service.create()
   - Maintain background task execution

2. **batch_scan_domains**:

   - Replace db_service with domain_service
   - Replace job_service with SQLAlchemy version
   - Maintain batch processing logic

3. **get_scan_status**:

   - Replace job status fetch with SQLAlchemy queries
   - Ensure backward compatibility

4. **get_batch_status**:

   - Replace batch status queries with SQLAlchemy
   - Maintain response format compatibility

5. **process_domain_scan**:

   - Replace direct SQL with domain_service operations
   - Implement proper transaction management
   - Maintain error handling patterns

6. **process_batch_scan**:
   - Replace job and domain operations with SQLAlchemy
   - Maintain concurrency with semaphores
   - Use SQLAlchemy transactions properly

## 4. Dependency Management

The following dependencies need to be updated:

### 4.1 Core Dependencies

- Update import statements to use new SQLAlchemy services
- Replace raw SQL references with ORM queries
- Update error handling for SQLAlchemy exceptions

### 4.2 Circular Dependency Prevention

- Use dependency injection for services
- Implement proper layering to prevent circular imports
- Use factory patterns where appropriate

## 5. Data Consistency Considerations

### 5.1 Migration Period

During the migration period, we need to ensure:

- Both old and new systems can read the same data
- Writes are performed consistently
- No data is lost during the transition

### 5.2 Validation Steps

- Compare results from old and new implementations
- Verify transaction boundaries are maintained
- Ensure tenant isolation is preserved

## 6. Implementation Order

1. **Update Domain Model and Service**:

   - Complete the Domain model with all fields
   - Implement domain_service CRUD operations
   - Test basic domain operations

2. **Update Job Model and Service**:

   - Complete the Job model with status tracking
   - Implement job_service CRUD operations
   - Test job tracking functionality

3. **Single Domain Scan Endpoint**:

   - Update the scan_domain endpoint to use SQLAlchemy
   - Test with background processing

4. **Background Processing**:

   - Update process_domain_scan to use SQLAlchemy
   - Test end-to-end flow

5. **Batch Processing**:

   - Update batch operations to use SQLAlchemy
   - Test with concurrency

6. **Status Endpoints**:
   - Update status endpoints to use SQLAlchemy queries
   - Test compatibility with existing clients

## 7. Testing Strategy

### 7.1 Unit Tests

- Test each new SQLAlchemy model
- Test each service method
- Verify transaction boundaries

### 7.2 Integration Tests

- Test full endpoint functionality
- Verify background processing works
- Test batch processing concurrency

### 7.3 Data Validation

- Compare results from old and new implementations
- Verify data integrity
- Check tenant isolation

## 8. Rollback Plan

If issues arise during migration:

1. **Endpoint-level Rollback**:

   - Keep old implementations alongside new ones
   - Switch back to old implementation if needed

2. **Service-level Rollback**:
   - Maintain backward compatibility in services
   - Allow switching to previous implementation

## 9. SQLAlchemy Best Practices to Implement

1. **Use Session Management**:

   ```python
   async with async_session() as session:
       async with session.begin():
           # Work with session here
   ```

2. **Use Relationships**:

   ```python
   # Define relationships in models
   domains = relationship("Domain", back_populates="jobs")
   ```

3. **Use Async Query API**:

   ```python
   result = await session.execute(
       select(Domain).where(Domain.tenant_id == tenant_id)
   )
   domains = result.scalars().all()
   ```

4. **Proper Transaction Management**:

   ```python
   async with session.begin():
       # Everything here happens in a transaction
       session.add(domain)
       session.add(job)
   ```

5. **Type-Safe Filters**:
   ```python
   # Instead of string-based WHERE clauses
   query = select(Domain).where(
       Domain.tenant_id == tenant_id,
       Domain.status == "active"
   )
   ```

## 10. Timeline and Milestones

1. **Week 1: Core Models and Services**

   - Complete Domain and Job models
   - Implement basic CRUD services
   - Set up proper session management

2. **Week 2: Single Domain Endpoint**

   - Migrate scan_domain endpoint
   - Update background processing
   - Test end-to-end flow

3. **Week 3: Batch Processing**

   - Migrate batch processing
   - Update status endpoints
   - Complete testing

4. **Week 4: Optimization and Cleanup**
   - Performance optimization
   - Code cleanup
   - Documentation update

## Conclusion

This migration plan provides a structured approach to converting the sitemap scraper and its dependencies from raw SQL to SQLAlchemy. By following this plan, we'll ensure a smooth transition while maintaining application functionality and performance.

The migration will deliver:

- Improved code quality through ORM usage
- Better type safety and error handling
- Consistent patterns for database access
- Proper transaction management
- A template for migrating other endpoints
