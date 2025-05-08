# 1.6: Transaction Management Testing Plan

## Overview

This document outlines a comprehensive testing strategy to verify the effectiveness of transaction management fixes implemented across the ScraperSky backend. The fixes follow our architectural principle: "Routers own transaction boundaries, services do not."

The test plan focuses on validating that transaction management is working correctly within router-service interactions, with particular attention to edge cases and concurrent operations.

## Test Categories

We will organize our tests into the following categories:

### 1. Basic Transaction Pattern Validation

These tests verify that our basic architectural pattern is correctly implemented:

- **Pattern Adherence Tests**: Verify routers do not start transactions that wrap service calls
- **Session Passing Tests**: Verify session objects are correctly passed to services
- **Service Transaction Tests**: Verify services can start their own transactions

### 2. Error Handling Tests

These tests verify correct behavior in error conditions:

- **Service Exception Tests**: Verify that exceptions in services are properly propagated
- **Transaction Rollback Tests**: Verify that changes are rolled back when errors occur
- **Partial Failure Tests**: Verify behavior when some operations succeed but others fail

### 3. Concurrency Tests

These tests verify correct behavior during concurrent operations:

- **Parallel Request Tests**: Verify multiple simultaneous requests handle transactions correctly
- **Database Lock Tests**: Verify proper handling of row/table locks
- **Transaction Isolation Tests**: Verify that transactions maintain proper isolation levels

### 4. Integration Tests

These tests verify end-to-end functionality:

- **Router-Service Integration Tests**: Verify complete request flows from router to service and database
- **Multi-Component Tests**: Test interactions between multiple routers and services
- **Cross-Functional Tests**: Test sequences of related operations that should be atomic

## Test Implementation Approach

We'll implement these tests using pytest with a focus on:

1. **Dependency Injection**: Custom fixture to provide test sessions
2. **Mocking**: Use unittest.mock to verify transaction behavior when needed
3. **Database State Verification**: Assertions to verify database state before and after operations
4. **Exception Handling**: Tests for expected exception propagation
5. **Asynchronous Testing**: Proper use of pytest-asyncio for async tests

## Test Structure

Each test file will be organized as:

```python
# test_transaction_[component].py

import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

# Fixtures
@pytest.fixture
async def mock_session():
    # Create a mock session with transaction capabilities
    session = MagicMock(spec=AsyncSession)
    session.begin.return_value.__aenter__.return_value = None
    session.execute.return_value = MagicMock()
    session.commit = MagicMock()
    session.rollback = MagicMock()
    return session

# Basic Pattern Tests
async def test_router_does_not_start_transaction(mock_session):
    # Test that router doesn't start transaction before calling service
    ...

# Error Handling Tests
async def test_service_exception_propagates(mock_session):
    # Test that exceptions in service are properly propagated
    ...

# Concurrency Tests
async def test_parallel_requests(mock_session):
    # Test multiple simultaneous requests
    ...

# Integration Tests
async def test_complete_request_flow(mock_session):
    # Test complete request flow
    ...
```

## Test Matrix

We will develop specific tests for each of the router files that received transaction management fixes:

| Router File | Basic Pattern | Error Handling | Concurrency | Integration |
|-------------|---------------|----------------|-------------|-------------|
| rbac_features.py | 3 tests | 2 tests | 1 test | 1 test |
| rbac_admin.py | 4 tests | 3 tests | 2 tests | 1 test |
| rbac_permissions.py | 7 tests | 5 tests | 3 tests | 2 tests |
| batch_page_scraper.py | 4 tests | 3 tests | 2 tests | 1 test |
| dev_tools.py | 1 test | 1 test | N/A | 1 test |

## Specific Test Cases

### RBAC Features Router Tests

1. **Test update_tenant_feature does not start transaction**
2. **Test service transaction isolation in feature operations**
3. **Test exception handling in feature updates**
4. **Test concurrent feature flag updates**

### RBAC Admin Router Tests

1. **Test dashboard stats retrieve without transaction wrapper**
2. **Test profiles endpoint session passing**
3. **Test tenants listing without transaction**
4. **Test roles management error propagation**
5. **Test concurrent admin operations**

### RBAC Permissions Router Tests

1. **Test permission creation without router transaction**
2. **Test permission assignment session passing**
3. **Test role-permission operations transaction isolation**
4. **Test exception handling in permission operations**
5. **Test concurrent permission modifications**

### Batch Page Scraper Router Tests

1. **Test scan domain operation session passing**
2. **Test batch operations transaction isolation**
3. **Test error handling in batch processing**
4. **Test concurrent batch operations**

### Dev Tools Router Tests

1. **Test setup_sidebar transaction management**
2. **Test sidebar setup error handling**

## Mocking Strategy

For testing transaction management specifically, we'll use a combination of:

1. **Session Mocks**: Replace real AsyncSession with a mock that allows spying on transaction operations
2. **Service Mocks**: Where appropriate, replace service implementations to control transaction behavior
3. **Database Operation Mocks**: Abstract actual database operations to focus on transaction boundaries

## Expected Test Results

Successful tests will demonstrate:

1. Routers never start transactions that wrap service calls
2. Services receive valid session objects to manage their own transactions
3. Exceptions within service transactions are properly propagated
4. Transaction rollbacks occur correctly on errors
5. Concurrent operations maintain proper isolation

## Implementation Plan

1. Create base test fixtures for transaction testing
2. Implement component-specific test cases
3. Create integration tests for end-to-end flows
4. Run tests with coverage reporting to ensure completeness
5. Document any remaining edge cases or areas for improvement

This test plan will provide comprehensive validation of our transaction management architecture and ensures the fixes we've implemented are working as expected.
