# Transaction Management Fix Plan - Part 2: ActionQueue and ContentMap

This document outlines the transaction management fixes required for the ActionQueue and ContentMap components of ScraperSky backend, in compliance with the architectural pattern: "Routers own transaction boundaries, services do not."

## 1. ActionQueue Component

### Files to Modify:

1. `/src/services/job_service.py`
2. `/src/routers/google_maps_api.py` (uses job_service)

### Issues to Address:

#### In `job_service.py`:

- The `JobService` class uses the `@managed_transaction` decorator on several methods, which is not consistent with our "services don't own transaction boundaries" pattern.
- Methods need to be refactored to be transaction-aware but not create/manage transactions directly.

#### In `google_maps_api.py`:

- The router properly manages transactions in some places, but there may be inconsistencies in how it calls job_service methods that have the `@managed_transaction` decorator.

### Fixes Required:

1. **In `job_service.py`:**
   - Add transaction state awareness to methods
   - Remove `@managed_transaction` decorators that manage transaction boundaries
   - Ensure methods check transaction state
   - Split complex methods into smaller, transaction-aware components

2. **In `google_maps_api.py`:**
   - Ensure router methods properly wrap service calls with transaction context
   - Use session.begin() blocks consistently
   - Background tasks should create their own session and transactions

## 2. ContentMap Component

### Files to Modify:

1. `/src/routers/modernized_sitemap.py`
2. `/src/services/sitemap/sitemap_service.py` 
3. `/src/services/sitemap/processing_service.py`

### Issues to Address:

#### In `modernized_sitemap.py`:

- Router properly manages transactions for some operations, but there may be inconsistencies.
- Need to ensure all service calls are properly wrapped in transaction contexts.

#### In `sitemap_service.py`:

- The service assumes it's being called within an active transaction in some places but doesn't check.
- Need to add transaction state checking.

#### In `processing_service.py`:

- Background processing task manages its own transactions, which should be kept.
- Direct service methods should be transaction-aware but not control transactions.

### Fixes Required:

1. **In `modernized_sitemap.py`:**
   - Ensure all service calls are properly wrapped in transaction contexts
   - Use session.begin() blocks consistently

2. **In `sitemap_service.py`:**
   - Add transaction state checking
   - Document transaction requirements in docstrings
   - Ensure methods don't create their own transactions

3. **In `processing_service.py`:**
   - Add transaction state awareness
   - Ensure methods don't create transactions unless explicitly for background tasks

## 3. Test Files to Create

1. `/tests/transaction/test_transaction_actionqueue.py`
   - Test `job_service.py` transaction awareness
   - Test router transaction boundary ownership
   - Mock session and verify transaction behaviors

2. `/tests/transaction/test_transaction_contentmap.py`
   - Test `sitemap_service.py` transaction awareness
   - Test `processing_service.py` transaction awareness
   - Test router transaction boundary ownership
   - Mock session and verify transaction behaviors

## General Fix Pattern

For all files:

1. Add transaction state checking:
```python
in_transaction = session.in_transaction()
logger.debug(f"Session transaction state in {method_name}: {in_transaction}")
```

2. Document transaction requirements:
```python
"""
This method should be called within an active transaction.
The transaction is managed by the router, not by this service.
"""
```

3. Split complex methods:
```python
async def complex_method(self, session, ...):
    # Check transaction state
    in_transaction = session.in_transaction()
    
    if in_transaction:
        # Use existing transaction
        return await self._internal_complex_method(session, ...)
    else:
        # Let caller know they should provide a transaction
        logger.warning("Method called without transaction context")
        raise ValueError("This method should be called within an active transaction")
        
async def _internal_complex_method(self, session, ...):
    # Implementation that assumes transaction exists
    ...
```

## Implementation Order

1. Implement changes to `job_service.py` first
2. Implement changes to `google_maps_api.py`
3. Implement changes to sitemap services
4. Implement changes to sitemap routers
5. Create test files

Each change should follow the pattern established in the FrontendScout, EmailHunter, and SocialRadar fixes:
- Make services transaction-aware but not transaction-controlling
- Ensure routers own transaction boundaries
- Add appropriate logging and error handling