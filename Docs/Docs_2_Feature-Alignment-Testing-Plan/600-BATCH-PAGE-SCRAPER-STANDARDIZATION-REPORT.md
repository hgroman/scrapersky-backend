# Batch Page Scraper Component Standardization Report

## Overview

This document provides a comprehensive summary of the standardization work performed on the Batch Page Scraper component of the ScraperSky backend. The standardization follows the reference implementation demonstrated in the Google Maps API component, ensuring consistent transaction boundaries, proper RBAC integration, and standardized error handling across all routes.

## Context and Requirements

The standardization followed these key requirements:

1. **Router Owns Transaction Boundaries**: Ensuring routers explicitly manage transaction boundaries using `async with session.begin():` while services are transaction-aware but don't create, commit, or rollback transactions.

2. **Four-Layer RBAC Integration**: Implementing all four permission check layers in the correct order:
   - Basic Permission Check (synchronous)
   - Feature Enablement Check (async)
   - Role Level Check (async)
   - Tab Permission Check (async, where applicable)

3. **Service Transaction Awareness**: Making service methods check for transaction state and log warnings if not in transaction, but never managing transactions directly.

4. **Standardized Error Handling**: Using consistent try/except patterns to convert errors to proper HTTPExceptions.

5. **Background Task Implementation**: Ensuring background tasks create their own sessions and manage their own transactions.

## Files Modified

1. **Router Implementation**:
   - `/src/routers/batch_page_scraper.py` - Updated to follow standardized patterns

2. **Service Implementation**:
   - `/src/services/page_scraper/processing_service.py` - Made properly transaction-aware

3. **Tests**:
   - `/tests/transaction/test_transaction_batch_page_scraper.py` - Updated to verify new patterns

## Detailed Changes

### 1. Router Changes (`batch_page_scraper.py`)

#### 1.1 Import Changes

Added imports for RBAC utilities and constants:

```python
from ..utils.permissions import (
    require_permission,
    require_feature_enabled,
    require_role_level,
    require_tab_permission
)
from ..constants.rbac import ROLE_HIERARCHY
```

Updated session import:

```python
from ..session.async_session import get_session, async_session_factory
```

#### 1.2 Four-Layer RBAC Integration

Implemented all four layers of RBAC checks in each route:

```python
# 1. Basic permission check
require_permission(current_user, "domain:scan")

# 2. Feature enablement check
await require_feature_enabled(
    tenant_id=tenant_id,
    feature_name="batch_page_scraper",
    session=session,
    user_permissions=current_user.get("permissions", [])
)

# 3. Role level check
await require_role_level(
    user=current_user,
    required_role_id=ROLE_HIERARCHY["USER"],
    session=session
)

# 4. Tab permission check
await require_tab_permission(
    user=current_user,
    tab_name="discovery-scan",
    feature_name="batch_page_scraper",
    session=session
)
```

#### 1.3 Transaction Boundary Management

Added explicit transaction boundaries to all routes:

```python
# Router owns the transaction boundary
async with session.begin():
    # Process the domain scan through the page processing service
    result = await page_processing_service.initiate_domain_scan(
        session=session,
        # Other parameters...
    )
```

#### 1.4 Error Handling

Implemented standardized error handling pattern:

```python
try:
    # Router owns the transaction boundary
    async with session.begin():
        # Service call...

    # Return response
    return response_model

except HTTPException:
    # Re-raise HTTP exceptions as-is
    raise
except Exception as e:
    logger.error(f"Error message: {str(e)}")
    raise HTTPException(status_code=500, detail=f"Error message: {str(e)}")
```

#### 1.5 Background Task Implementation

Updated background tasks to create their own sessions and manage their own transactions:

```python
async def process_domain_background():
    # IMPORTANT: Always create a new session for background tasks
    async with async_session_factory() as bg_session:
        try:
            # Always create a new transaction for background tasks
            async with bg_session.begin():
                await batch_processor_service.process_domains_batch(
                    # Parameters...
                )
        except Exception as e:
            logger.error(f"Error in background processing: {str(e)}")
```

#### 1.6 Docstring Documentation

Enhanced docstrings to document permission requirements:

```python
"""
Scan a domain to extract metadata from its pages.

Permissions required:
- domain:scan permission
- batch_page_scraper feature enabled
- USER role or higher
- discovery-scan tab access
"""
```

### 2. Service Changes (`processing_service.py`)

#### 2.1 Transaction Awareness

Made service methods check and log transaction state:

```python
async def initiate_domain_scan(self, session: AsyncSession, ...):
    # Check if in transaction
    in_transaction = session.in_transaction()
    logger.debug(f"initiate_domain_scan transaction state: {in_transaction}")

    if not in_transaction:
        logger.warning("initiate_domain_scan called without an active transaction; the router should handle transactions")
```

#### 2.2 Exception Propagation

Updated error handling to propagate errors to the router:

```python
try:
    # Implementation
    return result
except Exception as e:
    logger.error(f"Error in service method: {str(e)}")
    # Let the exception propagate to the router
    raise
```

#### 2.3 Service Documentation

Updated docstrings to indicate transaction awareness:

```python
"""
This method is transaction-aware but does not manage transactions.
Transaction boundaries should be managed by the router.
"""
```

### 3. Test Changes (`test_transaction_batch_page_scraper.py`)

#### 3.1 Transaction Boundary Tests

Added tests to verify router-owned transaction boundaries:

```python
@pytest.mark.asyncio
async def test_scan_domain_uses_transaction(mock_session, ...):
    # Test implementation...

    # Assert session.begin() WAS called by the router (owns transaction boundary)
    mock_session.begin.assert_called_once()

    # Assert transaction context was entered
    mock_session.begin.return_value.__aenter__.assert_called_once()
```

#### 3.2 RBAC Integration Tests

Added tests to verify all four layers of RBAC checks:

```python
@pytest.mark.asyncio
async def test_batch_scan_domains_uses_proper_rbac_checks(mock_session, ...):
    # Test implementation...

    # Assert all RBAC checks were called in the correct order
    mock_rbac_checks['require_permission'].assert_called_once()
    mock_rbac_checks['require_feature_enabled'].assert_called_once()
    mock_rbac_checks['require_role_level'].assert_called_once()
    mock_rbac_checks['require_tab_permission'].assert_called_once()
```

#### 3.3 Service Transaction Awareness Tests

Added tests to verify service transaction awareness:

```python
@pytest.mark.asyncio
async def test_service_transaction_awareness():
    # Test implementation...

    # Check that in_transaction was called (transaction awareness)
    mock_session.in_transaction.assert_called()

    # Check that commit/rollback were NOT called (router should handle this)
    assert not mock_commit.called
    assert not mock_rollback.called
```

#### 3.4 Background Task Tests

Added tests to verify background tasks create their own sessions:

```python
@pytest.mark.asyncio
async def test_background_task_creates_own_session(mock_session, ...):
    # Test implementation...

    # Check that background task does not receive the request session
    for arg in mock_background_tasks.add_task.call_args[0]:
        assert arg != mock_session
```

## Key Architectural Patterns Implemented

1. **Router-Owned Transaction Boundaries**:
   - All routes now use `async with session.begin():` to own the transaction boundary
   - Error handling consistently propagates errors up the stack
   - Background tasks create their own sessions and transactions

2. **Four-Layer RBAC Integration**:
   - Basic permission checks with `require_permission`
   - Feature enablement checks with `require_feature_enabled`
   - Role level checks with `require_role_level`
   - Tab permission checks with `require_tab_permission`

3. **Service Transaction Awareness**:
   - Services check `session.in_transaction()` but don't manage transactions
   - Services propagate errors for routers to handle
   - Methods document transaction awareness in docstrings

4. **Standardized Error Handling**:
   - Consistent error wrapping with proper HTTP status codes
   - HTTPExceptions are re-raised, other exceptions are wrapped
   - Detailed logging with error context

## Testing Strategy

The testing approach verifies:

1. **Transaction Boundary Ownership**:
   - Tests that routers start transactions
   - Tests that transactions are used around service calls
   - Tests that background tasks create their own sessions

2. **RBAC Implementation**:
   - Tests that all RBAC checks are called in the correct order
   - Tests that appropriate role levels are required for different operations
   - Tests that RBAC checks happen before transaction boundaries

3. **Error Handling**:
   - Tests that errors from services are properly converted to HTTPExceptions
   - Tests that HTTPExceptions are re-raised as-is

4. **Service Transaction Awareness**:
   - Tests that services check transaction state
   - Tests that services don't call commit or rollback

## Challenges and Solutions

1. **Challenge**: Converting existing background task pattern to create its own sessions
   **Solution**: Added explicit session creation with `async_session_factory()` in background tasks

2. **Challenge**: Maintaining the right feature flag and tab permission mappings
   **Solution**: Used the RBAC constants and feature maps to ensure consistent naming

3. **Challenge**: Adapting the existing error handling approach to the standard pattern
   **Solution**: Restructured error handling to re-raise HTTPExceptions and wrap other exceptions

## Next Steps

The Batch Page Scraper component is now fully standardized according to the reference implementation. Lessons learned from this standardization can be applied to the remaining components:

1. Domain Manager Component
2. DevTools Component

## Conclusion

The standardization of the Batch Page Scraper component has successfully implemented the architectural patterns from the reference implementation. The component now follows consistent transaction management patterns, has proper RBAC integration at all four layers, and handles errors in a standardized way. This effort serves as a template for standardizing other components in the ScraperSky backend.
