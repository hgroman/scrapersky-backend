# Error Service Consolidation Plan

## Current Usage

After scanning the codebase, we found these files are using error service implementations:

1. **Using services/error/error_service.py (RECOMMENDED):**
   - src/routers/sitemap_analyzer.py
   - src/services/places/places_search_service.py

2. **Using services/core/error_service.py (DUPLICATE):**
   - Not directly imported by any router file
   - May be imported through core/__init__.py

3. **Using services/new/error_service.py (DUPLICATE):**
   - Not directly imported by any router file
   - May be imported through new/__init__.py

## Consolidation Action Plan

We'll standardize on `services/error/error_service.py` as it's:
- The most comprehensive implementation
- Already in use by production code (sitemap_analyzer.py)
- Has better PostgreSQL error handling
- Includes a route_error_handler for wrapping routers

### 1. Keep Primary Implementation:
- Keep `src/services/error/error_service.py`
- Keep `src/services/error/__init__.py` (imports the service for easier importing)

### 2. Add Router Error Handler to Main App:
In `src/main.py`, we should add the route_error_handler from error_service to each router registration:

```python
# Import the error service
from src.services.error.error_service import ErrorService, error_service

# When registering routers, add error handling
app.include_router(ErrorService.route_error_handler(router))
```

### 3. Check for Missing Imports:
We should check if any router files aren't properly importing the error service.

## Testing Impact
Since we're not removing any existing implementations yet, this change has minimal impact. We're only standardizing for new development.

## Follow-up Tasks
After confirming this works, we can:
1. Add error handling to all router files
2. Make sure background tasks have proper error handling
3. Remove the duplicate implementations

## Risk Assessment
- Risk: LOW
- Impact of failure: LOW (since we're not removing existing code yet)
- Testability: HIGH (error handling can be tested by introducing intentional errors)
