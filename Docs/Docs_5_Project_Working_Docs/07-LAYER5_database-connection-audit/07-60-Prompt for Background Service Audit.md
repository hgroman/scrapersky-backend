# Prompt for Background Service Audit

## Project Context

You're working on the ScraperSky backend – a FastAPI application using SQLAlchemy for database interactions with PostgreSQL via Supavisor. We've successfully identified and fixed a critical issue with background tasks in the batch processing service, where SQLAlchemy async operations were failing with `MissingGreenlet` errors.

## What Was Accomplished

We've:

1. Fixed the "MissingGreenlet" error in batch processing by implementing a specific pattern
2. Created documentation in `07-59-BACKGROUND-TASK-STANDARDIZATION-WORK-ORDER.md`
3. Established a technical pattern in `20-BACKGROUND-TASK-SQLALCHEMY-PATTERN.md`
4. Identified a clear architectural dependency map in `07-60-ScraperSky Batch Scraper Dependency Map.md`

## Your Mission

Your task is to systematically audit all remaining background service implementations and apply our proven pattern. Specifically:

1. **Audit all background task implementations** in:

   - `src/services/sitemap/background_service.py`
   - `src/services/places/places_search_service.py`
   - `src/tasks/email_scraper.py`
   - Any other services that use background tasks

2. **Refactor each implementation** to follow our pattern:

   - Use isolated session management for each database operation
   - Implement proper error handling for each step
   - Ensure clean, linear async flow without nested operations
   - Use `get_background_session()` for all database operations
   - Maintain session lifecycle control (commit/rollback handled by context manager)

3. **Document your changes** by:
   - Creating a clear summary of what you're changing and why
   - Following our architectural boundaries from the dependency map
   - Creating detailed implementation plans for each service

## Technical Requirements

1. **Session Management**:

   - Always use `get_background_session()` for background tasks
   - Create a new session for each discrete database operation
   - Never reuse sessions across operations

2. **Async Flow**:

   - Process items sequentially with clean, linear control flow
   - Avoid nesting async operations that share database connections

3. **Error Handling**:
   - Catch and log all exceptions
   - Use new sessions for status updates after errors
   - Ensure errors in one item don't prevent processing of others

## Approach

1. Start by analyzing each background task implementation
2. Document the current approach and any potential issues
3. Implement the new pattern, following our work in batch processing
4. Add comprehensive error handling and logging
5. Update any references to these background tasks

Remember, the goal is to standardize all background tasks to avoid `MissingGreenlet` errors while maintaining clear, maintainable code with proper error handling.
