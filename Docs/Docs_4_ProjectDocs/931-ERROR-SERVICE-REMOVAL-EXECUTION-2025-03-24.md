# ErrorService Removal Execution Plan

## Date: 2025-03-24

## Files Requiring Modification

Based on our analysis, the following files need modification to completely remove the custom ErrorService:

### 1. Service Files

| File | Current Usage | Required Action |
|------|---------------|-----------------|
| `/src/services/scraping/scrape_executor_service.py` | `from ..error.error_service import error_service` | Remove import and replace error handling |
| `/src/services/places/places_search_service.py` | `from ...services.core.error_service import error_service` | Remove import and replace error handling |
| `/src/services/batch/batch_processor_service.py` | `from ..core.error_service import error_service` | Remove import and replace error handling |

### 2. Implementation File

| File | Action |
|------|--------|
| `/src/services/core/error_service.py` | Consider removal after all references are eliminated |

## Execution Plan

### Step 1: Modify Service Files

For each service file:
1. View the current implementation
2. Identify how error_service is being used
3. Replace with standard Python try/except or FastAPI error handling
4. Test functionality after changes

### Step 2: Test Application

After each service file modification:
1. Restart Docker container
2. Test relevant endpoints
3. Verify error handling works correctly

### Step 3: Final Cleanup

Once all service files are updated:
1. Consider removing the error_service.py file
2. Update documentation
3. Final testing of all endpoints

## Detailed Modification Plan

### For Each Service File:

1. **Remove import statement**:
   ```python
   # Remove this line
   from ..core.error_service import error_service
   ```

2. **Replace error_service.handle_exception calls**:
   ```python
   # Replace this:
   except Exception as e:
       error_service.handle_exception(e, "operation_name")
       raise

   # With this:
   except Exception as e:
       logger.error(f"Error in operation_name: {str(e)}")
       raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
   ```

3. **Replace error_service.wrap_function calls**:
   ```python
   # Replace this:
   result = await error_service.wrap_async_function(async_function, *args, **kwargs)

   # With this:
   try:
       result = await async_function(*args, **kwargs)
   except Exception as e:
       logger.error(f"Error in {async_function.__name__}: {str(e)}")
       raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
   ```

## Verification Checklist

After each file modification:
- [ ] All error_service imports removed
- [ ] All error_service function calls replaced
- [ ] Functionality tested and working
- [ ] Error handling verified

## Rollback Plan

If issues are encountered:
1. Revert changes to the specific file
2. Document the issue
3. Consider alternative approaches