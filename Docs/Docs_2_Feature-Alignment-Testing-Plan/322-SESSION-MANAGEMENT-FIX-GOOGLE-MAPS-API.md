Session Management Fix: Google Maps API Endpoints README

## Issue Summary

We identified and fixed session management issues in the Google Maps API routes that were causing database errors, particularly in the `/staging` endpoint. The issue stemmed from inconsistent transaction management when calling service methods that interact with the database.

## What Was Fixed

The key issue was that some endpoints were passing session objects to service methods without wrapping those calls in proper transaction contexts (`async with session.begin():`). This was leading to session state issues and potentially causing the `_AsyncGeneratorContextManager` error.

Specifically, we added explicit transaction contexts to these endpoints:

1. `get_staging_places`: Added transaction around `PlacesService.get_places`
2. `update_place_status`: Added transaction around `PlacesService.update_status`
3. `batch_update_place_status`: Added transaction around multiple `PlacesService.update_status` calls

## Technical Details

### Problem Pattern

The problematic pattern looked like this:

```python
@router.get("/endpoint")
async def get_data(session: AsyncSession = Depends(get_session)):
    # Direct service call without transaction context
    result = await SomeService.some_method(session, other_args)
    return result
```

This can lead to issues because:

1. No explicit transaction boundary is defined
2. Error handling and rollback mechanism isn't clear
3. When multiple service calls are made, they may have inconsistent transaction states

### Fixed Pattern

The corrected pattern now looks like this:

```python
@router.get("/endpoint")
async def get_data(session: AsyncSession = Depends(get_session)):
    # Proper transaction context
    async with session.begin():
        result = await SomeService.some_method(session, other_args)
    return result
```

This ensures:

1. Clear transaction boundaries
2. Automatic rollback on exceptions
3. Consistent state across multiple database operations

## How to Identify Similar Issues

Look for these patterns in your code:

1. Router endpoints that directly call service methods with `session` parameter
2. Missing `async with session.begin():` blocks around database operations
3. Multiple database operations without an explicit transaction

## Best Practices for Session Management

1. **Always use transaction contexts**: Wrap service method calls that perform database operations in `async with session.begin():` blocks.

2. **Session dependency injection**: Continue using `Depends(get_session)` in FastAPI routes, but ensure proper transaction management within route handlers.

3. **Service method implementation**: Service methods should receive an active session and perform operations without managing transactions themselves (unless specifically designed to do so).

4. **Error handling**: Let the transaction context handle rollbacks automatically on exceptions rather than manually catching and rolling back.

## Example of Correct Session Usage

```python
# Router endpoint with proper session handling
@router.get("/items")
async def get_items(
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(user_dependency)
):
    # Permission checks
    require_permission(current_user, "items:view")

    # Feature checks
    await require_feature_enabled(
        tenant_id=current_user.get("tenant_id", "default"),
        feature_name="items_feature",
        session=session
    )

    try:
        # Database operations wrapped in transaction
        async with session.begin():
            items = await ItemService.get_items(
                session,
                tenant_id=current_user.get("tenant_id")
            )

        # Process results outside transaction if needed
        return {"items": items}

    except Exception as e:
        logger.error(f"Error in get_items: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving items: {str(e)}"
        )
```

## Testing Recommendations

1. Test all modified endpoints in staging environment
2. Monitor for session-related errors in logs
3. Verify that all CRUD operations work as expected
4. Check performance impact of explicit transactions (should be minimal)

## Affected Files

- `src/routers/google_maps_api.py`
  - Modified `get_staging_places`
  - Modified `update_place_status`
  - Modified `batch_update_place_status`
