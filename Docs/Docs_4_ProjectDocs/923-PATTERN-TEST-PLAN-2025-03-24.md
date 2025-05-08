# DATABASE PATTERN TEST PLAN

## Project Context

We've just completed a major database service consolidation project for the ScraperSky backend. This project standardized all database access patterns across the codebase to ensure consistent transaction management, proper session handling, and appropriate error handling. The following key patterns were established:

1. **Routers own transaction boundaries** using `async with session.begin()`
2. **Services are transaction-aware but don't create transactions**
3. **Session dependency injection** using FastAPI's `Depends(get_session_dependency)`
4. **Background tasks create and manage their own sessions**
5. **Consistent error handling with appropriate transaction rollback**

The consolidation covered 11 files:
- `src/db/sitemap_handler.py`
- `src/routers/sitemap_analyzer.py`
- `src/routers/modernized_sitemap.py`
- `src/routers/db_portal.py`
- `src/services/db_inspector.py`
- `src/db/domain_handler.py`
- `src/routers/dev_tools.py`
- `src/routers/google_maps_api.py`
- `src/routers/batch_page_scraper.py`
- `src/routers/modernized_page_scraper.py`
- `src/routers/profile.py`

Now, we need to create comprehensive tests to verify these patterns are working correctly.

## Test Framework Setup

1. **Directory Structure**
   Create the following directory structure:
   ```
   tests/
   ├── conftest.py                      # Shared pytest fixtures
   ├── db_patterns/
   │   ├── __init__.py
   │   ├── test_transaction_boundaries.py
   │   ├── test_session_dependency.py
   │   ├── test_service_methods.py
   │   └── test_background_tasks.py
   └── utils/
       ├── __init__.py
       └── test_helpers.py              # Helper functions for testing
   ```

2. **Dependencies**
   Ensure the following packages are installed:
   - pytest
   - pytest-asyncio
   - pytest-mock
   - SQLAlchemy (already in requirements.txt)
   - httpx (for testing FastAPI endpoints)

   Command: `pip install pytest pytest-asyncio pytest-mock httpx`

3. **conftest.py Setup**
   Create a conftest.py file in the tests directory with the following core fixtures:

   ```python
   import asyncio
   import pytest
   from typing import AsyncGenerator, List, Dict, Any
   from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
   from sqlalchemy.orm import declarative_base
   from sqlalchemy.pool import NullPool
   from sqlalchemy import Column, Integer, String, Boolean, text
   
   # Create in-memory SQLite database for testing
   TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
   Base = declarative_base()
   
   # Sample model for testing
   class TestEntity(Base):
       __tablename__ = "test_entities"
       id = Column(Integer, primary_key=True)
       name = Column(String, nullable=False)
       active = Column(Boolean, default=True)
   
   @pytest.fixture(scope="session")
   def event_loop():
       """Create an instance of the default event loop for each test case."""
       loop = asyncio.get_event_loop_policy().new_event_loop()
       yield loop
       loop.close()
   
   @pytest.fixture(scope="session")
   async def db_engine() -> AsyncGenerator[AsyncEngine, None]:
       """Create a SQLAlchemy async engine for testing."""
       engine = create_async_engine(
           TEST_DATABASE_URL,
           poolclass=NullPool,
           future=True,
           echo=False  # Set to True for SQL debugging
       )
       
       async with engine.begin() as conn:
           await conn.run_sync(Base.metadata.create_all)
       
       yield engine
       
       async with engine.begin() as conn:
           await conn.run_sync(Base.metadata.drop_all)
       
       await engine.dispose()
   
   @pytest.fixture
   async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
       """Create a SQLAlchemy async session for testing."""
       connection = await db_engine.connect()
       transaction = await connection.begin()
       session = AsyncSession(bind=connection, expire_on_commit=False)
       
       yield session
       
       await session.close()
       await transaction.rollback()
       await connection.close()
   
   @pytest.fixture
   async def seed_test_data(db_session) -> None:
       """Seed test data into the database."""
       async with db_session.begin():
           for i in range(5):
               db_session.add(TestEntity(name=f"Test Entity {i}"))
   ```

## Test Cases

### 1. Transaction Boundaries Test (test_transaction_boundaries.py)

These tests verify that routers properly own transaction boundaries.

```python
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select
from tests.conftest import TestEntity

# Mock router function to test transaction commit
async def mock_router_success(session: AsyncSession):
    # Router owns transaction boundaries
    async with session.begin():
        # Add an entity within transaction
        session.add(TestEntity(name="Transaction Test"))

# Mock router function to test transaction rollback
async def mock_router_failure(session: AsyncSession):
    async with session.begin():
        # Add an entity
        session.add(TestEntity(name="Should Be Rolled Back"))
        # Raise exception to trigger rollback
        raise ValueError("Simulated error")

@pytest.mark.asyncio
async def test_transaction_commit(db_session):
    """Test that transactions are properly committed when successful."""
    # Arrange - Get initial count
    result = await db_session.execute(select(TestEntity))
    initial_count = len(result.scalars().all())
    
    # Act - Execute router function
    await mock_router_success(db_session)
    
    # Assert - Verify entity was committed
    result = await db_session.execute(select(TestEntity))
    entities = result.scalars().all()
    assert len(entities) == initial_count + 1
    assert any(entity.name == "Transaction Test" for entity in entities)

@pytest.mark.asyncio
async def test_transaction_rollback(db_session):
    """Test that transactions are properly rolled back on exceptions."""
    # Arrange - Get initial count
    result = await db_session.execute(select(TestEntity))
    initial_count = len(result.scalars().all())
    
    # Act - Execute router function that should fail
    with pytest.raises(ValueError):
        await mock_router_failure(db_session)
    
    # Assert - Verify no entity was committed
    result = await db_session.execute(select(TestEntity))
    entities = result.scalars().all()
    assert len(entities) == initial_count
    assert all(entity.name != "Should Be Rolled Back" for entity in entities)

@pytest.mark.asyncio
async def test_nested_transaction(db_session):
    """Test that nested transactions work correctly."""
    # Arrange - Get initial count
    result = await db_session.execute(select(TestEntity))
    initial_count = len(result.scalars().all())
    
    # Act - Execute nested transactions
    async with db_session.begin():
        # Outer transaction
        session.add(TestEntity(name="Outer Transaction"))
        
        async with db_session.begin_nested():
            # Inner transaction
            session.add(TestEntity(name="Inner Transaction"))
            
            # This rollback should only affect the inner transaction
            await db_session.rollback()
    
    # Assert - Verify outer transaction was committed
    result = await db_session.execute(select(TestEntity))
    entities = result.scalars().all()
    assert len(entities) == initial_count + 1
    assert any(entity.name == "Outer Transaction" for entity in entities)
    assert all(entity.name != "Inner Transaction" for entity in entities)
```

### 2. Session Dependency Test (test_session_dependency.py)

These tests verify that the session dependency injection works correctly.

```python
import pytest
from unittest.mock import AsyncMock, patch
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from tests.conftest import TestEntity

# Mock session dependency
async def get_test_session_dependency():
    # This would be replaced with the actual session in tests
    yield AsyncMock(spec=AsyncSession)

# Create mock router
app = FastAPI()

@app.get("/test")
async def test_endpoint(session: AsyncSession = Depends(get_test_session_dependency)):
    # Simulate a database query
    async with session.begin():
        await session.execute(select(TestEntity))
    return {"status": "success"}

@pytest.mark.asyncio
async def test_session_dependency_injection():
    """Test that session is properly injected into endpoints."""
    # Arrange
    mock_session = AsyncMock(spec=AsyncSession)
    
    # Replace the dependency with our mock
    with patch("test_session_dependency.get_test_session_dependency", return_value=mock_session):
        client = TestClient(app)
        
        # Act
        response = client.get("/test")
        
        # Assert
        assert response.status_code == 200
        assert response.json() == {"status": "success"}
        
        # Verify session methods were called
        mock_session.begin.assert_called_once()
        mock_session.execute.assert_called_once()

@pytest.mark.asyncio
async def test_connection_pooling(db_engine):
    """Test that connection pooling works correctly."""
    # Simulate multiple concurrent sessions using the same engine
    sessions = []
    for _ in range(5):
        session = AsyncSession(bind=db_engine)
        sessions.append(session)
    
    # Execute queries on all sessions concurrently
    async def execute_query(session, entity_name):
        async with session.begin():
            session.add(TestEntity(name=entity_name))
    
    # Run concurrent queries
    await asyncio.gather(*[
        execute_query(session, f"Pooled Entity {i}")
        for i, session in enumerate(sessions)
    ])
    
    # Cleanup sessions
    for session in sessions:
        await session.close()
    
    # Verify entities were created
    async with AsyncSession(bind=db_engine) as verify_session:
        result = await verify_session.execute(select(TestEntity))
        entities = result.scalars().all()
        
        entity_names = [entity.name for entity in entities]
        assert all(f"Pooled Entity {i}" in entity_names for i in range(5))
```

### 3. Service Methods Test (test_service_methods.py)

These tests verify that services correctly use provided sessions without managing transactions.

```python
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select
from unittest.mock import patch, AsyncMock
from tests.conftest import TestEntity

# Mock service class
class MockService:
    async def create_entity(self, session: AsyncSession, name: str):
        """Service method that accepts a session but doesn't manage transactions."""
        session.add(TestEntity(name=name))
        return True
    
    async def get_entity(self, session: AsyncSession, entity_id: int):
        """Service method that does a read operation."""
        result = await session.execute(
            select(TestEntity).where(TestEntity.id == entity_id)
        )
        return result.scalar_one_or_none()
    
    async def update_entity(self, session: AsyncSession, entity_id: int, new_name: str):
        """Service method that does an update operation."""
        entity = await self.get_entity(session, entity_id)
        if entity:
            entity.name = new_name
            return True
        return False

# Mock router using service
async def mock_router_with_service(session: AsyncSession):
    """Router that uses a service while owning transaction boundaries."""
    service = MockService()
    async with session.begin():
        await service.create_entity(session, "Service Test Entity")

@pytest.mark.asyncio
async def test_service_transaction_awareness(db_session):
    """Test that services correctly use provided sessions."""
    # Arrange
    service = MockService()
    
    # Act - Call service within a transaction
    async with db_session.begin():
        result = await service.create_entity(db_session, "Transaction Test")
    
    # Assert - Verify entity was created
    assert result is True
    
    result = await db_session.execute(select(TestEntity).where(TestEntity.name == "Transaction Test"))
    entity = result.scalar_one_or_none()
    assert entity is not None
    assert entity.name == "Transaction Test"

@pytest.mark.asyncio
async def test_service_does_not_commit(db_session):
    """Test that services don't commit transactions themselves."""
    # Arrange
    service = MockService()
    
    # Act - Call service without an outer transaction
    # This simulates a bug where someone might call a service without a transaction
    await service.create_entity(db_session, "No Transaction")
    
    # At this point, without an explicit commit, the entity shouldn't be committed
    # We'll fetch with a new session to ensure we're not seeing uncommitted changes
    async with AsyncSession(bind=db_session.bind) as new_session:
        result = await new_session.execute(
            select(TestEntity).where(TestEntity.name == "No Transaction")
        )
        entity = result.scalar_one_or_none()
    
    # Assert - Entity should not exist since there was no commit
    assert entity is None

@pytest.mark.asyncio
async def test_router_service_integration(db_session):
    """Test that routers and services work correctly together."""
    # Act - Call mock router that uses service
    await mock_router_with_service(db_session)
    
    # Assert - Verify entity was created
    result = await db_session.execute(
        select(TestEntity).where(TestEntity.name == "Service Test Entity")
    )
    entity = result.scalar_one_or_none()
    assert entity is not None
```

### 4. Background Tasks Test (test_background_tasks.py)

These tests verify that background tasks correctly create and manage their own sessions.

```python
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import select, text
from unittest.mock import patch, AsyncMock
from tests.conftest import TestEntity, Base

# Mock async session factory
async_session_factory = None

# Mock background task function
async def mock_background_task(data: str):
    """Background task that creates and manages its own session."""
    # Create a new session for the background task
    async with async_session_factory() as session:
        try:
            # Manage transaction explicitly
            async with session.begin():
                # Perform database operations
                session.add(TestEntity(name=f"Background: {data}"))
        except Exception as e:
            # Log error
            print(f"Error in background task: {str(e)}")
            # No need to rollback - the context manager will do it
            raise

# Mock background task that fails
async def mock_failing_background_task(data: str):
    """Background task that fails but properly manages its session."""
    async with async_session_factory() as session:
        try:
            async with session.begin():
                # Add entity
                session.add(TestEntity(name=f"Should Fail: {data}"))
                # Simulate failure
                raise ValueError("Simulated background task error")
        except Exception as e:
            # Log error but don't raise - this simulates error handling in background tasks
            print(f"Error in background task: {str(e)}")
            # Context manager will handle rollback

@pytest.fixture(scope="module")
async def setup_background_tests(db_engine):
    """Setup for background task tests."""
    global async_session_factory
    
    # Create tables if they don't exist
    async with db_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session factory
    async_session_factory = async_sessionmaker(
        db_engine, expire_on_commit=False, class_=AsyncSession
    )
    
    yield
    
    # Cleanup
    async with db_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.mark.asyncio
async def test_background_task_session_management(setup_background_tests, db_engine):
    """Test that background tasks correctly create and manage their own sessions."""
    # Act - Run background task
    await mock_background_task("test_data")
    
    # Assert - Verify entity was created
    # Use a new session to verify data was committed
    async with AsyncSession(bind=db_engine) as verify_session:
        result = await verify_session.execute(
            select(TestEntity).where(TestEntity.name == "Background: test_data")
        )
        entity = result.scalar_one_or_none()
        assert entity is not None

@pytest.mark.asyncio
async def test_background_task_error_handling(setup_background_tests, db_engine):
    """Test that background tasks properly handle errors and rollback transactions."""
    # Act - Run failing background task
    await mock_failing_background_task("test_error")
    
    # Assert - Verify no entity was created due to rollback
    async with AsyncSession(bind=db_engine) as verify_session:
        result = await verify_session.execute(
            select(TestEntity).where(TestEntity.name == "Should Fail: test_error")
        )
        entity = result.scalar_one_or_none()
        assert entity is None

@pytest.mark.asyncio
async def test_background_task_session_closure(db_engine):
    """Test that sessions are properly closed after background task completion."""
    # Use a mock to track session closure
    original_factory = async_session_factory
    
    mock_session = AsyncMock(spec=AsyncSession)
    mock_factory = AsyncMock(return_value=mock_session)
    
    # Configure mock session context manager behavior
    mock_session.__aenter__.return_value = mock_session
    mock_session.begin.return_value.__aenter__.return_value = None
    
    # Replace factory temporarily
    global async_session_factory
    async_session_factory = mock_factory
    
    # Act - Run background task with mock session
    await mock_background_task("closure_test")
    
    # Assert - Verify session was closed
    mock_session.close.assert_called_once()
    
    # Restore original factory
    async_session_factory = original_factory
```

## Running the Tests

1. **Run all tests**
   ```
   python -m pytest tests/db_patterns -v
   ```

2. **Run specific test category**
   ```
   python -m pytest tests/db_patterns/test_transaction_boundaries.py -v
   ```

3. **Run tests with coverage report**
   ```
   python -m pytest tests/db_patterns --cov=src --cov-report=term-missing
   ```

## Success Criteria

1. All tests should pass with no failures
2. The tests should verify:
   - Transaction boundaries are properly owned by routers
   - Transactions are committed on success and rolled back on failure
   - Services accept sessions but don't manage transactions
   - Background tasks create and manage their own sessions
   - Connection pooling works correctly
   - Error handling with appropriate transaction rollback

## Notes for Test Implementation

1. Use in-memory SQLite database for speed and isolation
2. Mock external dependencies to focus on database patterns
3. Test both success and failure scenarios for each pattern
4. Ensure each test is isolated from others to prevent test interdependence
5. Focus on verifying the database patterns, not business logic

## Integration with CI/CD

Add the following to your CI/CD workflow to run these tests automatically:

```yaml
- name: Run Database Pattern Tests
  run: |
    pip install pytest pytest-asyncio pytest-mock pytest-cov httpx
    python -m pytest tests/db_patterns -v --cov=src
```

This test suite will validate that the database access patterns we've established are working correctly and prevent future regressions.