# STRATEGIC DIRECTIVE: Complete Connection Pooling MVP

## CONTEXT

Our ScraperSky backend modernization is nearing completion. We've fixed database transaction issues (90.7) and made significant progress on connection pooling standardization (90.9). The final step is to complete connection pooling with minimal changes before moving to feature alignment (100.0).

## YOUR ASSIGNMENT

Review document: `/Docs/90.11-Connection-Pooling-Completion.md`

Make a single, focused change to the database session factory that will ensure all database operations automatically use the required Supavisor connection pooling parameters.

### Required Implementation

1. **Update Session Factory in `src/db/session.py`**
   - Locate where the SQLAlchemy async_session factory is created
   - Add the execution_options parameter with `postgresql_expert_mode=True` as shown in section 1 of the document
   - Leave all other code untouched
   
2. **Test Existing Endpoints**
   - Verify the profile endpoint works with the updated session factory
   - Verify the features endpoint works with the updated session factory
   - Verify the domain scanner endpoint works with the updated session factory

## SUCCESS CRITERIA

This task will be successful when:

1. The session factory includes the postgresql_expert_mode execution option
2. Existing endpoints work without modification
3. No database connection errors appear in logs

## TESTING APPROACH

1. Make the minimal change to the session factory
2. Restart the application
3. Test each endpoint to verify it still works properly
4. Check logs for any database connection errors

## DELIVERABLES

1. The single code change to `src/db/session.py`
2. A brief report confirming that endpoints work with the updated session factory

## IMPORTANT: AVOID SCOPE CREEP

This is a minimalist MVP approach:
- Make only this ONE change
- Do NOT add new utility files
- Do NOT modify service implementations
- Do NOT add parameter passing mechanisms
- Do NOT rewrite existing code

We are prioritizing simplicity and stability over perfect implementation. This single change will get us to a working state without overengineering.

## TIMELINE

This should be a quick task - aim to complete it within 1-2 hours maximum.