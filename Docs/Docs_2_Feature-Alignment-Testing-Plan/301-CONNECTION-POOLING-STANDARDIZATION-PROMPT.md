# STRATEGIC DIRECTIVE: ScraperSky Connection Pooling Standardization

## CONTEXT

Our ScraperSky backend has been successfully improved by fixing database transaction issues, as documented in `Docs/90.7-Database-Transaction-Issue-Resolution.md`. The next high-leverage improvement is standardizing connection pooling parameters across all database operations.

Currently, database endpoints inconsistently apply the required Supavisor connection pooling parameters (`raw_sql=true`, `no_prepare=true`, `statement_cache_size=0`). Some endpoints include these parameters while others don't, leading to unreliable behavior especially in production environments.

## YOUR ASSIGNMENT

Review document: `/Docs/90.8-Connection-Pooling-Standardization.md`

Implement a central mechanism to automatically apply connection pooling parameters to all database operations, following the detailed implementation plan in the document.

### Required Deliverables

1. **Database URL Modifier Utility in `src/db/engine.py`**
   - Create the `get_supavisor_ready_url()` function exactly as specified in the document
   - Ensure it handles URLs with and without existing query parameters

2. **Modified Database Engine Creation in `src/db/engine.py`**
   - Update the engine creation function to use the new URL modifier
   - Ensure all engine creation points in the codebase use this function

3. **Endpoint Parameter Helper in `src/utils/db_helpers.py`**
   - Create this new file if it doesn't exist
   - Implement the `get_db_params()` function as a FastAPI dependency
   - Document its purpose and usage

4. **Update One Example Endpoint**
   - Apply the new parameter helper to the profiles endpoint (`src/routers/profile.py`)
   - Verify it correctly uses the connection pooling parameters

## SUCCESS CRITERIA

Your implementation will be considered successful when:

1. All database connections automatically include the required parameters
2. The system works reliably with these standardized parameters
3. No connection errors appear in logs related to pooling
4. The implementation follows the approach outlined in the document

## TESTING REQUIREMENTS

Test with the following endpoints:

1. **Profiles Endpoint**: `/api/v3/profiles`
   - Verify that the endpoint works with the new parameter helper

2. **Database URL Transformation**:
   - Test with URLs that have existing query parameters
   - Test with URLs that don't have query parameters
   - Verify parameters are correctly added in both cases

## DELIVERABLES

1. Code changes to implement the connection pooling standardization
2. Test results showing successful application of parameters
3. Brief summary of changes made and their effect

## TIMELINE

This is our second highest priority task after the database transaction fixes. Please complete it within 8 hours of starting work.

## KEY CONSIDERATIONS

1. **Minimal Disruption**: Make changes that maintain backward compatibility
2. **Focus on Leverage**: This change should impact all database operations with minimal code changes
3. **Consistent Implementation**: Ensure the approach is consistent with the existing codebase
4. **Quality over Speed**: It's better to implement it correctly than quickly

This standardization will significantly improve the reliability of our database operations, especially in production environments where connection pooling is critical.
