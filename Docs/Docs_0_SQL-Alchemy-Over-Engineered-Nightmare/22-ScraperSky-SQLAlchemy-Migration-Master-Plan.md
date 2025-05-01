# ScraperSky SQLAlchemy Migration Master Plan

This document serves as the comprehensive implementation plan for completing the ScraperSky modernization project, focusing on SQLAlchemy ORM integration and service standardization.

## Project Overview

The ScraperSky modernization project aims to refactor the backend codebase to use SQLAlchemy ORM consistently, standardize service architecture, and improve code quality. The project is currently approximately 65% complete, with key services like domain_service already using SQLAlchemy fully.

## Project Status

| Area                      | Status       | Notes                                                    |
| ------------------------- | ------------ | -------------------------------------------------------- |
| SQLAlchemy Models         | 90% Complete | Most models are defined and working                      |
| Service Layer Integration | 45% Complete | Some services use SQLAlchemy, others use legacy patterns |
| Router Refactoring        | 30% Complete | Most routers still use mixed patterns                    |
| Testing Coverage          | 50% Complete | Unit tests exist for SQLAlchemy services                 |
| Documentation             | 40% Complete | Service inventory matrix created                         |

## Migration Goals

1. **Standardize Service Architecture**: All services should follow a consistent pattern
2. **Complete SQLAlchemy Integration**: Replace all raw SQL with SQLAlchemy ORM
3. **Decouple Database Operations**: Move all database operations to services
4. **Improve Error Handling**: Standardize error handling across the application
5. **Enhance Testing**: Achieve >80% test coverage for all services
6. **Optimize Performance**: Maintain or improve performance with new patterns

## Implementation Roadmap

### Phase 1: Core Service Modernization (Weeks 1-3)

#### Week 1: Core Services Foundation

1. Extend domain_service.py and job_service.py with additional methods

   - Add relationship loading capabilities
   - Create methods to replace common raw SQL queries
   - Add comprehensive error handling

2. Create service method templates for:

   - Retrieving records with relationships
   - Filtering by common criteria
   - Batch operations
   - Status tracking and updates

3. Update service tests for new methods

#### Week 2: Job Service Modernization

1. Remove legacy in-memory tracking from job_service.py

   - Replace with SQLAlchemy operations
   - Maintain backward compatibility where needed

2. Implement job relationship methods

   - Jobs with domains
   - Jobs with batch jobs
   - Jobs with results

3. Update job_service documentation and tests

#### Week 3: Batch Processor Service Modernization

1. Complete SQLAlchemy implementation in batch_processor_service.py

   - Replace direct database operations
   - Implement proper transaction management
   - Add relationship loading methods

2. Standardize batch progress tracking

   - Use SQLAlchemy events for status updates
   - Implement concurrent processing guards

3. Update batch processor tests

### Phase 2: Router Refactoring (Weeks 4-6)

#### Week 4: sitemap_scraper.py Refactoring

Following the detailed plan in [Document 21](./21-Sitemap-Scraper-Refactoring-Plan.md):

1. Replace direct database operations with service calls
2. Convert raw SQL to SQLAlchemy ORM
3. Standardize error handling
4. Break down large functions
5. Update tests for the refactored router

#### Week 5: domain_manager.py Refactoring

1. Analyze current service usage patterns
2. Identify direct database operations
3. Replace with service calls
4. Standardize error handling
5. Update tests

#### Week 6: Other Router Refactoring

1. Prioritize remaining routers based on complexity and usage
2. Apply the same refactoring patterns to each router
3. Update tests for each router

### Phase 3: Service Standardization (Weeks 7-9)

#### Week 7: Authentication and User Context Services

1. Refactor auth_service.py to use SQLAlchemy

   - Design SQLAlchemy models for permissions
   - Implement proper caching
   - Update JWT validation

2. Update user_context_service.py

   - Integrate with auth_service
   - Use SQLAlchemy for user data
   - Implement proper caching

3. Update middleware to use refactored services

#### Week 8: Error and Validation Services

1. Standardize error_service.py

   - Create consistent error handling patterns
   - Implement SQLAlchemy for error logging
   - Add structured error responses

2. Update validation_service.py

   - Use SQLAlchemy for validation rules
   - Implement standardized validation patterns
   - Add comprehensive input validation

3. Update service consumers to use new patterns

#### Week 9: Remaining Services

1. Prioritize remaining services based on usage
2. Apply SQLAlchemy patterns to each service
3. Update documentation and tests

### Phase 4: Integration and Performance Optimization (Weeks 10-12)

#### Week 10: Integration Testing

1. Create comprehensive integration tests

   - Test all service interactions
   - Verify transaction handling
   - Test concurrency scenarios

2. Fix any issues found during integration testing

#### Week 11: Performance Optimization

1. Identify performance bottlenecks

   - Add instrumentation to measure database query performance
   - Test with realistic data volumes
   - Identify slow operations

2. Optimize SQLAlchemy queries

   - Use appropriate loading strategies
   - Optimize relationship loading
   - Implement caching where appropriate

3. Update documentation with performance guidelines

#### Week 12: Final Cleanup and Documentation

1. Remove any remaining legacy code
2. Update all documentation
3. Create migration guides for future development
4. Conduct final code review

## Service Migration Priority Matrix

Based on the analysis in [Document 19](./19-Service-Inventory-Matrix.md), the following services will be migrated in order of priority:

### Highest Priority

1. **job_service** (🟨 Partial SQLAlchemy)

   - Used by: sitemap_scraper.py, domain_manager.py, batch_processor.py
   - Required changes: Remove in-memory tracking, standardize SQLAlchemy operations

2. **batch_processor_service** (🟨 Partial SQLAlchemy)

   - Used by: sitemap_scraper.py, domain_manager.py, batch_processor.py
   - Required changes: Complete SQLAlchemy implementation, remove direct database operations

3. **db_service** (❌ Legacy)
   - Used by: All components
   - Required changes: Create transition plan, replace with SQLAlchemy service calls

### Medium Priority

4. **auth_service** (❌ Legacy)

   - Used by: All components
   - Required changes: Design SQLAlchemy models for permissions, implement caching

5. **user_context_service** (❌ Legacy)

   - Used by: All components
   - Required changes: Integrate with auth_service, use SQLAlchemy models

6. **error_service** (❌ Legacy)

   - Used by: All components
   - Required changes: Standardize interfaces, add SQLAlchemy for error tracking

7. **validation_service** (❌ Legacy)
   - Used by: Most components
   - Required changes: Standardize interfaces, integrate with error_service

### Lower Priority

8. **sitemap_service** (❌ Legacy)

   - Used by: sitemap_scraper.py, batch_processor.py
   - Required changes: Convert to SQLAlchemy

9. **storage_service** (❌ Legacy)

   - Used by: export.py
   - Required changes: Update file storage operations to use SQLAlchemy for metadata

10. **api_service** and other specialized services (❌ Legacy)
    - Used by: Various components
    - Required changes: Convert to SQLAlchemy where appropriate

## Key Patterns and Best Practices

### Service Implementation Pattern

All services should follow this implementation pattern:

```python
class ExampleService:
    """Service for example operations"""

    async def create(self, session, data):
        """Create a new example"""
        example = Example(**data)
        session.add(example)
        return example

    async def get_by_id(self, session, example_id, tenant_id=None):
        """Get an example by ID with optional tenant filtering"""
        query = select(Example).where(Example.id == example_id)
        if tenant_id:
            query = query.where(Example.tenant_id == tenant_id)
        result = await session.execute(query)
        return result.scalar_one_or_none()

    async def get_all(self, session, tenant_id=None, **filters):
        """Get all examples with optional filtering"""
        query = select(Example)
        if tenant_id:
            query = query.where(Example.tenant_id == tenant_id)
        # Apply additional filters
        for key, value in filters.items():
            if hasattr(Example, key):
                query = query.where(getattr(Example, key) == value)
        result = await session.execute(query)
        return result.scalars().all()

    async def update(self, session, example_id, data, tenant_id=None):
        """Update an example"""
        example = await self.get_by_id(session, example_id, tenant_id)
        if not example:
            return None
        for key, value in data.items():
            if hasattr(example, key):
                setattr(example, key, value)
        return example

    async def delete(self, session, example_id, tenant_id=None):
        """Delete an example"""
        example = await self.get_by_id(session, example_id, tenant_id)
        if not example:
            return False
        await session.delete(example)
        return True
```

### Router Implementation Pattern

All routers should follow this implementation pattern:

```python
@router.get("/examples/{example_id}")
async def get_example(
    example_id: int,
    session: AsyncSession = Depends(get_session),
    tenant_id: int = Depends(get_tenant_id)
):
    """Get an example by ID"""
    try:
        example = await example_service.get_by_id(session, example_id, tenant_id)
        if not example:
            return error_service.not_found("Example not found")
        return {"example": example}
    except Exception as e:
        error_details = error_service.handle_exception(
            e,
            "get_example_error",
            context={"example_id": example_id, "tenant_id": tenant_id},
            log_error=True
        )
        return error_service.format_error_response(error_details)
```

### Relationship Loading Pattern

For loading relationships, use this pattern:

```python
async def get_with_relationships(self, session, model_id, tenant_id=None):
    """Get a model with relationships loaded"""
    query = (
        select(Model)
        .options(
            selectinload(Model.relationship1),
            selectinload(Model.relationship2)
        )
        .where(Model.id == model_id)
    )
    if tenant_id:
        query = query.where(Model.tenant_id == tenant_id)
    result = await session.execute(query)
    return result.scalar_one_or_none()
```

## Testing Strategy

### Unit Tests

Each service should have comprehensive unit tests covering:

1. CRUD operations
2. Error handling
3. Edge cases
4. Tenant isolation

Example test pattern:

```python
async def test_example_service_create():
    """Test creating an example"""
    async with AsyncSession(engine) as session:
        # Arrange
        data = {"name": "Test Example", "tenant_id": 1}

        # Act
        example = await example_service.create(session, data)
        await session.commit()

        # Assert
        assert example.id is not None
        assert example.name == "Test Example"
        assert example.tenant_id == 1
```

### Integration Tests

Integration tests should verify:

1. Service interactions
2. Transaction handling
3. Concurrency behavior
4. End-to-end functionality

## Monitoring and Performance Metrics

To ensure the migration doesn't negatively impact performance, implement:

1. Query execution time metrics
2. Database connection pool monitoring
3. Service method timing
4. Error rate tracking

## Rollback Plan

In case of critical issues:

1. Implement feature flags to toggle between old and new implementations
2. Maintain compatibility layers during the transition
3. Create rollback scripts to revert database schema changes
4. Implement A/B testing for critical services

## Documentation Requirements

For each refactored service:

1. Update docstrings with comprehensive method documentation
2. Document expected exceptions and error handling
3. Provide usage examples
4. Document any performance considerations
5. Update API documentation

## Conclusion

This master plan provides a structured approach to completing the ScraperSky modernization project. By following the roadmap and focusing on the highest priority services first, the team can efficiently migrate the application to a standardized SQLAlchemy ORM architecture while minimizing risk and maintaining application functionality.

Progress should be tracked against the roadmap, with regular checkpoints to ensure the project remains on schedule. Any deviations or issues should be addressed promptly to maintain momentum.

Upon completion, ScraperSky will have a more maintainable, testable, and consistent codebase, setting a solid foundation for future development.
