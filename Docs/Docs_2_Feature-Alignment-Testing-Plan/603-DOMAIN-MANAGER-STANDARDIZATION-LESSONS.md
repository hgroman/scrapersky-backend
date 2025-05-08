# Domain Manager Standardization: Lessons Learned

## Overview

This document captures key lessons learned during the standardization of the Domain Manager component. These insights should be applied to the remaining components (DevTools and RBAC Permissions) to ensure consistent standardization across the ScraperSky backend.

## Architectural Lessons

### 1. Transaction Management Pattern

#### What We Did
- Implemented clear transaction boundaries in routers using `async with session.begin()` blocks
- Made service methods transaction-aware without managing transactions
- Added transaction state logging in services with `session.in_transaction()`
- Ensured background tasks create their own sessions and transactions

#### Key Insights
- **Router Responsibility**: Routers should explicitly create transaction boundaries and handle errors that might impact transaction completion
- **Nested Try/Except Blocks**: Using nested try/except blocks (one for RBAC, one for transaction) improves error handling clarity
- **Background Task Exception**: Background tasks are the only components that should manage their own transactions

#### Implementation Template
```python
# In routers:
try:
    # RBAC checks here

    try:
        async with session.begin():
            result = await service.method(session, params)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
except HTTPException:
    raise
except Exception as e:
    logger.error(f"Error: {str(e)}")
    raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")
```

### 2. RBAC Integration Pattern

#### What We Did
- Implemented four-layer RBAC checks for all endpoints
- Added clear documentation of permission requirements in docstrings
- Standardized RBAC error handling

#### Key Insights
- **Layer Order Matters**: The four layers should always be implemented in the same order:
  1. Basic permission check (`require_permission`)
  2. Feature enablement check (`require_feature_enabled`)
  3. Role level check (`require_role_level`)
  4. Tab permission check (`require_tab_permission`)
- **Tenant Context**: Always get tenant ID from user context first before RBAC checks
- **Error Propagation**: HTTPExceptions from RBAC checks should be propagated directly to preserve error codes

#### Implementation Template
```python
# Get tenant ID from user context
tenant_id = user_context_service.get_tenant_id(current_user)

# 1. Basic permission check
require_permission(current_user, "permission_name")

# 2. Feature enablement check
user_permissions = current_user.get("permissions", [])
await require_feature_enabled(
    tenant_id=tenant_id,
    feature_name="feature_name",
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
    tab_name="tab_name",
    feature_name="feature_name",
    session=session
)
```

### 3. Background Task Handling

#### What We Did
- Ensured background tasks create their own sessions and manage their own transactions
- Added clear documentation of background task session and transaction handling
- Implemented a standard pattern for detecting when to create sessions vs use existing ones

#### Key Insights
- **Session Creation Rule**: Background tasks should create new sessions if none are provided
- **Transaction Management Pattern**: Background tasks should manage their own transactions
- **Error Handling**: Errors in background tasks need separate session handling for status updates

#### Implementation Template
```python
async def process_background(params, session=None):
    # Create a new session if one wasn't provided
    own_session = session is None
    if own_session:
        logger.debug(f"Creating new session for background task")
        from ...db.session import async_session
        session_ctx = async_session()
    else:
        logger.debug(f"Using provided session for background task")
        session_ctx = session

    try:
        # Use the session as a context manager only if we created it
        if own_session:
            async with session_ctx as session_obj:
                # Ensure database operations are wrapped in a transaction
                async with session_obj.begin():
                    # Process with transaction
                    pass
        else:
            # Check if in transaction and create one if needed
            in_transaction = session_ctx.in_transaction()
            if not in_transaction:
                async with session_ctx.begin():
                    # Process with transaction
                    pass
            else:
                # Already in transaction
                pass

    except Exception as e:
        logger.error(f"Error in background task: {str(e)}")
        # Handle error - may need a new session for status updates
```

### 4. Error Handling Pattern

#### What We Did
- Implemented consistent error handling in routers
- Ensured HTTPExceptions are propagated directly
- Added proper logging at different error levels

#### Key Insights
- **Exception Specificity**: Use specific exceptions for different error types when possible
- **User-Friendly Messages**: Error messages in HTTPExceptions should be user-friendly
- **Detailed Logging**: Log detailed error information for debugging while keeping user messages simple
- **Transaction Handling**: Ensure exceptions don't leave transactions hanging

#### Implementation Template
```python
try:
    # Operation that might fail
except HTTPException:
    # Always propagate HTTP exceptions directly to preserve status codes
    raise
except ValueError as e:
    # Handle validation errors
    logger.error(f"Validation error: {str(e)}")
    raise HTTPException(status_code=400, detail=f"Invalid input: {str(e)}")
except Exception as e:
    # Handle unexpected errors
    logger.error(f"Unexpected error: {str(e)}")
    raise HTTPException(status_code=500, detail="An unexpected error occurred")
```

## Testing Lessons

### 1. Transaction Testing

#### What We Did
- Created tests that verify transaction boundaries are properly managed
- Tested transaction rollback on errors
- Verified services don't commit or rollback transactions

#### Key Insights
- **Mock Sessions**: Use AsyncMock for sessions with begin(), in_transaction(), etc.
- **Context Manager Testing**: Test both __aenter__ and __aexit__ paths
- **Verification Order**: Check transaction methods are called in the correct order

### 2. RBAC Testing

#### What We Did
- Created tests that verify all four layers of RBAC checks
- Tested RBAC failure paths
- Verified services are not called when RBAC checks fail

#### Key Insights
- **Mock All Layers**: Mock all four RBAC layers individually to test different failure scenarios
- **Order Testing**: Verify RBAC checks are called in the correct order
- **Failure Handling**: Test that service methods aren't called when RBAC checks fail

### 3. Error Handling Testing

#### What We Did
- Created tests for different error scenarios
- Tested proper conversion of errors to HTTPExceptions
- Verified error messages are appropriate

#### Key Insights
- **Error Simulation**: Mock services to raise different types of exceptions
- **Error Propagation**: Verify HTTPExceptions are propagated while other exceptions are converted
- **Status Code Testing**: Verify the correct HTTP status codes are used for different error types

## Documentation Lessons

### 1. Code Documentation

#### What We Did
- Added clear docstrings explaining transaction handling and RBAC requirements
- Documented method parameters, return values, and exceptions
- Added inline comments explaining complex operations

#### Key Insights
- **Transaction Documentation**: Always document transaction handling expectations in service methods
- **RBAC Requirements**: Document all four RBAC requirements in route docstrings
- **Background Task Documentation**: Clearly document session and transaction handling for background tasks

### 2. Report Documentation

#### What We Did
- Created a comprehensive standardization report
- Documented changes made, challenges faced, and solutions implemented
- Included key code patterns and examples

#### Key Insights
- **Pattern Documentation**: Document the architectural patterns implemented
- **Challenge Documentation**: Document challenges faced and how they were solved
- **Future Recommendations**: Include recommendations for future improvements

## Application to Remaining Components

When standardizing the remaining components (DevTools, RBAC Permissions), apply these lessons to ensure consistency:

1. **DevTools Standardization**:
   - Apply transaction boundaries to all endpoints that modify data
   - Add four-layer RBAC checks for all sensitive operations
   - Handle the unique challenge of DevTools often executing system commands
   - Ensure proper error handling and logging for system operations

2. **RBAC Permissions Standardization**:
   - Apply consistent transaction boundaries
   - Apply self-referential RBAC (permissions checking permissions)
   - Ensure clean error messages for permission failures
   - Implement thorough testing for complex permission scenarios

## Conclusion

These lessons learned provide a blueprint for standardizing the remaining components. By applying these patterns consistently, we'll ensure a coherent, maintainable, and secure architecture across the ScraperSky backend.

The standardization process has proven effective in improving code quality, enhancing security through consistent RBAC, ensuring data integrity with proper transaction handling, and making the codebase more maintainable through consistent patterns.
