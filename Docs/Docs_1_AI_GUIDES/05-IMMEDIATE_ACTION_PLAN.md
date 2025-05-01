# IMMEDIATE ACTION PLAN

This document outlines a practical, step-by-step plan to complete the ScraperSky project with minimal complications and maximum effectiveness.

## 1. MODULE MAP & CRITICAL PATH IDENTIFICATION

### Core Modules Map

```
+----------------+    +----------------+    +----------------+
| AUTH SYSTEM    | -> | RBAC SYSTEM    | -> | FEATURE FLAGS  |
+----------------+    +----------------+    +----------------+
        |                     |                     |
        v                     v                     v
+----------------+    +----------------+    +----------------+
| API ENDPOINTS  | -> | SERVICES       | -> | DATA MODELS    |
+----------------+    +----------------+    +----------------+
        |                     |                     |
        v                     v                     v
+----------------+    +----------------+    +----------------+
| BACKGROUND     | -> | DATABASE       | -> | ERROR HANDLING |
| TASKS          |    | OPERATIONS     |    | & LOGGING      |
+----------------+    +----------------+    +----------------+
```

### Critical Paths (In Priority Order)

1. **Sitemap Scanning**
   - Router: `modernized_sitemap.py`
   - Service: `sitemap/processing_service.py`
   - Models: `sitemap.py`, `domain.py`
   - Background: Process domain scanning

2. **Batch Page Processing**
   - Router: `batch_page_scraper.py`
   - Service: `batch/batch_processor_service.py`
   - Models: `batch_job.py`, `job.py`
   - Background: Process batch jobs

3. **Google Maps API**
   - Router: `google_maps_api.py`
   - Service: `places/places_service.py`
   - Models: `place.py`, `place_search.py`

4. **ContentMap Feature**
   - Router: `sitemap_analyzer.py`
   - Service: `sitemap/sitemap_service.py`
   - Models: `sitemap.py`

5. **RBAC System**
   - Router: `rbac_*.py` routes
   - Service: `rbac/unified_rbac_service.py`
   - Models: `rbac.py`, `profile.py`

## 2. FOCUSED FIXES (ONE AT A TIME)

### 1. Sitemap Database Insertion (COMPLETED)

- Fix transaction management in `_process_domain`
- Remove nested transactions
- Ensure proper session handling

### 2. Batch Processing Transaction Fix

- Apply same transaction pattern as sitemap
- Remove nested transactions
- Ensure background tasks create own sessions
- Document with transaction flow diagram

### 3. Google Maps API Transaction Fix

- Apply consistent transaction pattern
- Ensure service methods don't create transactions
- Document any context-specific adjustments

### 4. ContentMap Database Persistence

- Ensure consistent model usage
- Fix any database connection issues
- Apply transaction pattern from sitemap fix

### 5. RBAC System Optimization

- Review and fix transaction issues
- Consolidate permission checking
- Ensure consistent tenant isolation

## 3. STANDARDIZED TESTING APPROACH

Create a test template for each critical component:

### Database Transaction Test Template

```python
async def test_transaction_rollback_on_error():
    """Test that transactions properly rollback on error."""
    # Setup test data
    test_data = generate_test_data()
    
    # Create service with mock that will raise exception
    service = create_service_with_error_trigger()
    
    # Execute service method within transaction
    async with get_test_session() as session:
        async with session.begin():
            try:
                await service.method_that_will_fail(session, test_data)
                assert False, "Method should have raised exception"
            except Exception:
                pass
    
    # Verify database state - transaction should have rolled back
    async with get_test_session() as verify_session:
        result = await verify_session.execute(
            select(Model).where(Model.id == test_data["id"])
        )
        assert result.scalars().first() is None, "Transaction was not rolled back"
```

### Background Task Test Template

```python
async def test_background_task_session_management():
    """Test that background tasks properly manage their sessions."""
    # Setup test data and tracking
    task_id = str(uuid.uuid4())
    test_data = generate_test_data()
    
    # Execute background task
    await run_background_task(
        task_func=service.background_task,
        task_id=task_id,
        data=test_data
    )
    
    # Verify database state - task should have completed
    async with get_test_session() as verify_session:
        result = await verify_session.execute(
            select(TaskStatus).where(TaskStatus.task_id == task_id)
        )
        task_status = result.scalars().first()
        assert task_status is not None, "Task status not recorded"
        assert task_status.status == "completed", "Task not completed"
```

### Implementation Steps

1. Create test templates for each critical component
2. Implement tests for each fixed module
3. Run tests as part of the fix verification
4. Document test results with each fix

## 4. EXECUTION WORKFLOW

### For Each Critical Path Component:

1. **Assessment**
   - Run existing tests if available
   - Document current behavior
   - Identify specific issues

2. **Focused Fix**
   - Use the appropriate AI expert role
   - Make minimal, targeted changes
   - Follow established patterns

3. **Verification**
   - Run automated tests
   - Manually test the component
   - Document the fix

4. **Documentation**
   - Update relevant documentation
   - Create fix summary
   - Document any deviations from patterns

### Task Execution Checklist

For each component fix:

- [ ] Assessment completed
- [ ] AI session initiated with appropriate role
- [ ] Fix implemented
- [ ] Tests created/updated
- [ ] Tests passing
- [ ] Manual verification completed
- [ ] Documentation updated
- [ ] Fix summary created

## 5. DATABASE INTEGRITY CHECKS

Create scripts to verify database integrity after fixes:

### Transaction Verification

```python
async def verify_transaction_integrity():
    """Verify that transactions are working correctly."""
    # Setup test data
    test_id = str(uuid.uuid4())
    
    # Test transaction commit
    async with get_session() as session:
        async with session.begin():
            session.add(TestModel(id=test_id, name="test"))
    
    # Verify commit worked
    async with get_session() as verify_session:
        result = await verify_session.execute(
            select(TestModel).where(TestModel.id == test_id)
        )
        assert result.scalars().first() is not None, "Transaction commit failed"
    
    # Test transaction rollback
    rollback_id = str(uuid.uuid4())
    try:
        async with get_session() as session:
            async with session.begin():
                session.add(TestModel(id=rollback_id, name="test"))
                raise ValueError("Trigger rollback")
    except ValueError:
        pass
    
    # Verify rollback worked
    async with get_session() as verify_session:
        result = await verify_session.execute(
            select(TestModel).where(TestModel.id == rollback_id)
        )
        assert result.scalars().first() is None, "Transaction rollback failed"
```

### Database Access Verification

```python
async def verify_database_access_patterns():
    """Verify that database access follows established patterns."""
    # Check service methods don't create transactions
    service = TestService()
    created_transaction = False
    
    class MockSession:
        def begin(self):
            nonlocal created_transaction
            created_transaction = True
    
    mock_session = MockSession()
    await service.read_method(mock_session, "test")
    
    assert not created_transaction, "Service method created transaction"
```

### Implementation Steps

1. Create database integrity verification scripts
2. Run scripts after each fix
3. Document verification results

## 6. COMPLETION CRITERIA

For overall project completion:

1. **Critical Path Functionality**
   - All critical paths are working
   - Tests are passing
   - Manual verification successful

2. **Documentation**
   - Code documentation is complete
   - Architecture documentation is updated
   - Test documentation is complete

3. **Code Quality**
   - No known bugs in critical paths
   - Consistent patterns are applied
   - No unnecessary complexity

4. **Performance**
   - Database operations are efficient
   - API response times are acceptable
   - Background tasks complete successfully

## 7. HANDOFF PREPARATION

1. **Project Structure Documentation**
   - Create module dependency diagram
   - Document component interactions
   - Explain transaction flow

2. **Developer Guide**
   - Document how to add new endpoints
   - Explain how to add new service methods
   - Provide transaction management guide

3. **Operations Guide**
   - Document deployment process
   - Explain database maintenance
   - Provide troubleshooting guide