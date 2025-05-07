# ScraperSky Workflow Builder Cheat Sheet

> ## ⚠️ ENUM STANDARDIZATION MANDATE ⚠️
>
> **ALL WORKFLOWS MUST USE THESE EXACT ENUM VALUES WITHOUT EXCEPTION:**
>
> **CurationStatus:** `New`, `Queued`, `Processing`, `Complete`, `Error`, `Skipped` > **ProcessingStatus:** `Queued`, `Processing`, `Complete`, `Error`
>
> **Database Types:** `{workflow_name}curationstatus`, `{workflow_name}processingstatus` > **Python Classes:** `{ClassName}CurationStatus`, `{ClassName}ProcessingStatus`
>
> **Location:** Place enum classes in the SAME FILE as their related models

This is a practical checklist for creating a new standardized workflow by cloning and adapting an existing one. All ScraperSky workflows follow the identical pattern - just fill in the blanks and follow these cookie-cutter steps.

## Step 1: Define Your Workflow

| Question                                    | Example Answer       | Your Answer |
| ------------------------------------------- | -------------------- | ----------- |
| **What is the workflow name?** (snake_case) | `contact_extraction` |             |
| **What is the source table?**               | `pages`              |             |
| **What is the destination table?**          | `contacts`           |             |

> **NOTE**: The workflow name determines all naming patterns. Use snake_case format.

## Step 2: Add Database Columns (Manual SQL - No Alembic!)

```sql
-- Create required enum types (MUST be created BEFORE adding columns)
CREATE TYPE {workflow_name}curationstatus AS ENUM ('New', 'Queued', 'Processing', 'Complete', 'Error', 'Skipped');
CREATE TYPE {workflow_name}processingstatus AS ENUM ('New', 'Queued', 'Processing', 'Complete', 'Error');

-- Add columns to source table (e.g., pages)
ALTER TABLE {source_table} ADD COLUMN {workflow_name}_curation_status {workflow_name}curationstatus NOT NULL DEFAULT 'New';
ALTER TABLE {source_table} ADD COLUMN {workflow_name}_processing_status {workflow_name}processingstatus NULL;
ALTER TABLE {source_table} ADD COLUMN {workflow_name}_processing_error TEXT NULL;

-- Create indexes for performance (CRITICAL for status-based queries)
CREATE INDEX IF NOT EXISTS idx_{source_table}_{workflow_name}_curation_status ON {source_table}({workflow_name}_curation_status);
CREATE INDEX IF NOT EXISTS idx_{source_table}_{workflow_name}_processing_status ON {source_table}({workflow_name}_processing_status);
```

### Verification Queries

```sql
-- Check the enum types and their values
SELECT
    t.typname AS enum_name,
    array_agg(e.enumlabel ORDER BY e.enumsortorder) AS enum_values
FROM
    pg_type t
JOIN
    pg_enum e ON t.oid = e.enumtypid
JOIN
    pg_catalog.pg_namespace n ON n.oid = t.typnamespace
WHERE
    n.nspname = 'public' -- Adjust if your enums are in a different schema
    AND t.typtype = 'e' -- Filter for enum types
GROUP BY
    t.typname
ORDER BY
    t.typname;

-- Check the table columns after adding them
SELECT
    column_name,
    data_type,
    is_nullable,
    column_default,
    udt_name -- This shows the specific ENUM type name
FROM
    information_schema.columns
WHERE
    table_schema = 'public'
    AND table_name = '{source_table}'
ORDER BY
    ordinal_position;
```

## Step 3: Add Python Enums and Update Model

> **IMPORTANT STANDARDIZATION NOTE:** Place enums in the same module as their related models (domain-based placement).
> This is our preferred pattern going forward, though you may see inconsistent placement in legacy code.

```python
# In src/models/{source_table}.py
from enum import Enum
from sqlalchemy import Column, Text
from sqlalchemy.dialects.postgresql import ENUM as PgEnum

# Define Python enums in the same file as their related model
class {SourceTable}CurationStatus(str, Enum):
    New = "New"
    Queued = "Queued"
    Processing = "Processing"
    Complete = "Complete"
    Error = "Error"
    Skipped = "Skipped"

class {SourceTable}ProcessingStatus(str, Enum):
    Queued = "Queued"
    Processing = "Processing"
    Complete = "Complete"
    Error = "Error"

# Update the SQLAlchemy model
class {SourceTable}(Base):
    # ... existing columns ...

    # Add new workflow columns with proper enum references
    {workflow_name}_curation_status = Column(
        PgEnum({SourceTable}CurationStatus, name="{workflow_name}curationstatus", create_type=False),
        nullable=False,
        server_default={SourceTable}CurationStatus.New.value,
        index=True  # Add index for status filtering
    )

    {workflow_name}_processing_status = Column(
        PgEnum({SourceTable}ProcessingStatus, name="{workflow_name}processingstatus", create_type=False),
        nullable=True,
        index=True  # Add index for scheduler polling
    )
```

## Step 4: Clone & Adapt API Router

1. **Copy an existing router** (e.g., `src/routers/pages.py` → `src/routers/{source_table}s.py`)
   1a. **Verify/confirm new router path with User if not standard or obvious.**

2. **IMPORTANT: Standard Session Dependency**
   For FastAPI endpoints, you **MUST** use the project's standard dependency injection pattern:

   ```python
   from src.session.async_session import get_session_dependency
   ```

3. **Update imports** for domain-based enum placement:
   ```python
   # Import source model
   from src.models.{source_table} import {SourceTable}
   # Import enums from model file (domain-based placement)
   from src.models.{source_table} import {SourceTable}CurationStatus, {SourceTable}ProcessingStatus
   ```
4. **Update endpoint URL** for specific workflow:
   ```python
   @router.put("/api/v3/{source_table}s/{workflow_name}/status", response_model=GenericResponse)
   ```
5. **Ensure dual-status update logic** is implemented in route handler

## Step 5: Register Router in main.py

```python
from src.routers.{source_table_or_workflow_router_file} import router as {workflow_name}_router # Adjust import
# ...
app.include_router({workflow_name}_router, tags=["{WorkflowNameTitle} | {SourceTableTitle}s"]) # Use descriptive tags
```

## Step 6: Clone & Adapt Background Scheduler

> This is the **consumer** in the producer-consumer pattern. It polls for records with status set to 'Queued' by the API endpoint.

1. **Copy an existing scheduler** function (e.g., `src/services/{existing_workflow}_scheduler.py`)
2. **Update imports** for domain-based enum placement:
   ```python
   # Import source model
   from src.models.{source_table} import {SourceTable}
   # Import processing enum from model file
   from src.models.{source_table} import {SourceTable}ProcessingStatus
   ```
   2a. **Ensure DB access uses `get_background_session()`.**
3. **Use `with_for_update(skip_locked=True)`** in query to prevent race conditions
4. **Register your scheduler** in `src/schedulers.py`:

```python
scheduler.add_job(
    process_{workflow_name}_queue,
    'interval',
    minutes=1,  # Make configurable
    id=f"{workflow_name}_scheduler",
    max_instances=1  # Prevents race conditions
)
```

## Step 7: Implement Processing Service

This requires custom logic. Create `src/services/{workflow_name}_service.py`:

```python
# Import enums from model file (domain-based placement)
from src.models.{source_table} import {SourceTable}, {SourceTable}ProcessingStatus

async def process_single_{source_table}_for_{workflow_name}(session: AsyncSession, {source_table}_id: UUID) -> None:
    try:
        # Step 1: Retrieve the source record (outside transaction)
        stmt = select({SourceTable}).where({SourceTable}.id == {source_table}_id)
        result = await session.execute(stmt)
        source_record = result.scalar_one_or_none()

        if not source_record:
            logger.warning(f"{SourceTable} {source_table}_id not found")
            return

        # IMPORTANT: Idempotency check - prevents duplicate processing
        if source_record.{workflow_name}_processing_status != {SourceTable}ProcessingStatus.Processing:
            logger.warning(f"Status changed to {source_record.{workflow_name}_processing_status}. Skipping.")
            return

        # Step 2: Extract & process data - CUSTOM LOGIC HERE
        # This happens outside transaction for long-running operations
        extracted_data = await perform_custom_extraction(source_record)

        # Step 3: Update status after processing (atomic transaction)
        async with session.begin():
            # Option A: Update source record only
            source_record.{workflow_name}_processing_status = {SourceTable}ProcessingStatus.Complete

            # Option B: Create new destination record with extracted data
            # new_record = {DestinationTable}(**extracted_data)
            # session.add(new_record)
            # source_record.{destination_table}_extraction_status = {SourceTable}ProcessingStatus.Complete
    except Exception as e:
        logger.error(f"Error in {workflow_name} processing: {e}")
        # Update error status in a new transaction
        async with session.begin():
            source_record.{workflow_name}_processing_status = {SourceTable}ProcessingStatus.Error
            source_record.{workflow_name}_processing_error = str(e)[:1000]  # Truncate long errors
```

> **Key Points**: • Check status before processing (idempotency) • Place custom logic outside transaction • Use proper transactional boundaries • Catch exceptions and update error status

## Done!

That's it! The workflow is now implemented and will follow the standard pattern used throughout ScraperSky.
