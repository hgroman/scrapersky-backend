# Connection Pooling Standardization: Final Steps

## Objective

Complete the connection pooling standardization with minimal code changes to reach MVP. This represents the final step in our connection pooling work before moving to feature alignment.

## Current Status

The connection pooling implementation (document 90.9) made significant progress:
- URL modifier added to `engine.py`
- Engine creation updated to include Supavisor parameters
- Profile service updated to use raw SQL with parameters

The only remaining issue is simplifying how these parameters are applied consistently.

## Minimal Approach to Complete Implementation

### 1. Update Session Factory (Single Change)

Apply a single, focused change to `src/db/session.py`:

```python
# Add this to src/db/session.py where the async_session is created

# Update existing session factory to include Supavisor parameters
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    # Add this line to apply parameters by default
    execution_options={"postgresql_expert_mode": True}
)
```

This single change ensures all sessions created through the factory automatically include the Supavisor parameters, without complex parameter passing.

### 2. Verify with Existing Code (No Changes)

Test existing endpoints that use the session factory to confirm they work with the enhanced sessions. No further code changes should be needed.

### 3. Update Documentation

Update the README.md to include information about the automatic Supavisor parameter application.

## Why This Approach Avoids Scope Creep

1. **One Simple Change**: Only modifies one line in the session factory
2. **No New Files**: Doesn't create additional utility files or helpers
3. **No Service Rewrites**: Doesn't require rewriting existing services
4. **No Parameter Passing**: Eliminates complex parameter passing without new abstractions
5. **Backward Compatible**: Works with all existing code

## Testing Plan

Test existing endpoints that perform database operations to verify they work with the enhanced session factory:

1. **Profile Endpoint**: `/api/v3/profiles`
2. **Features Endpoint**: `/api/v3/features/`
3. **Domain Scanner**: `/api/v3/batch_page_scraper/scan`

## Success Criteria

1. All endpoints work properly with the enhanced session factory
2. No database connection errors in logs
3. Connection pooling parameters are properly applied

This minimal approach completes our connection pooling standardization without introducing new complexity. It represents the final step before moving to feature alignment (100.0) while ensuring we've addressed the database connectivity issues.