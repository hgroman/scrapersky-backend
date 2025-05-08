# Enhanced Database Connection Audit Plan

**Date:** 2025-03-25
**Author:** Claude AI
**Status:** Draft
**Priority:** CRITICAL

## Executive Summary

This document enhances the existing database connection audit plan with a comprehensive two-phase approach. Phase 1 focuses on completing the immediate fixes for non-compliant connection patterns, while Phase 2 establishes a systematic framework for long-term compliance and standardization.

## Phase 1: Initial Compliance (In Progress)

_Current focus: Fix identified non-compliant connection patterns_

### Completed Tasks

1. Identified four files with non-compliant database connection patterns:
   - ✅ `/src/services/sitemap/processing_service.py` - Fixed by removing non-compliant `_process_domain` method
   - ✅ `/debug_sitemap_flow.py` - Fixed by removing unused import of `async_session_factory`
   - ✅ `/src/routers/google_maps_api.py` - Fixed by replacing non-compliant `async_session_factory` with `get_session()`
   - ✅ `/src/routers/batch_page_scraper.py` - Fixed by replacing non-compliant import with `get_session`

### Findings from debug_sitemap_flow.py Execution

Running the debug_sitemap_flow.py script revealed several issues:

1. **Database Connection Configuration**: The script successfully connects to the database using the correct pattern:

   ```
   Using Supabase Supavisor connection pooler at aws-0-us-west-1.pooler.supabase.com:6543
   Using database URL: postgresql+asyncpg://postgres.ddfldwzhdhhzhxywqnyz:********@aws-0-us-west-1.pooler.supabase.com:6543/postgres
   ```

2. **Session Usage Pattern**: The script now properly uses the `get_session()` context manager:

   ```python
   async with get_session() as session:
       # Use the session here
   ```

3. **Database Schema Error**: Encountered error with sitemap_files table schema:

   ```
   column "url_count" of relation "sitemap_files" does not exist
   ```

   This indicates a model-to-schema misalignment issue.

4. **Type Error**: Job ID is handled incorrectly in database operations:

   ```
   operator does not exist: character varying = uuid
   ```

   This suggests type casting issues in data access code.

5. **Session Error Handling**: The error handling for database sessions has issues:
   ```
   Error closing session: 'AsyncSession' object has no attribute 'closed'
   ```
   This indicates improper session cleanup.

### Remaining Phase 1 Tasks

1. **Critical**: Locate and implement the background task methods:

   - `page_processing_service.process_domain_background`

     - Referenced in `/src/routers/batch_page_scraper.py:108` but not found in codebase
     - Receives `db_params` which is non-compliant

   - `batch_processor_service.process_batch_background`
     - Referenced in `/src/routers/batch_page_scraper.py:187` but not found in codebase
     - Receives `db_params` which is non-compliant

2. **Fix Session Management in Batch Processing**:

   - Batch processor service has proper session creation with `get_session()` at line 86:
     ```python
     async with get_session() as session:
         # Session usage here
     ```
   - However, it's unclear how background task methods `process_domain_background` and `process_batch_background` manage sessions

3. **Fix URL Count Schema Issue**:

   - Address the schema mismatch for `url_count` column in `sitemap_files` table

4. **Fix Job ID Type Casting**:

   - Address the type mismatch between character varying and UUID in job-related database operations

5. **Perform comprehensive search for any other instances of `async_session_factory`**:

   ```bash
   grep -r "async_session_factory" --include="*.py" ./src
   ```

6. **Search for direct session creation patterns**:

   ```bash
   grep -r "session = " --include="*.py" ./src
   grep -r "create_async_engine" --include="*.py" ./src
   ```

7. **Verify all changes with the test script**:
   ```bash
   python project-docs/07-database-connection-audit/scripts/test_supabase_connection.py
   ```

## Immediate Implementation Fixes

After analyzing the codebase, we've discovered that the background task methods referenced in the batch_page_scraper.py router are missing entirely rather than just having incorrect database connection patterns. This must be addressed as a priority since it breaks core functionality.

### 1. Implementation of Missing Background Task Methods

#### 1.1 Implement Page Processing Background Task

Create the missing `process_domain_background` method in the page_processing_service.py module:

```python
async def process_domain_background(
    job_id: str,
    domain: str,
    max_pages: int = 100,
    user_id: str = "system",
    **kwargs  # Remove db_params dependency
) -> None:
    """
    Process a domain in the background.

    This is a self-contained background task that creates its own database session
    using the approved get_session() context manager.

    Args:
        job_id: Job ID for tracking
        domain: Domain to process
        max_pages: Maximum pages to process
        user_id: User ID for attribution
    """
    logger.info(f"Starting dedicated background processing for domain: {domain}, job_id: {job_id}")
    logger.info(f"Job parameters: user_id={user_id}")

    # Track job status in memory while database connection is established
    _job_statuses[job_id] = {
        "status": "started",
        "created_at": datetime.utcnow().isoformat(),
        "domain": domain,
        "progress": 0.0,
        "metadata": {"sitemaps": []},
        "started_at": datetime.utcnow().isoformat()
    }

    try:
        # Create dedicated session using the approved connection pattern
        logger.info(f"Using standard session factory for job {job_id}")
        async with get_session() as session:
            # Start transaction
            async with session.begin():
                logger.info(f"Started transaction for job {job_id}")

                # Process the domain (implement core functionality)
                # ...

                # Update job status in the database
                await job_service.update_job_status(
                    session=session,
                    job_id=job_id,
                    status="completed",
                    progress=100.0
                )

                # Update in-memory status
                _job_statuses[job_id]["status"] = "completed"
                _job_statuses[job_id]["progress"] = 100.0
                _job_statuses[job_id]["completed_at"] = datetime.utcnow().isoformat()

    except Exception as e:
        # Log the error
        error_message = f"Error processing domain {domain}: {str(e)}"
        logger.error(error_message)
        logger.error(f"Debug info - Job ID: {job_id}, Domain: {domain}")

        # Update in-memory status
        _job_statuses[job_id]["status"] = "failed"
        _job_statuses[job_id]["error"] = error_message
        _job_statuses[job_id]["completed_at"] = datetime.utcnow().isoformat()

        # Create a new session for error reporting
        try:
            async with get_session() as error_session:
                async with error_session.begin():
                    # Update job status to reflect the error
                    await job_service.update_job_status(
                        session=error_session,
                        job_id=job_id,
                        status="failed",
                        progress=0.0,
                        error=error_message
                    )
        except Exception as inner_e:
            # If we can't update the database, at least log the error
            logger.error(f"Failed to update job status in database: {str(inner_e)}")
```

#### 1.2 Implement Batch Processor Background Task

Create the missing `process_batch_background` method in the batch_processor_service.py module:

```python
async def process_batch_background(
    batch_id: str,
    domains: List[str],
    max_pages: int = 100,
    max_concurrent_jobs: int = 5,
    user_id: str = "system",
    **kwargs  # Remove db_params dependency
) -> None:
    """
    Process a batch of domains in the background.

    This is a self-contained background task that creates its own database session
    using the approved get_session() context manager.

    Args:
        batch_id: Batch ID for tracking
        domains: List of domains to process
        max_pages: Maximum pages to process per domain
        max_concurrent_jobs: Maximum concurrent jobs
        user_id: User ID for attribution
    """
    logger.info(f"Starting batch processing: {batch_id}, {len(domains)} domains")

    # Create a semaphore to limit concurrency
    semaphore = asyncio.Semaphore(max_concurrent_jobs)

    # Create the batch record
    async with get_session() as session:
        async with session.begin():
            # Update batch status to processing
            await job_service.update_batch_status(
                session=session,
                batch_id=batch_id,
                status="processing",
                total_items=len(domains),
                completed_items=0,
                failed_items=0
            )

    # Create task list
    tasks = []
    for domain in domains:
        # Create a job ID for each domain
        job_id = f"batch_{batch_id}_{uuid.uuid4().hex[:8]}"

        # Define a wrapper function that respects the semaphore
        async def process_with_semaphore(domain, job_id):
            async with semaphore:
                # Call the domain processing function
                from src.services.page_scraper.processing_service import process_domain_background
                await process_domain_background(
                    job_id=job_id,
                    domain=domain,
                    max_pages=max_pages,
                    user_id=user_id
                )

        # Add the task to the list
        tasks.append(process_with_semaphore(domain, job_id))

    # Execute all tasks
    try:
        # Run all tasks concurrently with controlled concurrency
        await asyncio.gather(*tasks)

        # Update batch status to completed
        async with get_session() as session:
            async with session.begin():
                await job_service.update_batch_status(
                    session=session,
                    batch_id=batch_id,
                    status="completed",
                    completed_at=datetime.utcnow()
                )
    except Exception as e:
        # Log the error
        logger.error(f"Error processing batch {batch_id}: {str(e)}")

        # Update batch status to failed
        try:
            async with get_session() as session:
                async with session.begin():
                    await job_service.update_batch_status(
                        session=session,
                        batch_id=batch_id,
                        status="failed",
                        error=str(e),
                        completed_at=datetime.utcnow()
                    )
        except Exception as inner_e:
            logger.error(f"Error updating batch status: {str(inner_e)}")
```

### 2. Update Router to Remove db_params

Modify the `batch_page_scraper.py` router to remove the `db_params` parameter from background task calls:

```python
# Before
background_tasks.add_task(
    page_processing_service.process_domain_background,
    job_id=job_id,
    domain=base_url,
    max_pages=max_pages,
    user_id=current_user.get("id"),
    db_params=db_params  # Remove this
)

# After
background_tasks.add_task(
    page_processing_service.process_domain_background,
    job_id=job_id,
    domain=base_url,
    max_pages=max_pages,
    user_id=current_user.get("id")
)
```

And similar changes for the batch processing task:

```python
# Before
background_tasks.add_task(
    batch_processor_service.process_batch_background,
    batch_id=batch_id,
    domains=request.domains,
    max_pages=request.max_pages or 100,
    max_concurrent_jobs=request.max_concurrent_jobs or 5,
    user_id=current_user.get("id"),
    db_params=db_params  # Remove this
)

# After
background_tasks.add_task(
    batch_processor_service.process_batch_background,
    batch_id=batch_id,
    domains=request.domains,
    max_pages=request.max_pages or 100,
    max_concurrent_jobs=request.max_concurrent_jobs or 5,
    user_id=current_user.get("id")
)
```

### 3. Fix Database Schema Mismatch

The `url_count` column is referenced in the code but doesn't exist in the database. Two options:

#### Option A: Update the Database Schema (Preferred)

Add the missing column to the database:

```sql
ALTER TABLE sitemap_files ADD COLUMN url_count INTEGER DEFAULT 0;
```

#### Option B: Update the Model Code

Remove the `url_count` field from the model and any references to it in the code.

### 4. Fix Job ID Type Casting

Add explicit type casting in the job service:

```python
# Before
query = update(Job).where(Job.job_id == job_id)

# After
query = update(Job).where(Job.job_id == str(job_id))
```

Or ensure consistent types in the schema:

```python
# In models/job.py
job_id = Column(String, index=True)  # Ensure it's defined as String not UUID
```

## Phase 2: Comprehensive Standardization

_Strategic enforcement of connection standards across the entire codebase_

### 1. Complete Database Connection Inventory

1. **Create a comprehensive database touchpoint inventory document**:

   - Document ALL database connection points in a single reference file
   - Include file paths, line numbers, and connection types
   - Categorize by component type (router, service, background task)
   - Update this inventory document with each code change

2. **Use automated tools to generate the initial inventory**:

   ```bash
   # Find all session dependencies
   grep -r "Depends(get_session" --include="*.py" ./src > db_touchpoints.txt

   # Find all session parameters
   grep -r "session: AsyncSession" --include="*.py" ./src >> db_touchpoints.txt

   # Find all database operations
   grep -r "session.execute\|session.query\|session.add\|session.delete" --include="*.py" ./src >> db_touchpoints.txt
   ```

### 2. Extended Connection Configuration Verification

1. **Verify pool size settings**:

   - Ensure minimum pool size of 5
   - Verify recommended pool size of 10 where appropriate
   - Check all engine creation parameters for compliance with README requirements

2. **Validate Supavisor-specific configuration**:
   - Verify correct connection string format
   - Confirm SSL context configuration
   - Validate statement cache disabled for pgbouncer compatibility

### 3. Endpoint Parameter Support Audit

1. **Identify all database-intensive endpoints**:

   - Cross-reference with the database touchpoint inventory
   - Focus on endpoints with complex database operations

2. **Verify parameter support**:

   - Check each endpoint for support of:
     - `raw_sql=true`
     - `no_prepare=true`
     - `statement_cache_size=0`
   - Test functionality of these parameters

3. **Document endpoint parameter compliance**:
   - Add status to the database touchpoint inventory
   - Create examples of correct implementation

### 4. Alembic Migration Configuration Audit

1. **Verify Alembic configuration follows connection standards**:

   - Ensure connection string format is correct
   - Check for proper Supavisor pooling configuration
   - Test migrations with Supavisor connection

2. **Document Alembic compliance status**:
   - Include in the database touchpoint inventory
   - Create reference implementation if needed

### 5. Schema Verification Process

1. **Use existing database tools**:

   - `scripts/db/inspect_table.py` for schema verification
   - `scripts/db/simple_inspect.py` for Python 3.13 compatibility
   - `scripts/db/test_connection.py` for connection testing

2. **Document any discrepancies found**:
   - Update models to match actual schema
   - Fix relationship configurations

### 6. Implementation of Enforcement Tools

1. **Develop a custom database connection linter**:

   - Create Python script to detect non-compliant connection patterns
   - Identify direct session creation
   - Detect improper connection string formats
   - Flag missing dependency injection

2. **Integrate with CI/CD pipeline**:
   - Add as a pre-commit hook
   - Include in GitHub Actions workflow
   - Automatically run on PR submissions

### 7. Continuous Compliance Monitoring

1. **Schedule regular automated audits**:

   - Weekly automated linter runs
   - Monthly manual review of high-risk files

2. **Create a compliance dashboard**:
   - Track non-compliant files
   - Monitor progress over time

## Success Criteria

1. **Zero direct database connections** - All connections use the approved pattern
2. **Complete tenant isolation removal** - No references to tenant_id filtering in DB operations
3. **100% test script pass rate** - All connections work with the test script
4. **Comprehensive documentation** - Complete inventory of all database touchpoints
5. **Automated enforcement** - Linter catches any non-compliant additions

## Technical Requirements from README

The following requirements from the README.md must be enforced in all database connections:

1. **Supavisor Connection Pooling**:

   - Connection string format: `postgresql+asyncpg://postgres.your-project:password@aws-0-us-west-1.pooler.supabase.com:6543/postgres`
   - Pool size: Minimum 5, recommended 10
   - Pool pre-ping: Enabled

2. **Connection Parameters for Endpoints**:

   - `raw_sql=true` - Use raw SQL instead of ORM
   - `no_prepare=true` - Disable prepared statements
   - `statement_cache_size=0` - Control statement caching

3. **Model Requirements**:
   - Models match actual database schema
   - Proper relationship configurations

## Implementation Timeline

| Phase | Action                                  | Timeline    | Owner        |
| ----- | --------------------------------------- | ----------- | ------------ |
| 1     | Complete current audit                  | In progress | Current team |
| 1     | Fix background task methods             | 1 day       | TBD          |
| 1     | Comprehensive search for non-compliance | 1 day       | TBD          |
| 1     | Verify with test script                 | 1 day       | TBD          |
| 2     | Create database touchpoint inventory    | 2 days      | TBD          |
| 2     | Verify configuration parameters         | 1 day       | TBD          |
| 2     | Audit endpoint parameter support        | 2 days      | TBD          |
| 2     | Check Alembic configuration             | 1 day       | TBD          |
| 2     | Verify schema alignment                 | 2 days      | TBD          |
| 2     | Develop enforcement tools               | 3 days      | TBD          |
| 2     | Implement continuous monitoring         | 1 day       | TBD          |

## References

1. [Database Connection Standards](../Docs_1_AI_GUIDES/07-DATABASE_CONNECTION_STANDARDS.md)
2. [Architecture Quick Reference](../Docs_1_AI_GUIDES/02-ARCHITECTURE_QUICK_REFERENCE.md)
3. [Tenant Isolation Removed](../Docs_1_AI_GUIDES/09-TENANT_ISOLATION_REMOVED.md)
4. [Simplification Opportunities](../Docs_1_AI_GUIDES/04-SIMPLIFICATION_OPPORTUNITIES.md)
5. [README.md Database Requirements](../../README.md)
6. [Transaction Patterns Reference](./943-TRANSACTION-PATTERNS-REFERENCE.md)
7. [Supabase Connection Issue](./955-SUPABASE-CONNECTION-ISSUE.md)
