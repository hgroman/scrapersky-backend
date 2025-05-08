# Domain Manager Standardization Report

## Overview

This report documents the standardization work performed on the Domain Manager component of the ScraperSky backend. The goal was to ensure this component follows the same architectural patterns established in the reference implementation (Google Maps API), particularly regarding transaction management, RBAC integration, error handling, and background task handling.

## Component Files

The primary files involved in this standardization effort were:

1. `/src/routers/modernized_sitemap.py` - Router handling domain scanning endpoints
2. `/src/services/domain_service.py` - Service for domain management operations
3. `/src/services/sitemap/processing_service.py` - Service for sitemap processing
4. `/tests/transaction/test_transaction_domain_manager.py` - Tests for transaction and RBAC

## Changes Made

### 1. Router Updates

#### Transaction Management

- Ensured all endpoints consistently use `async with session.begin()` to own transaction boundaries
- Added proper error handling with try/except blocks that preserve transaction integrity
- Ensured clean conversion of service-level errors to HTTPExceptions

#### RBAC Integration

- Implemented four-layer RBAC checks for all endpoints:
  - Basic permission: "access_sitemap_scanner"
  - Feature flag: "sitemap_analyzer"
  - Role level check: Minimum USER role required
  - Tab permission: "discovery-scan" for feature "sitemap_analyzer"
- Added clear documentation of permission requirements in docstrings

#### Background Task Handling

- Ensured proper background task pattern where tasks create their own sessions
- Added clear documentation of background task session and transaction handling

### 2. Service Updates

#### Transaction Awareness

- Made all service methods transaction-aware with `session.in_transaction()` checks
- Added transaction state logging
- Removed any transaction management (commits/rollbacks) from service layer
- Ensured background task methods properly create their own sessions and manage their own transactions

#### Documentation

- Added clear documentation indicating transaction awareness requirements
- Updated method docstrings to explain transaction handling

### 3. Testing

- Created comprehensive test cases for transaction boundaries
- Added tests for four-layer RBAC checks
- Added tests for error handling scenarios
- Verified background task behavior

## Architectural Patterns Implemented

### 1. Router-Owned Transaction Boundaries

```python
try:
    async with session.begin():
        result = await service.method(session, params)
    return result
except HTTPException:
    raise
except Exception as e:
    logger.error(f"Error: {str(e)}")
    raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
```

### 2. Four-Layer RBAC Integration

```python
# 1. Basic permission check
require_permission(current_user, "access_sitemap_scanner")

# 2. Feature enablement check
await require_feature_enabled(
    tenant_id=tenant_id, 
    feature_name="sitemap_analyzer", 
    session=session,
    user_permissions=user_permissions
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
    feature_name="sitemap_analyzer",
    session=session
)
```

### 3. Service Transaction Awareness

```python
# Check if in transaction
in_transaction = session.in_transaction()
logger.debug(f"Method transaction state: {in_transaction}")

if not in_transaction:
    logger.warning("Method called without transaction; router should handle transactions")
```

### 4. Background Task Pattern

```python
async def _process_domain(...):
    # Create a new session for this background task
    own_session = session is None
    if own_session:
        session_ctx = async_session()
        async with session_ctx as session_obj:
            async with session_obj.begin():
                # Process with transaction
    else:
        # Use existing session
```

## Challenges and Solutions

### 1. Legacy Code Integration

**Challenge**: The component included legacy database access patterns using raw SQL.

**Solution**: We kept the existing patterns functional but added transaction awareness to ensure they operate correctly within the new architecture. Future work should replace these with standard ORM operations.

### 2. Background Task Complexity

**Challenge**: Background tasks require careful handling of session creation and transaction management.

**Solution**: We implemented a clear pattern that distinguishes between router-provided sessions and self-created sessions, with proper transaction handling in both cases.

### 3. RBAC Integration

**Challenge**: Ensuring all four layers of RBAC checks are consistently applied.

**Solution**: We implemented a standard pattern for all endpoints with clear ordering and error handling.

## Test Coverage

The standardization includes comprehensive test coverage for:

- Transaction boundary management
- Four-layer RBAC checks
- Error handling
- Background task behavior

## Conclusion

The Domain Manager component has been successfully standardized to follow the architectural patterns established in the reference implementation. All endpoints now have proper transaction boundaries, consistent RBAC integration, and standardized error handling. The services are transaction-aware without managing transactions. Background tasks correctly create their own sessions and transactions.

This standardization improves code consistency, maintainability, and security across the ScraperSky backend.