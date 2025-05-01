# STRATEGIC DIRECTIVE: ScraperSky Database Session Factory Enhancement

## CONTEXT

Our ScraperSky backend modernization is progressing well. We've fixed the database transaction issues as documented in `Docs/90.7-Database-Transaction-Issue-Resolution.md` and begun connection pooling standardization (see `Docs/90.9-Connection-Pooling-Implementation-Summary.md`). 

However, our current approach to connection pooling has revealed a more efficient solution: enhancing the database session factory to automatically apply required Supavisor parameters, rather than passing parameters through multiple layers of the application.

## YOUR ASSIGNMENT

Review document: `/Docs/90.10-Database-Session-Factory-Enhancement.md`

Implement a centralized approach to standardize Supavisor connection pooling across all database operations by enhancing the database session factory and creating SQL utility helpers.

### Required Deliverables

1. **Enhanced Database Session Factory**
   - Modify `src/db/session.py` to implement the session factory as specified in section 3.1 of the document
   - Ensure sessions automatically include Supavisor compatibility parameters
   - Document the automatic parameter application functionality

2. **SQL Utility Helpers**
   - Create `src/utils/db_utils.py` with the `execute_raw_sql` function as specified in section 3.2
   - Implement proper error handling and result transformation
   - Include comprehensive documentation for the helper functions

3. **Service Implementation**
   - Update `src/services/profile_service.py` to use the new pattern as shown in section 3.3
   - Ensure the service works with the new session factory and SQL helpers
   - Verify all database operations continue to function correctly

## SUCCESS CRITERIA

Your implementation will be considered successful when:

1. Database sessions automatically include required Supavisor parameters
2. `execute_raw_sql` helper correctly executes queries with proper error handling
3. Profile service successfully uses the new pattern
4. No explicit parameter passing is needed in endpoints
5. All database operations work reliably with the enhanced session factory

## TESTING REQUIREMENTS

Test your implementation with:

1. **Session Factory Tests**
   - Verify sessions created through the factory have the correct parameters
   - Check that different query types work correctly with the enhanced sessions

2. **SQL Helper Tests**
   - Test the `execute_raw_sql` function with SELECT, INSERT, UPDATE, DELETE operations
   - Verify results are correctly transformed to dictionaries

3. **Service Integration Test**
   - Test the updated profile service with the profiles endpoint
   - Verify data retrieval works without explicit parameter passing

## DELIVERABLES

1. Code changes implementing the session factory enhancement
2. SQL utility helper implementation
3. Updated profile service implementation
4. Test results showing successful operation
5. Brief summary of changes and their effects

## TIMELINE

This is our third high-leverage task. Please complete it within 8-10 hours of starting work.

## KEY CONSIDERATIONS

1. **Backward Compatibility**: Ensure existing code continues to work with the enhanced session factory
2. **Performance**: Monitor for any performance impacts from the changes
3. **ORM Compatibility**: Some SQLAlchemy ORM operations might behave differently with the new settings
4. **Error Handling**: Ensure comprehensive error handling in the SQL utility helpers

This enhancement will significantly improve the reliability and maintainability of our database operations by centralizing connection pooling parameter application and standardizing SQL execution patterns.