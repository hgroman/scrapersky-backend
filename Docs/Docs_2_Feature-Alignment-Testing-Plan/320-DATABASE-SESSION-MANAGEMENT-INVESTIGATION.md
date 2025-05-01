# Database Session Management Investigation

## 1. Executive Summary

During the verification of authentication standardization, we identified critical database connectivity issues preventing proper API functionality. This document outlines our plan to investigate and resolve these SQLAlchemy session management problems, specifically the error: `_AsyncGeneratorContextManager' object has no attribute 'scalar'`, which indicates improper usage of AsyncSession objects and context managers in the codebase.

## 2. Problem Definition

### 2.1 Error Observation

All API tests that reached the database layer encountered the same error:

```
"_AsyncGeneratorContextManager' object has no attribute 'scalar'"
```

or:

```
"_AsyncGeneratorContextManager' object has no attribute 'execute'"
```

These errors occurred despite successful authentication, indicating a problem in the database session management code rather than in the authentication flow.

### 2.2 Technical Analysis

Based on the error message and standard patterns in SQLAlchemy 2.0, we can make several observations:

1. The error suggests that code is attempting to use an AsyncGeneratorContextManager (returned by `async with` expressions) as if it were the actual AsyncSession object
2. This likely indicates confusion between:
   - The context manager that wraps a session (`async with get_session() as session`)
   - The actual session object itself
3. The error is occurring when trying to call methods like `execute()` or `scalar()` on the context manager instead of on the actual session object

## 3. Investigation Plan

### 3.1 Code Review Focus Areas

1. **Database Session Factory**:

   - Examine `get_session()` implementation in `/src/db/session.py`
   - Verify it correctly returns AsyncSession objects
   - Check how it's setting up connection pooling with Supavisor

2. **Session Usage Patterns**:

   - Review how `AsyncSession` objects are used throughout the codebase
   - Identify patterns of incorrect usage (e.g., using context managers directly)
   - Look for inconsistencies in session handling

3. **Service Layer Database Access**:

   - Focus on the specific services used by Google Maps API routes:
     - `PlacesService`
     - `PlacesSearchService`
     - `PlacesStorageService`

4. **Transaction Management**:
   - Review transaction handling patterns
   - Check for proper usage of `async with session.begin()` blocks
   - Verify commit/rollback patterns

### 3.2 Specific Files to Examine

1. `/src/db/session.py` - Core session factory
2. `/src/services/places/places_service.py` - Place-related database operations
3. `/src/services/places/places_storage_service.py` - Storage operations for places
4. `/src/services/rbac/feature_service.py` - Where the current error is occurring
5. `/src/routers/google_maps_api.py` - Usage of database sessions in API routes

## 4. Implementation Approach

### 4.1 Diagnostic Strategy

1. **Create Database Session Diagnostic Tool**:

   ```python
   # Database session diagnostic script
   async def diagnose_session():
       session = await get_session()
       print(f"Session type: {type(session)}")
       try:
           result = await session.execute(text("SELECT 1"))
           print(f"Execute result: {result}")
           scalar = await result.scalar()
           print(f"Scalar result: {scalar}")
           return True
       except Exception as e:
           print(f"Error: {str(e)}")
           print(f"Error type: {type(e)}")
           return False
   ```

2. **Add Temporary Logging**:

   - Add DEBUG level logging around session creation
   - Log the type of session objects at critical points
   - Trace session lifecycle through transactions

3. **Create Isolated Test Cases**:
   - Small, isolated tests for session behavior
   - Tests that bypass the full API stack
   - Direct tests of session factory

### 4.2 Correction Strategy

Based on SQLAlchemy 2.0 best practices, we anticipate needing to:

1. **Update Session Factory**:

   - Ensure proper implementation of dependency injection pattern
   - Correctly handle async context management
   - Properly integrate with Supavisor connection pooling

2. **Fix Service Layer**:

   - Update service methods to correctly receive and use session objects
   - Ensure proper transaction management
   - Fix context management issues

3. **Standardize Session Usage Patterns**:
   - Create developer guidelines for session usage
   - Implement consistent patterns across all services
   - Provide examples of correct usage

## 5. SQLAlchemy 2.0 Async Best Practices

To guide our corrections, we'll follow these SQLAlchemy 2.0 async best practices:

### 5.1 Session Creation and Usage

```python
# Correct pattern for dependency injection
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    engine = get_engine()
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session

# Correct usage in FastAPI endpoint
@app.get("/items/{item_id}")
async def get_item(item_id: int, session: AsyncSession = Depends(get_session)):
    stmt = select(Item).where(Item.id == item_id)
    result = await session.execute(stmt)
    item = result.scalar_one_or_none()
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item
```

### 5.2 Transaction Management

```python
# Correct transaction management
async def create_item(session: AsyncSession, item_data: dict):
    async with session.begin():
        item = Item(**item_data)
        session.add(item)
        # Commit happens automatically at the end of the context manager
    return item
```

## 6. Implementation Plan

### 6.1 Phase 1: Analysis and Diagnosis

1. Create and run diagnostic tests to confirm the nature of the issue
2. Review all database session usage patterns in the codebase
3. Identify the specific points of failure in session management
4. Develop a detailed fix approach based on findings

### 6.2 Phase 2: Implementation

1. Update the database session factory if needed
2. Fix the specific service methods where errors are occurring
3. Apply consistent session management patterns across services
4. Implement proper transaction handling

### 6.3 Phase 3: Testing

1. Create tests to verify session management works correctly
2. Test all API endpoints with database operations
3. Verify transaction handling with complex operations
4. Ensure compatibility with Supavisor connection pooling

## 7. Next Steps

1. **Immediate Actions**:

   - Set up database session diagnostic tools
   - Review core session factory code
   - Examine the specific error location in `feature_service.py`

2. **Key Questions to Answer**:

   - Is the session factory returning the correct object type?
   - Are services properly extracting the session from the context manager?
   - Is there a pattern of misuse across multiple services?
   - Is Supavisor connection pooling properly configured?

3. **Expected Outcomes**:
   - Identified root cause of session management issues
   - Clear understanding of required fixes
   - Plan for implementing corrections consistently across the codebase

## 8. Conclusion

The database session management issues must be resolved to enable proper functionality of the API endpoints. With a systematic investigation and correction approach following SQLAlchemy 2.0 best practices, we can restore proper database connectivity while ensuring consistent patterns for future development.
