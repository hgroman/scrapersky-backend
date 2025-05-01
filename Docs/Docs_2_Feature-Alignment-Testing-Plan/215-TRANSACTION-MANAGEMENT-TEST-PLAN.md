# Transaction Management Testing Plan

This document outlines the comprehensive test plan for verifying proper transaction management across all ScraperSky backend components after implementing the "Routers own transaction boundaries, services do not" pattern.

## Testing Approach

The testing approach follows these principles:

1. **Unit Tests:** Verify individual component behavior
2. **Integration Tests:** Verify components work together correctly
3. **Mock Testing:** Use mocks to isolate components and verify behaviors
4. **Edge Case Testing:** Test error conditions and concurrent access

## Test Files Created

We have created the following test files:

1. **FrontendScout Testing:**
   - `/tests/transaction/test_transaction_frontendscout.py`

2. **ActionQueue Testing:**
   - `/tests/transaction/test_transaction_actionqueue.py`

3. **ContentMap Testing:**
   - `/tests/transaction/test_transaction_contentmap.py`

## Test Categories

Each test file covers the following test categories:

### 1. Transaction Awareness Tests

These tests verify that service methods check transaction state but don't create transactions:

```python
@pytest.mark.asyncio
async def test_service_method_transaction_awareness(mock_session, mock_session_in_transaction):
    """Test that service method checks transaction state but doesn't create transactions."""
    service = ServiceClass()
    
    # Test with session not in transaction
    await service.method(mock_session, ...)
    mock_session.in_transaction.assert_called_once()
    
    # Test with session already in transaction
    await service.method(mock_session_in_transaction, ...)
    mock_session_in_transaction.in_transaction.assert_called_once()
```

### 2. Router Transaction Management Tests

These tests verify that router methods create transaction boundaries:

```python
@pytest.mark.asyncio
async def test_router_method_creates_transaction(mock_session):
    """Test that the router method creates a transaction."""
    # Mock service method
    with patch("src.services.service_module.service_method", new=AsyncMock(return_value=...)):
        # Call the router method
        await router_method(..., session=mock_session)
        
        # Verify the router created a transaction
        mock_session.begin.assert_called_once()
```

### 3. Background Task Tests

These tests verify that background tasks create their own sessions and transactions:

```python
@pytest.mark.asyncio
async def test_background_task_creates_own_session():
    """Test that background task creates its own session."""
    # Mock session factory
    mock_session = AsyncMock(spec=AsyncSession)
    
    with patch("src.db.session.async_session_factory", return_value=mock_session):
        # Call background task method
        await background_task_method(...)
        
        # Verify session was created and transaction was started
        mock_session.begin.assert_called_once()
```

### 4. Exception Propagation Tests

These tests verify that service methods propagate exceptions for transaction management:

```python
@pytest.mark.asyncio
async def test_service_method_exception_propagation(mock_session):
    """Test that exceptions in service method are propagated to the caller."""
    service = ServiceClass()
    
    # Mock dependency to raise exception
    dependency_mock = AsyncMock(side_effect=Exception("Test error"))
    
    with patch.object(service, '_dependency_method', new=dependency_mock):
        # Test that the exception is propagated
        with pytest.raises(Exception, match="Test error"):
            await service.method(mock_session, ...)
```

### 5. Concurrency Tests

These tests verify behavior under concurrent access:

```python
@pytest.mark.asyncio
async def test_concurrent_service_access():
    """Test that concurrent service access maintains transaction isolation."""
    # Create tasks to simulate concurrent access
    tasks = [
        asyncio.create_task(service.method(session1, ...)),
        asyncio.create_task(service.method(session2, ...))
    ]
    
    # Run tasks concurrently
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Verify results maintain transaction isolation
    # ...
```

## Running the Tests

To run the transaction management tests:

```bash
# Run all transaction tests
pytest tests/transaction/

# Run specific component tests
pytest tests/transaction/test_transaction_frontendscout.py
pytest tests/transaction/test_transaction_actionqueue.py
pytest tests/transaction/test_transaction_contentmap.py

# Run with verbose output
pytest -v tests/transaction/

# Run with coverage
pytest --cov=src.services --cov=src.routers tests/transaction/
```

## Test Fixtures

The test files use the following fixtures:

### Mock Session Fixtures

```python
@pytest.fixture
def mock_session():
    """Create a mock SQLAlchemy session for testing."""
    session = AsyncMock(spec=AsyncSession)
    # Mock the in_transaction method to return False by default
    session.in_transaction.return_value = False
    # Mock flush to do nothing
    session.flush = AsyncMock()
    # Mock begin to return a context manager
    cm = MagicMock()
    cm.__aenter__ = AsyncMock(return_value=None)
    cm.__aexit__ = AsyncMock(return_value=None)
    session.begin.return_value = cm
    
    return session


@pytest.fixture
def mock_session_in_transaction():
    """Create a mock SQLAlchemy session that's already in a transaction."""
    session = AsyncMock(spec=AsyncSession)
    # Mock the in_transaction method to return True
    session.in_transaction.return_value = True
    # Mock flush to do nothing
    session.flush = AsyncMock()
    
    return session
```

### Mock Background Tasks Fixture

```python
@pytest.fixture
def mock_background_tasks():
    """Create a mock BackgroundTasks."""
    bg_tasks = AsyncMock(spec=BackgroundTasks)
    bg_tasks.add_task = MagicMock()
    return bg_tasks
```

## Integration Test Plan

After unit tests pass, integration tests should verify:

1. **End-to-End Router-Service Interactions:**
   - Router properly begins transaction
   - Service methods use transaction correctly
   - Transaction commits on success
   - Transaction rolls back on failure

2. **Router-Service-Background Task Interactions:**
   - Router begins transaction
   - Service registers background task
   - Transaction commits
   - Background task runs with its own session
   - Background task properly manages its own transaction

3. **Complex Multi-Component Workflows:**
   - Verify transaction integrity across component boundaries
   - Check that no nested transactions occur
   - Validate that results are consistent with transaction boundaries

## Verification in Production

After deploying the changes, monitor:

1. **Database Locks:** Check for reduction in database lock timeouts and deadlocks
2. **Transaction Duration:** Monitor transaction duration for improvements
3. **Error Rates:** Check for reduction in transaction-related errors
4. **Performance:** Monitor database connection usage and query performance

## Summary

This test plan provides comprehensive verification of transaction management across all components, ensuring the "Routers own transaction boundaries, services do not" pattern is consistently applied and functioning correctly.