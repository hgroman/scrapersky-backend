# Domain Manager Standardization Plan

## Component Overview

The Domain Manager component consists of several related files that manage domain records, metadata, and sitemap operations. The primary files involved are:

1. `/src/routers/modernized_sitemap.py` - Router handling domain scanning endpoints
2. `/src/services/domain_service.py` - Service for domain management operations
3. `/src/services/sitemap/processing_service.py` - Service for sitemap processing
4. `/src/db/sitemap_handler_fixed.py` - Low-level database operations (legacy)

## Current Status

The Domain Manager component currently has:

- Partial implementation of transaction boundaries in modernized_sitemap.py
- Limited RBAC integration with only basic permission checks
- Inconsistent error handling patterns
- Service layer with partial transaction awareness
- Mixture of raw SQL queries and ORM operations
- Background task implementation that lacks proper session management

## Standardization Requirements

Based on our reference implementation (Google Maps API), the Domain Manager component needs:

1. **Transaction Management**
   - Router methods must own transaction boundaries with `async with session.begin()`
   - Service methods must be transaction-aware but not manage transactions
   - Background tasks must create own sessions and manage own transactions

2. **RBAC Integration**
   - Four-layer RBAC checks for all endpoints:
     - Basic permission check
     - Feature enablement check
     - Role level check
     - Tab permission check

3. **Service Modularization**
   - Clearly separate responsibilities between layers
   - Remove business logic from routers
   - Proper logging and error handling

4. **Error Handling**
   - Consistent error handling patterns
   - Proper HTTP exception handling
   - Informative error messages

## Implementation Plan

### 1. Router Updates - modernized_sitemap.py

- Update all endpoints with explicit transaction boundaries
- Implement four-layer RBAC checks for all endpoints
- Standardize error handling
- Update docstrings with permission requirements
- Update background task handling to follow standard pattern

### 2. Service Updates - domain_service.py

- Make all methods transaction-aware with proper logging
- Remove any transaction management (commits/rollbacks)
- Add transaction state checking with `session.in_transaction()`
- Standardize error handling
- Ensure all methods follow the service pattern

### 3. Service Updates - sitemap/processing_service.py

- Make all methods transaction-aware
- Update background tasks to create own sessions
- Implement proper error handling
- Standardize method interfaces

### 4. Legacy Code - sitemap_handler_fixed.py

- Identify functionality that can be refactored to use ORM
- Mark deprecated methods with clear documentation
- Create standardized alternatives for used functionality

### 5. Tests

- Create transaction tests for all router endpoints
- Create RBAC tests for all permission layers
- Create service unit tests
- Include test for background task behavior

## Test Cases

1. **Router Transaction Tests**
   - Verify transaction boundaries are properly managed
   - Test transaction rollback on errors
   - Verify background tasks are correctly dispatched

2. **RBAC Tests**
   - Test all four layers of RBAC checks
   - Verify proper error messages on permission denial

3. **Service Tests**
   - Test transaction awareness
   - Verify service behavior within and outside transactions
   - Test error handling and logging

## Expected Deliverables

1. Updated router implementation
2. Updated service implementations
3. New test files
4. Standardization report documenting changes
5. Updated progress tracking document

## Potential Challenges

1. **Legacy Integration**: The component uses a mix of raw SQL and ORM approaches, which may complicate standardization.
2. **Background Task Complexity**: The background tasks need careful handling to ensure proper session management.
3. **Error Handling**: The current error handling pattern is inconsistent and needs standardization.

## Success Criteria

The Domain Manager component standardization will be considered successful when:

1. All endpoints follow the router-owned transaction boundary pattern
2. All service methods are transaction-aware without managing transactions
3. Four-layer RBAC checks are implemented for all endpoints
4. Background tasks correctly create and manage their own sessions
5. All tests pass
6. Error handling is consistent and follows the standard pattern
