# Complete ErrorService Removal Plan

## Date: 2025-03-24

## Objective

Completely remove all instances of the custom ErrorService implementation from the ScraperSky backend and ensure all routes and services use FastAPI's native error handling mechanisms.

## Methodology

We will use a combination of tools to systematically identify and remove all ErrorService implementations:

1. **Ruff** for code analysis and automatic fixes where possible
2. **Grep** for comprehensive search to ensure nothing is missed
3. **Manual verification** of critical endpoints after changes

## Work Order

### Phase 1: Comprehensive Analysis

1. Use Ruff to identify all imports of ErrorService

   ```bash
   cd .
   ruff check --select=F401 src/ | grep "ErrorService"
   ```

2. Use Grep to find all instances of ErrorService usage

   ```bash
   grep -r "ErrorService" src/
   grep -r "error_service" src/
   grep -r "route_error_handler" src/
   grep -r "async_exception_handler" src/
   grep -r "exception_handler" src/
   ```

3. Create a comprehensive list of all files that need modification

### Phase 2: Router Modifications

1. Update all router registrations in main.py (COMPLETED)

   - Remove all instances of ErrorService.route_error_handler
   - Use direct router registration

2. Check for any additional router registration patterns in other files

   ```bash
   grep -r "include_router" --include="*.py" src/
   ```

3. Update any additional router registrations found

### Phase 3: Service Layer Modifications

1. Identify all service files that might use ErrorService

   ```bash
   grep -r "from.*error_service" --include="*.py" src/
   ```

2. Remove ErrorService usage from all service files
   - Replace with FastAPI's native error handling where needed
   - Remove unnecessary try/except blocks designed for ErrorService

### Phase 4: Remove Decorator Usage

1. Find all instances of decorator usage

   ```bash
   grep -r "@.*error.*service" --include="*.py" src/
   grep -r "@.*exception.*handler" --include="*.py" src/
   ```

2. Remove or replace decorators with FastAPI equivalents

### Phase 5: Add FastAPI Exception Handlers

1. Add global exception handlers in main.py for custom exceptions
   ```python
   @app.exception_handler(CustomException)
   async def custom_exception_handler(request, exc):
       return JSONResponse(
           status_code=exc.status_code,
           content={"message": exc.detail}
       )
   ```

### Phase 6: Testing and Verification

1. Restart Docker container after each major change

   ```bash
   docker-compose restart
   ```

2. Test critical endpoints to ensure they work correctly

   - `/api/v3/sitemap/scan`
   - Other key endpoints

3. Verify error responses are properly formatted

### Phase 7: Final Cleanup

1. Remove the ErrorService implementation file

   ```bash
   rm src/services/core/error_service.py
   ```

2. Update any documentation referring to ErrorService

## Verification Checklist

- [ ] All ErrorService imports removed
- [ ] All ErrorService.route_error_handler calls removed
- [ ] All router registrations using direct FastAPI approach
- [ ] All services using FastAPI's native error handling
- [ ] All endpoints returning correct responses
- [ ] All error responses properly formatted
- [ ] Docker container builds and runs correctly
- [ ] Documentation updated to reflect changes

## Rollback Plan

If issues are encountered:

1. Revert changes to specific files
2. If major issues occur, restore from version control
3. Document any issues encountered for future reference

## Verification Steps

1.  **Navigate to Project Root**: Ensure you are in the project root directory.
    ```bash
    cd .
    ```
2.  **Search for `ErrorService`**: Verify no occurrences remain in the `src` directory.
