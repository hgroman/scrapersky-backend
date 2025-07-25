# ScraperSky Workflow Builder Cheat Sheet (Enhanced)

## Quick Reference Links

- [Complete Naming Conventions Guide](../Docs_6_Architecture_and_Status/CONVENTIONS_AND_PATTERNS_GUIDE.md) - The definitive reference for all naming patterns
- [Q&A Key Insights](../Docs_6_Architecture_and_Status/Q&A_Key_Insights.md) - Common questions and consensus answers
- [Scheduler and Settings Patterns](../Docs_1_AI_GUIDES/28-SCHEDULER_AND_SETTINGS_PATTERNS.md) - Best practices for scheduler implementation
- [Enum Handling Standards](../Docs_1_AI_GUIDES/27-ENUM_HANDLING_STANDARDS.md) - Guidelines for enum implementation
- [Transaction Patterns Reference](../Docs_7_Reference/07-04-transaction-patterns-reference.md) - Standards for transaction management

> ## ⚠️ ENUM STANDARDIZATION MANDATE ⚠️
>
> **ALL WORKFLOWS MUST USE THESE EXACT ENUM VALUES WITHOUT EXCEPTION:**
>
> **CurationStatus:** `New`, `Queued`, `Processing`, `Complete`, `Error`, `Skipped` > **ProcessingStatus:** `Queued`, `Processing`, `Complete`, `Error`
>
> **Database Types:** `{workflow_name}curationstatus`, `{workflow_name}processingstatus` > **Python Classes:** `{WorkflowName}CurationStatus`, `{WorkflowName}ProcessingStatus`
>
> **Location:** Place enum classes in the SAME FILE as their related models
>
> **Example of correct implementation:**
>
> ```python
> # In src/models/{source_table}.py
> class {WorkflowName}CurationStatus(str, Enum):
>     New = "New"
>     Queued = "Queued"
>     Processing = "Processing"
>     Complete = "Complete"
>     Error = "Error"
>     Skipped = "Skipped"
> ```

## CRITICAL NAMING CONVENTION

**THE WORKFLOW NAME DEFINES ALL NAMING CONVENTIONS THROUGHOUT THE IMPLEMENTATION**

The workflow name you choose in Phase 1 (e.g., "page_curation") will define:

- Database field names (`page_curation_curation_status`, `page_curation_processing_status`)
- Enum type names (`pagecurationcurationstatus`, `pagecurationprocessingstatus`) - _Note: DB enums often follow class name_
- Python Enum class names (`PageCurationCurationStatus`, `PageCurationProcessingStatus`)
- Service file names (`page_curation_service.py`, `page_curation_scheduler.py`)
- UI component IDs (`page-curation-tab`)
- Function names (`process_page_curation_queue`)

This consistency is **MANDATORY** and ensures all components are correctly linked throughout the system. **Use snake_case for the workflow name.**

## CRITICAL TRANSACTION PATTERN

**TRANSACTION MANAGEMENT RESPONSIBILITY:**

- **Router endpoints** MUST manage transaction boundaries with `async with session.begin():`
- **Processing service functions** should NOT start their own transactions
- **Dual-status updates** MUST occur within the same transaction
- **Example:**
  ```python
  async with session.begin():
      # Update curation_status
      # Update processing_status if needed
      # All changes committed together
  ```

## ORM EXCLUSIVITY REQUIREMENT

**ALL DATABASE OPERATIONS MUST USE SQLALCHEMY ORM**

- No raw SQL queries (security risk)
- No mixing of ORM and Core operations
- All table relationships must be defined in the models
- All ENUM values must match between database and Python

---

This guide provides a step-by-step process to create a new ScraperSky workflow based on the producer-consumer pattern. By following these 5 phases, you can rapidly implement a standardized workflow that adheres to all architectural principles.

> **Reference:** See the [Producer-Consumer Workflow Pattern](../../Docs_7_Workflow_Canon/PRODUCER_CONSUMER_WORKFLOW_PATTERN.md) document for the authoritative pattern definition.

## Overview of the 5 Phases

1.  **Phase 1: Questionnaire Completion** - Define workflow purpose, source and destination tables
2.  **Phase 2: Consumer Endpoint Construction** - Create CRUD endpoints for user row selection and status updates
3.  **Phase 3: Background Service Implementation** - Build the status monitoring scheduler
4.  **Phase 4: Curation Service Development** - Create the actual data enrichment/processing service
5.  **Phase 5: End-to-End Testing** - Verify the complete workflow

## Phase 1: Questionnaire Completion

The first phase focuses on clearly defining what your workflow is meant to accomplish.

### 1.1 Core Questions

Answer these foundation questions to define your workflow:

| Question                                    | Example Answer       | Your Answer           |
| :------------------------------------------ | :------------------- | :-------------------- |
| **What is the workflow name?** (snake_case) | `contact_extraction` | `{workflow_name}`     |
| What is the purpose of this workflow?       | Extract contacts     |                       |
| What is the source table?                   | `pages`              | `{source_table}`      |
| What is the destination table?              | `contacts`           | `{destination_table}` |

> **CRITICAL**: The workflow name determines ALL naming patterns.
> **Note on Destination Table:** For workflows that update the source table itself (e.g., page curation), the `destination_table` can be listed as `_(Updates source)_`. In later phases, think of placeholders involving 'destination' or 'output' as referring back to the _source table_ being modified by the processing step.

### 1.2 Additional Workflow Details

These questions help refine implementation details:

| Question                                            | Example Answer               | Your Answer |
| :-------------------------------------------------- | :--------------------------- | :---------- |
| Will this have a UI component?                      | Yes                          |             |
| Is this a background-only process?                  | No                           |             |
| Does it update existing records or create new ones? | Creates new records          |             |
| Estimated processing time per record                | > 5 seconds (background)     |             |
| What specific fields from source table are needed?  | page_content, url            |             |
| What verification/validation is required?           | Check for valid email format |             |

## Phase 1 Tasks: Schema Preparation

> **CRITICAL: USE SUPABASE MCP FOR ALL DATABASE SCHEMA CHANGES**
>
> As per the AI Collaboration Constitution (§3), all database schema changes for this project—including creating ENUM types (Sec 1.4), adding or altering columns (Sec 1.3), and creating indexes—**MUST be performed using Supabase MCP (Migrations, Customizations, and Policies)**.
>
> **Supabase MCP** uses natural language to generate PostgreSQL migration files, which can then be executed against the database environment automatically.
>
> **SQL migration files should be created in the `supabase/migrations/` directory** with timestamps in the format `YYYYMMDDHHMMSS_description.sql`.
>
> Ensure all schema changes are logged in your workflow's "Exact Specific Effort" document.

After answering the questionnaire, complete these database schema tasks to prepare for implementation:

### 1.3 Database Schema Requirements

Add the required status fields to the source table:

```sql
-- Add to source table ({source_table})
-- NOTE: Enum types must be created first (see 1.4)

-- User-driven status field (e.g., for selection/rejection)
ALTER TABLE {source_table} ADD COLUMN {workflow_name}_curation_status {workflow_name}curationstatus NOT NULL DEFAULT 'New';

-- Background processing status field (starts NULL, set by API/curation step)
ALTER TABLE {source_table} ADD COLUMN {workflow_name}_processing_status {workflow_name}processingstatus NULL;

-- Optional: Error message field for background processing
ALTER TABLE {source_table} ADD COLUMN {workflow_name}_processing_error TEXT NULL;
```

### 1.4 Required Database Enum Types

Create both enum types in PostgreSQL **(Manual SQL Execution Required)**. Names should match Python class names (CamelCase converted to lowercase).

```sql
-- Curation status enum (user-driven selection/trigger)
-- Example Name: pagecurationstatus
CREATE TYPE {workflow_name}curationstatus AS ENUM ('New', 'Queued', 'Processing', 'Complete', 'Error', 'Skipped');

-- Processing status enum (background processing lifecycle)
-- Example Name: pageprocessingstatus
CREATE TYPE {workflow_name}processingstatus AS ENUM ('Queued', 'Processing', 'Complete', 'Error');
```

> **IMPORTANT:** These standardized enum values should be used consistently across ALL workflows!

#### Verification Queries

After creating your ENUM types and adding columns, use these queries to verify success:

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

> **Reference:** See [Enum Handling Standards](../../Docs_1_AI_GUIDES/27-ENUM_HANDLING_STANDARDS.md) and [Database Enum Isolation](../../Docs_1_AI_GUIDES/29-DATABASE_ENUM_ISOLATION.md).

### 1.5 Python Model and Enum Updates

> **STANDARDIZATION NOTE:** Place workflow enums in the same module as their related models (domain-based placement).
> This approach (model-based placement) is our preferred pattern going forward to support better separation of concerns.
> While you may see legacy enums in `src/models/enums.py` or `src/models/api_models.py`, new workflow status enums should follow the domain-based pattern.

After planning your database schema changes and creating a migration using Supabase MCP, you MUST update the corresponding SQLAlchemy model file. This involves defining the Python Enum classes and adding the new `Column` definitions that match the schema changes you applied through MCP migrations.

```python
# In: src/models/{source_table}.py

from enum import Enum
from typing import Optional # Add Optional if needed for nullable columns
from sqlalchemy import Column, Text # Add other required SQLA types
from sqlalchemy.dialects.postgresql import ENUM as PgEnum # Use PgEnum for DB types
# Import Base, BaseModel, other necessary items...
# from .base import Base, BaseModel

# --- {WorkflowNameTitle} Workflow Enums ---
class {WorkflowName}CurationStatus(str, Enum):
    New = "New"
    Queued = "Queued"
    Processing = "Processing"
    Complete = "Complete"
    Error = "Error"
    Skipped = "Skipped"
    # Add additional values only if absolutely necessary for this specific workflow

class {WorkflowName}ProcessingStatus(str, Enum):
    Queued = "Queued"
    Processing = "Processing"
    Complete = "Complete"  # Standard value across all workflows
    Error = "Error"

# --- Update SQLAlchemy Model ---
class {SourceTableTitle}(Base, BaseModel): # Assuming Base, BaseModel inheritance
    __tablename__ = "{source_table}s" # Or just {source_table} if that\'s the convention

    # ... existing columns ...

    # --- Add New Workflow Columns ---
    {workflow_name}_curation_status = Column(
        PgEnum({WorkflowName}CurationStatus, name="{workflow_name}curationstatus", create_type=False),
        nullable=False,
        server_default={WorkflowName}CurationStatus.New.value,
        index=True # Add index for status filtering
    )

    {workflow_name}_processing_status = Column(
        PgEnum({WorkflowName}ProcessingStatus, name="{workflow_name}processingstatus", create_type=False),
        nullable=True, # Typically nullable, set when curation triggers queueing
        index=True # Add index for scheduler polling
    )

    {workflow_name}_processing_error = Column(
        Text,
        nullable=True
    )

    # ... existing relationships etc. ...
```

> **IMPORTANT NOTE ON `create_type=False`:**
> Since database ENUM types are created and managed manually via SQL (as per project standards outlined in sections 1.3 & 1.4, and the AI Collaboration Constitution), `create_type=False` is **CRITICAL** in your `PgEnum` definitions above. This parameter tells SQLAlchemy _not_ to attempt to create the ENUM type in the database, preventing conflicts with our manual SQL-first approach. Always ensure this is set for ENUMs managed this way.

> **Reference:** See [Enum Handling Standards](../../Docs_1_AI_GUIDES/27-ENUM_HANDLING_STANDARDS.md)

## Phase 2: Consumer Endpoint Construction

This phase creates the API endpoint for user row selection and batch status updates.

> **DUAL-STATUS UPDATE PATTERN**: This is the cornerstone pattern of all workflows. When a user sets the curation status to trigger processing (usually "Queued"), the endpoint MUST ALSO set the processing_status to "Queued" in the same transaction. This producer-consumer pattern is what connects UI actions to background processing.

### 2.1 API Request Schema

Plan the Pydantic request models, typically placed in `src/schemas/`.

**Note:** Conventionally, schemas for workflow-specific actions (like batch status updates) **MUST** be placed in `src/schemas/{workflow_name}.py` as per the `CONVENTIONS_AND_PATTERNS_GUIDE.md` (Section 6). Schemas in `src/schemas/{source_table_name}.py` are for generic, reusable entity schemas.

```python
# Example File: src/schemas/{workflow_name}.py
from typing import List
from uuid import UUID
from pydantic import BaseModel, Field
# Import the CURATION enum from its domain-based location
from src.models.{source_table_name} import {WorkflowNameTitleCase}CurationStatus

# Convention: {WorkflowNameTitleCase}BatchStatusUpdateRequest
# Example Name (for page_curation): PageCurationBatchStatusUpdateRequest
class {WorkflowNameTitleCase}BatchStatusUpdateRequest(BaseModel):
    ids: List[UUID] = Field(..., min_length=1, description="List of one or more {SourceTableTitleCase} UUIDs to update.")
    status: {WorkflowNameTitleCase}CurationStatus = Field(..., description="The target curation status for the selected items.")

# Convention: {WorkflowNameTitleCase}BatchStatusUpdateResponse
# Example Name (for page_curation): PageCurationBatchStatusUpdateResponse
class {WorkflowNameTitleCase}BatchStatusUpdateResponse(BaseModel):
    message: str
    updated_ids: List[UUID]
    # count: int # Or updated_count, ensure consistency with API implementation
```

> **Reference:** See [API Standardization Guide](../../Docs_1_AI_GUIDES/15-API_STANDARDIZATION_GUIDE.md) and Section 6 of `CONVENTIONS_AND_PATTERNS_GUIDE.md`.

### 2.2 API Router Implementation

> **CRITICAL ARCHITECTURE PATTERN: DUAL-STATUS UPDATE**
> The API endpoint must implement the **dual-status update pattern**:
>
> 1. When user sets {workflow_name}\_curation_status to **`{WorkflowNameTitleCase}CurationStatus.Queued`** via the API (as per `CONVENTIONS_AND_PATTERNS_GUIDE.md` Section 2 & 4).
> 2. The endpoint MUST ALSO set {workflow_name}\_processing_status to `{WorkflowNameTitleCase}ProcessingStatus.Queued`.
> 3. This triggers the background scheduler to process this record.
>
> This producer-consumer pattern is fundamental to all workflows and MUST be implemented consistently.

Create/update router, as per `CONVENTIONS_AND_PATTERNS_GUIDE.md` Section 7, typically in `src/routers/{workflow_name}.py`.

> **Note on Router File Location & Naming:** The primary convention for new, workflow-specific routers is `src/routers/{workflow_name}.py`. This router is then typically included in `main.py` with a prefix like `/api/v3/{source_table_plural_name}`.
> **Confirm the desired path, name, and prefixing strategy with the User** if any doubt exists, adhering to the "Zero Assumptions" principle.

> **CRITICAL: Standard FastAPI Session Dependency**
> For injecting the SQLAlchemy `AsyncSession` into your FastAPI endpoints, you **MUST** use the project's standard dependency:

```python
# Example File: src/routers/{workflow_name}.py
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import update # `select` might not be needed for this specific endpoint
from sqlalchemy.ext.asyncio import AsyncSession

from src.session.async_session import get_session_dependency
# Import source model
from src.models.{source_table_name} import {SourceTableTitleCase}
# Import Curation and Processing enums from model file
from src.models.{source_table_name} import {WorkflowNameTitleCase}CurationStatus, {WorkflowNameTitleCase}ProcessingStatus
# Import request and response schemas from their location
from src.schemas.{workflow_name} import {WorkflowNameTitleCase}BatchStatusUpdateRequest, {WorkflowNameTitleCase}BatchStatusUpdateResponse
from src.auth.dependencies import get_current_active_user # Assuming this is the standard auth dep
# from src.auth.jwt_auth import UserInToken # Ensure UserInToken or equivalent is used if get_current_active_user returns it

router = APIRouter() # Example: router = APIRouter()
logger = logging.getLogger(__name__)

# Convention (from CONVENTIONS_AND_PATTERNS_GUIDE.md Sec 7): update_{source_table_name}_status_batch
# Example (for page_curation): update_page_status_batch
# Endpoint path is /status; full path /api/v3/{source_table_plural_name}/status comes from router prefixing.
@router.put("/status", response_model={WorkflowNameTitleCase}BatchStatusUpdateResponse)
async def update_{source_table_name}_status_batch(
    request: {WorkflowNameTitleCase}BatchStatusUpdateRequest,
    session: AsyncSession = Depends(get_session_dependency),
    current_user: UserInToken = Depends(get_current_active_user) # Replace UserInToken with actual type from auth dep
):
    """
    Update the {workflow_name}_curation_status for a batch of {source_table_name}s.

    If the target curation status is '{WorkflowNameTitleCase}CurationStatus.Queued',
    also updates the {workflow_name}_processing_status to '{WorkflowNameTitleCase}ProcessingStatus.Queued'.
    """
    try:
        target_curation_status = request.status
        logger.info(
            f"User {current_user.sub} updating {len(request.ids)} {source_table_name}s "
            f"to curation status {target_curation_status.value}"
        )

        # --- Determine if queueing for background processing is needed ---
        # This MUST use the Queued status for the curation enum as per CONVENTIONS_AND_PATTERNS_GUIDE.md
        should_queue_processing = (target_curation_status == {WorkflowNameTitleCase}CurationStatus.Queued)

        async with session.begin():
            update_values = {
                "{workflow_name}_curation_status": target_curation_status
            }

            if should_queue_processing:
                logger.debug(f"Queueing {source_table_name}s {request.ids} for {workflow_name} processing.")
                update_values["{workflow_name}_processing_status"] = {WorkflowNameTitleCase}ProcessingStatus.Queued
                update_values["{workflow_name}_processing_error"] = None
            else:
                 pass

            stmt = (
                update({SourceTableTitleCase})
                .where({SourceTableTitleCase}.id.in_(request.ids))
                .values(**update_values)
                .returning({SourceTableTitleCase}.id)
            )
            result = await session.execute(stmt)
            updated_ids = result.scalars().all()
            count = len(updated_ids)

            if count != len(request.ids):
                 logger.warning(f"Requested {len(request.ids)} updates, but only {count} were found/updated.")

        response_message = f"Updated {count} {source_table_name} records to curation status '{target_curation_status.value}'."
        if should_queue_processing and count > 0:
             response_message += f" Queued {count} for {workflow_name} processing."

        return {WorkflowNameTitleCase}BatchStatusUpdateResponse(message=response_message, updated_ids=updated_ids)

    except Exception as e:
        logger.exception(
            f"Error updating {source_table_name} status for IDs {request.ids} by user {current_user.sub}: {str(e)}",
            exc_info=True
        )
        raise HTTPException(status_code=500, detail=f"Error updating {source_table_name} status.")

```

### 2.3 Register Router in main.py

Add to `src/main.py` (or your main API router aggregation file, e.g., `src/api.py`). Ensure the router instance you added the endpoint to (from `src/routers/{workflow_name}.py`) is imported.

> **Note on Router Instance and Prefixing Strategy:**
> The router instance (e.g., `{workflow_name}_router` from `src/routers/{workflow_name}.py`) defines endpoints relative to its own path (e.g., `/status`).
> The full path is constructed by how this specific router is included into the main application router or the FastAPI app itself.
> Typically, the main application has a global prefix (e.g., `/api/v3`), and then workflow-specific routers are included with a further prefix related to their primary data entity (e.g., `/{source_table_plural_name}`).
> For a `workflow_name = page_curation` (source table `page`, plural `pages`), if the endpoint is `/status` in `page_curation_router.py`:
>
> - `main_app.include_router(page_curation_router, prefix="/api/v3/pages", tags=["Page Curation | Pages"])` would result in `/api/v3/pages/status`.
> - Alternatively, if you have a central `api_v3_router`:
>   - `main_app.include_router(api_v3_router, prefix="/api/v3")`
>   - `api_v3_router.include_router(page_curation_router, prefix="/pages", tags=["Page Curation | Pages"])` also yields `/api/v3/pages/status`.
>     **Consult existing patterns in `src/main.py` or `src/api.py` and confirm with the User if unsure.**

```python
# In src/main.py or your main API router file (e.g., src/api.py)

# Import the router instance from its workflow-specific file
# Example: from src.routers.page_curation import router as page_curation_router
from src.routers.{workflow_name} import router as {workflow_name}_router # Adjust alias as preferred

# ... FastAPI app (app) or main API router (e.g., api_v3_router) setup ...

# Include the workflow-specific router.
# The prefix here, combined with any app-level prefix, forms the base for the endpoint.
# Example for page_curation (source_table_name 'page', source_table_plural_name 'pages'):
# app.include_router(
#     page_curation_router,
#     prefix="/api/v3/pages", # Forms /api/v3/pages/status for the /status endpoint
#     tags=["PageCuration | Pages"]
# )

app.include_router(
    {workflow_name}_router, # Use the imported router instance
    tags=["{WorkflowNameTitleCase} | {SourceTableTitleCasePlural}"], # Example: "PageCuration | Pages"
    prefix="/api/v3/{source_table_plural_name}" # Example: "/api/v3/pages"
)
```

## Phase 3: Background Service Implementation

This phase creates the monitoring service (scheduler) that checks for records marked 'Queued' (or similar) for processing.

### 3.1 Background Scheduler Implementation

**Producer-Consumer Note:** This scheduler function acts as the **consumer** in the producer-consumer pattern. It polls the `{source_table_name}` table looking for records where the `{workflow_name}_processing_status` field has been set to `{WorkflowNameTitleCase}ProcessingStatus.Queued` (typically triggered by the API endpoint in Phase 2 when an item's curation status becomes `{WorkflowNameTitleCase}CurationStatus.Queued`). It locks a batch of these records, marks their processing status as `{WorkflowNameTitleCase}ProcessingStatus.Processing`, and then calls the dedicated processing service (Phase 4) for each item. Upon successful completion, the processing service will update the status to `{WorkflowNameTitleCase}ProcessingStatus.Completed`. If processing fails for an item, this scheduler attempts to mark the item's status as `{WorkflowNameTitleCase}ProcessingStatus.Error` and record the error message.

Create the scheduler function, typically within `src/services/{workflow_name}_scheduler.py` or added to an existing shared scheduler file.

> **Note on Session Management for Schedulers:**
> Background tasks and schedulers operate outside the FastAPI request lifecycle. Therefore, they **MUST** use a separate mechanism for obtaining database sessions. The project standard is to use `get_background_session` (typically imported from `src.db.session`). This is distinct from `get_session_dependency` used in API endpoints.

```python
# Example File: src/services/{workflow_name}_scheduler.py
import logging
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_background_session
# Import settings for configurable parameters
# from src.config.settings import settings # Uncomment and use for batch size, etc.

# Import source model
from src.models.{source_table_name} import {SourceTableTitleCase}
# Import processing enum from model file
from src.models.{source_table_name} import {WorkflowNameTitleCase}ProcessingStatus
# Import the actual processing function (defined in Phase 4)
from src.services.{workflow_name}_service import process_single_{source_table_name}_for_{workflow_name}

logger = logging.getLogger(__name__)

# SCHEDULER_BATCH_SIZE should be configured in src/config/settings.py and .env.example
# e.g., PAGE_CURATION_SCHEDULER_BATCH_SIZE = settings.PAGE_CURATION_SCHEDULER_BATCH_SIZE (or SCS_...)
SCHEDULER_BATCH_SIZE = 10 # Example: Replace with settings import

# Example Name: process_page_curation_queue
# Convention (CONVENTIONS_AND_PATTERNS_GUIDE.md Sec 8): process_{workflow_name}_queue
async def process_{workflow_name}_queue():
    """
    Scheduler job to find {source_table_name} records queued for {workflow_name} processing
    and trigger the processing for each.
    """
    session: AsyncSession = await get_background_session()
    processed_ids = []
    try:
        async with session.begin():
            # Find records where the PROCESSING status is 'Queued'
            stmt = (
                select({SourceTableTitleCase})
                .where({SourceTableTitleCase}.{workflow_name}_processing_status == {WorkflowNameTitleCase}ProcessingStatus.Queued)
                .with_for_update(skip_locked=True) # Avoid race conditions
                .limit(SCHEDULER_BATCH_SIZE)
            )
            result = await session.execute(stmt)
            records_to_process = result.scalars().all()

            if not records_to_process:
                # logger.debug(f"No {source_table_name}s found queued for {workflow_name} processing.")
                return # Exit early if nothing to do

            record_ids = [record.id for record in records_to_process]
            logger.info(f"Found {len(record_ids)} {source_table_name}s queued for {workflow_name}. Locking and marking as Processing.")

            # Mark the PROCESSING status as 'Processing'
            update_stmt = (
                update({SourceTableTitleCase})
                .where({SourceTableTitleCase}.id.in_(record_ids))
                .values({workflow_name}_processing_status={WorkflowNameTitleCase}ProcessingStatus.Processing)
            )
            await session.execute(update_stmt)
            processed_ids = record_ids # Keep track of IDs to process outside transaction

        # --- Process each record OUTSIDE the initial transaction ---
        logger.info(f"Processing {len(processed_ids)} {source_table_name} records for {workflow_name}...")
        for record_id in processed_ids:
            # Create a new session for each item to isolate transactions
            item_session: AsyncSession = await get_background_session()
            try:
                # Call the actual processing function (defined in Phase 4)
                await process_single_{source_table_name}_for_{workflow_name}(item_session, record_id)
                logger.debug(f"Successfully processed {source_table_name} {record_id} for {workflow_name}.")
            except Exception as item_error:
                # If processing fails, update the specific item's status to Error
                logger.exception(f"Error processing {source_table_name} {record_id} for {workflow_name}: {item_error}", exc_info=True)
                try:
                    async with item_session.begin():
                        error_stmt = (
                            update({SourceTableTitleCase})
                            .where({SourceTableTitleCase}.id == record_id)
                            .values(
                                {workflow_name}_processing_status={WorkflowNameTitleCase}ProcessingStatus.Error,
                                {workflow_name}_processing_error=str(item_error)[:1000] # Truncate error
                            )
                        )
                        await item_session.execute(error_stmt)
                except Exception as update_err:
                     logger.error(f"Failed to update error status for {source_table_name} {record_id}: {update_err}")
            finally:
                 await item_session.close() # Close the item-specific session

    except Exception as main_error:
        logger.exception(f"Error in {workflow_name} scheduler main loop: {main_error}", exc_info=True)
    finally:
        await session.close() # Close the main loop session

# (This setup function belongs in the same file as process_{workflow_name}_queue above)
# from apscheduler.schedulers.asyncio import AsyncIOScheduler # Import if needed
# from src.config.settings import settings # Import if needed
# from src.schedulers import scheduler # Import shared scheduler instance if needed

# def setup_{workflow_name}_scheduler(scheduler: AsyncIOScheduler) -> None:
#     job_id = f"{workflow_name}_scheduler"
#     interval_minutes = getattr(settings, f"{workflow_name.upper()}_SCHEDULER_INTERVAL_MINUTES", 1)
#     scheduler.add_job(...)

```

> **Reference:** See [Scheduled Tasks APScheduler Pattern](../../Docs_1_AI_GUIDES/21-SCHEDULED_TASKS_APSCHEDULER_PATTERN.md), [Shared Scheduler Integration Guide](../../Docs_1_AI_GUIDES/24-SHARED_SCHEDULER_INTEGRATION_GUIDE.md), and [Background Services Architecture](../../Docs_6_Architecture_and_Status/BACKGROUND_SERVICES_ARCHITECTURE.md).

### 3.2 Register Scheduler

As per the `CONVENTIONS_AND_PATTERNS_GUIDE.md` (Section 8), scheduler registration follows a specific pattern for modularity and clarity. Each workflow's scheduler defines its own setup function, which is then called from `src/main.py`.

**Step 1: Define Setup Function in `src/services/{workflow_name}_scheduler.py`**

Add the following setup function to your `src/services/{workflow_name}_scheduler.py` file (the same file where `process_{workflow_name}_queue` is defined).

```python
# In src/services/{workflow_name}_scheduler.py

# (process_{workflow_name}_queue function from Section 3.1 is defined above this)
# ...

from apscheduler.schedulers.asyncio import AsyncIOScheduler # Ensure scheduler instance is accessible
                                                          # Or import the shared scheduler instance if centrally managed, e.g.:
                                                          # from src.schedulers import scheduler
from src.config.settings import settings # For accessing configured intervals, etc.

# Assume 'scheduler' is your globally accessible AsyncIOScheduler instance.
# If it's not passed or imported, this pattern needs adjustment based on how 'scheduler' is shared.
# This example assumes `scheduler` is imported or globally available.
# from src.schedulers import scheduler # Example if scheduler is in src/schedulers.py

def setup_{workflow_name}_scheduler(scheduler: AsyncIOScheduler) -> None:
    """
    Adds the {workflow_name} processing job to the APScheduler instance.
    """
    job_id = f"{workflow_name}_scheduler"
    # Interval should be configured in src/config/settings.py and .env.example
    # e.g., PAGE_CURATION_SCHEDULER_INTERVAL_MINUTES = settings.PAGE_CURATION_SCHEDULER_INTERVAL_MINUTES
    # or using the SCS_ prefix: settings.SCS_PAGE_CURATION_SCHEDULER_INTERVAL_MINUTES
    # Parameter name convention: {WORKFLOW_NAME_UPPERCASE}_SCHEDULER_INTERVAL_MINUTES or SCS_{WORKFLOW_NAME_UPPERCASE}_SCHEDULER_INTERVAL_MINUTES
    interval_minutes = getattr(settings, f"{workflow_name.upper()}_SCHEDULER_INTERVAL_MINUTES", 1) # Default to 1 if not set

    scheduler.add_job(
        process_{workflow_name}_queue, # The async function defined in section 3.1
        trigger='interval',
        minutes=interval_minutes,
        id=job_id,
        replace_existing=True,
        max_instances=1 # Usually 1 to prevent race conditions unless designed for concurrency
    )
    # Use the same logger instance defined earlier in the file
    logger.info(f"Scheduled job '{job_id}' to run every {interval_minutes} minutes.")

```

**Step 2: Call Setup Function from `src/main.py` Lifespan Event**

Import and call your `setup_{workflow_name}_scheduler` function within the `lifespan` context manager in `src/main.py`.

```python
# In src/main.py
import asyncio
import logging # Add logger import
from contextlib import asynccontextmanager
from fastapi import FastAPI

# Import the shared scheduler instance (ensure it's initialized before use)
from src.schedulers import scheduler # Assuming your scheduler instance is here

# Import your workflow-specific scheduler setup function
# Example: from src.services.page_curation_scheduler import setup_page_curation_scheduler
from src.services.{workflow_name}_scheduler import setup_{workflow_name}_scheduler

# ... other imports ...

logger = logging.getLogger(__name__) # Initialize logger for lifespan

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting scheduler...")
    try:
        scheduler.start()
    except Exception as e:
        logger.exception(f"Failed to start scheduler: {e}")
        # Decide if application should proceed without scheduler

    # Register workflow-specific jobs
    try:
        setup_{workflow_name}_scheduler(scheduler) # Pass the scheduler instance
        # ... register other workflow schedulers here ...
        logger.info("Scheduler jobs registered.")
    except Exception as e:
        logger.exception("Failed to register scheduler jobs.")

    yield

    # Shutdown
    logger.info("Shutting down scheduler...")
    if scheduler.running:
        try:
            # Attempt a graceful shutdown with a timeout
            scheduler.shutdown(wait=True) # Set wait=True to allow jobs to complete
            logger.info("Scheduler shut down gracefully.")
        except (asyncio.CancelledError, TimeoutError):
            logger.warning("Scheduler shutdown timed out or was cancelled. Forcing shutdown.")
            scheduler.shutdown(wait=False) # Force shutdown
        except Exception as e:
            logger.error(f"Error during scheduler shutdown: {e}")
            scheduler.shutdown(wait=False) # Force shutdown on other errors
    else:
        logger.info("Scheduler was not running.")

# Initialize FastAPI app with lifespan manager
app = FastAPI(lifespan=lifespan)

# ... rest of your main.py (routers, etc.) ...

```

**Note:** The `minutes=1` default interval in `add_job` is an example. Determine the appropriate frequency based on workflow needs and performance impact. This **MUST** be configured via `settings` as shown.

> **Reference:** See [Scheduler and Settings Patterns](../../Docs_1_AI_GUIDES/28-SCHEDULER_AND_SETTINGS_PATTERNS.md) and Section 8 of `CONVENTIONS_AND_PATTERNS_GUIDE.md`.

## Phase 4: Curation Service Development

This phase implements the core data enrichment or processing functionality called by the scheduler.

### 4.1 Data Enrichment/Processing Service

Create the service function, typically in `src/services/{workflow_name}_service.py`.

**Transactional Boundary Note:** The `async with session.begin():` block ensures that all database updates within Step 3 (e.g., setting status to Completed, creating new records) are committed together. If any error occurs within this block, the transaction is automatically rolled back, maintaining data consistency.

**Resource Management Note:** The database session is managed by the calling scheduler function. If your custom processing logic in Step 2 (`perform_custom_extraction`) acquires other resources (e.g., network connections, file handles), ensure they are properly closed or released, potentially using context managers (`async with ...`), even if errors occur.

**External Integration Note:** If Step 2 involves calls to external services or APIs, implement robust error handling, appropriate timeouts, and consider patterns like retries (with backoff) or circuit breakers for resilience. Handle external errors gracefully to allow the workflow to mark the item as Error if necessary.

```python
# Example File: src/services/{workflow_name}_service.py
import logging
from uuid import UUID
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

# Import source model
from src.models.{source_table_name} import {SourceTableTitleCase}
# Import processing enum from model file
from src.models.{source_table_name} import {WorkflowNameTitleCase}ProcessingStatus
# If creating new records (Option B), import destination model and its TitleCase version:
# from src.models.{destination_table_name} import {DestinationTableTitleCase}

logger = logging.getLogger(__name__)

# Convention (CONVENTIONS_AND_PATTERNS_GUIDE.md Sec 8): process_single_{source_table_name}_for_{workflow_name}
# Example Name (page_curation): process_single_page_for_page_curation
async def process_single_{source_table_name}_for_{workflow_name}(
    session: AsyncSession, # Note: Session is passed in from scheduler
    record_id: UUID,
) -> None:
    """
    Processes a single {source_table_name} record for the {workflow_name} workflow.
    Handles transaction management for this specific record.
    """
    try:
        # --- Step 1: Retrieve the source record ---
        # No need for transaction here, retrieval only
        stmt = select({SourceTableTitleCase}).where({SourceTableTitleCase}.id == record_id)
        result = await session.execute(stmt)
        source_record = result.scalars().first()

        if not source_record:
            logger.warning(f"{workflow_name} processing: {SourceTableTitleCase} with ID {record_id} not found.")
            return # Exit if record vanished

        # IMPORTANT Idempotency Check:
        if source_record.{workflow_name}_processing_status != {WorkflowNameTitleCase}ProcessingStatus.Processing:
            logger.warning(f"{workflow_name} processing: {SourceTableTitleCase} {record_id} status changed "
                           f"to {source_record.{workflow_name}_processing_status}. Skipping.")
            return

        # --- Step 2: Perform the actual data enrichment/processing ---
        logger.debug(f"Performing {workflow_name} processing for {source_table_name} {record_id}...")
        # extracted_data = await perform_custom_extraction(source_record) # Example call

        # --- Step 3: Update status and/or create output records ---
        async with session.begin(): # Start transaction for final updates

            # --- Option A: Update Source Table (e.g., Page Curation) ---
            logger.debug(f"Updating {source_table_name} {record_id} status to Completed for {workflow_name}.")
            final_update_stmt = (
                update({SourceTableTitleCase})
                .where({SourceTableTitleCase}.id == record_id)
                .values(
                    {workflow_name}_processing_status={WorkflowNameTitleCase}ProcessingStatus.Completed,
                    {workflow_name}_processing_error=None
                    # Optionally update curation status too if needed, e.g., for a `{WorkflowNameTitleCase}CurationStatus.Processed` state
                    # {workflow_name}_curation_status = {WorkflowNameTitleCase}CurationStatus.Processed
                )
            )
            await session.execute(final_update_stmt)

            # --- Option B: Create New Records in Destination Table (e.g., Contact Extraction) ---
            # // Ensure {DestinationTableTitleCase} and {destination_table_name} are defined if using this option.
            # logger.debug(f"Creating {destination_table_name} records for {source_table_name} {record_id}...")
            # for item_data in extracted_data:
            #     new_record = {DestinationTableTitleCase}(
            #         id=uuid.uuid4(),
            #         {source_table_name}_id=record_id,
            #         **item_data
            #     )
            #     session.add(new_record)
            #
            # final_update_stmt_option_b = (
            #     update({SourceTableTitleCase})
            #     .where({SourceTableTitleCase}.id == record_id)
            #     .values(
            #         {workflow_name}_processing_status={WorkflowNameTitleCase}ProcessingStatus.Completed,
            #         {workflow_name}_processing_error=None
            #     )
            # )
            # await session.execute(final_update_stmt_option_b)
            # --- End Option B ---

    except Exception as e:
        logger.error(f"Error during process_single_{source_table_name}_for_{workflow_name} for ID {record_id}: {e}")
        raise

# --- Helper function for custom logic ---
# async def perform_custom_extraction(source_record: {SourceTableTitleCase}) -> List[Dict]:
#     # Implement your specific extraction/processing logic here.
#     return []
```

> **Reference:** See [Absolute ORM Requirement](../../Docs_1_AI_GUIDES/01-ABSOLUTE_ORM_REQUIREMENT.md), [Core Architectural Principles - Error Handling](../../Docs_1_AI_GUIDES/17-CORE_ARCHITECTURAL_PRINCIPLES.md#6-error-handling), and [Transaction Management Guide](../../Docs_1_AI_GUIDES/13-TRANSACTION_MANAGEMENT_GUIDE.md).

## Phase 4.5: Frontend Components (if UI-driven)

_(Moved from Phase 2 as UI is often built after API)_

If the workflow involves user interaction, create the necessary frontend components.

### 4.5.1 HTML Tab

Add to `templates/scraper-sky-mvp.html`:

```html
<!-- Example ID: page-curation-tab -->
<div class="tab-pane" id="{workflow_name}-tab">
  <!-- This ID should align with the tab button's data-panel attribute -->
  <div class="container">
    <div class="row mt-3">
      <div class="col-12">
        <!-- Example Title: Page Curation Management -->
        <h4>{WorkflowNameTitleCase} Management</h4>
        <div class="card">
          <div class="card-header bg-primary text-white">
            {SourceTableTitleCase} Selection
          </div>
          <div class="card-body">
            <!-- Table ID Convention: {workflowNameCamelCase}Table -->
            <!-- Example (page_curation): pageCurationTable -->
            <table id="{workflowNameCamelCase}Table" class="table table-striped">
              <thead>
                <tr>
                  <th>
                    <!-- Select All Checkbox ID Convention: selectAll{WorkflowNameTitleCase}Checkbox -->
                    <!-- Example (page_curation): selectAllPageCurationCheckbox -->
                    <input
                      type="checkbox"
                      id="selectAll{WorkflowNameTitleCase}Checkbox"
                    />
                  </th>
                  <th>ID</th>
                  <th>{WorkflowNameTitleCase} Curation Status</th>
                  <th>{WorkflowNameTitleCase} Processing Status</th>
                  <!-- Add other relevant fields -->
                </tr>
              </thead>
              <!-- Table Body ID Convention: {workflowNameCamelCase}TableBody -->
              <!-- Example (page_curation): pageCurationTableBody -->
              <tbody id="{workflowNameCamelCase}TableBody">
                <!-- Rows will be populated by JavaScript -->
              </tbody>
            </table>
          </div>
          <div class="card-footer">
            <!-- Button IDs should be descriptive. For more complex batch forms, see CONVENTIONS_AND_PATTERNS_GUIDE.md Sec 2 -->
            <!-- Example ID (for page_curation): update-pages-status-queued -->
            <button
              id="update-{source_table_plural_name}-status-queued"
              <!--
              Recommended
              id
              for
              the
              primary
              trigger
              button
              --
            >
              class="btn btn-success" > Queue Selected for Processing
            </button>
            <!-- Example ID: update-pages-status-skipped -->
            <button
              id="update-{source_table_plural_name}-status-skipped"
              class="btn btn-warning"
            >
              Mark Skipped
            </button>
            <!-- Add other action buttons as needed, using status values from {WorkflowNameTitleCase}CurationStatus -->
            <!-- e.g., id="update-{source_table_plural_name}-status-error" -->
          </div>
        </div>
      </div>
    </div>
  </div>
</div>
```

### 4.5.2 JavaScript File

Create in `static/js/{workflow_name_kebab_case}-tab.js` (e.g., for `page_curation`, this would be `page-curation-tab.js`).
Ensure all DOM selectors precisely match the HTML IDs defined in section 4.5.1 and follow conventions from `CONVENTIONS_AND_PATTERNS_GUIDE.md` Section 2 & 3.

```javascript
// Example File: static/js/page-curation-tab.js (using page_curation as example for placeholders)
$(document).ready(function () {
  // These should be derived from your workflow_name and source_table_name
  const workflowName = "{workflow_name}"; // E.g., "page_curation"
  const workflowNameCamelCase = "{workflowNameCamelCase}"; // E.g., "pageCuration"
  const workflowNameTitleCase = "{WorkflowNameTitleCase}"; // E.g., "PageCuration"
  const sourceTablePlural = "{source_table_plural_name}"; // E.g., "pages"

  const curationStatusEnum = {
    // These values MUST match the Python Enum members for {WorkflowNameTitleCase}CurationStatus
    New: "New",
    Queued: "Queued", // This status typically triggers processing
    Processing: "Processing", // Usually set by backend, may not be user-settable
    Complete: "Complete", // Usually set by backend
    Error: "Error", // Can be backend or user-settable
    Skipped: "Skipped", // Common user action
  };

  // DOM Element Selectors (must match HTML IDs from 4.5.1 and CONVENTIONS_AND_PATTERNS_GUIDE.md)
  const tableBody = $(`#${workflowNameCamelCase}TableBody`); // E.g., #pageCurationTableBody
  const selectAllCheckbox = $(`#selectAll${workflowNameTitleCase}Checkbox`); // E.g., #selectAllPageCurationCheckbox
  const itemCheckboxClass = `${workflowNameCamelCase}-item-checkbox`; // E.g., pageCuration-item-checkbox

  // Button Selectors (must match HTML IDs)
  const queueSelectedBtn = $(`#update-${sourceTablePlural}-status-queued`);
  const markSkippedBtn = $(`#update-${sourceTablePlural}-status-skipped`);
  // ... add selectors for other status buttons as defined in HTML

  // --- Load initial data ---
  function loadData() {
    // API endpoint to list items. Adjust if your list endpoint is different.
    // Consider adding query parameters for initial filtering (e.g., ?{workflow_name}_curation_status=New)
    $.ajax({
      url: `/api/v3/${sourceTablePlural}/list`, // Standard list endpoint for the source table
      type: "GET",
      // Add headers for auth if needed: headers: { "Authorization": "Bearer " + getJwtToken() },
      success: function (response) {
        populateTable(response.items || []); // Adjust based on your API list response structure
        selectAllCheckbox.prop("checked", false); // Reset select all
      },
      error: function (error) {
        showNotification(
          "Error",
          `Failed to load ${sourceTablePlural} data. Check console for details.`
        );
        console.error("Load error:", error);
      },
    });
  }

  // --- Populate Table ---
  function populateTable(items) {
    tableBody.empty();
    if (!items || items.length === 0) {
      // Adjust colspan to match the number of columns in your table
      tableBody.append(
        `<tr><td colspan="4">No items found for ${workflowName} workflow.</td></tr>`
      );
      return;
    }
    items.forEach((item) => {
      const curationStatus =
        item[`${workflow_name}_curation_status`] || curationStatusEnum.New;
      const processingStatus = item[`${workflow_name}_processing_status`] || "N/A";
      tableBody.append(`
        <tr>
            <td><input type="checkbox" class="${itemCheckboxClass}" data-id="${item.id}"></td>
            <td>${item.id}</td>
            <td>${curationStatus}</td>
            <td>${processingStatus}</td>
            <!-- Add other relevant <td> elements for fields from your item -->
        </tr>
      `);
    });
  }

  // --- Get Selected IDs ---
  function getSelectedIds() {
    return $(`.${itemCheckboxClass}:checked`)
      .map(function () {
        return $(this).data("id");
      })
      .get();
  }

  // --- Update Status Function ---
  function updateStatus(newCurationStatusValue) {
    const selectedIds = getSelectedIds();
    if (selectedIds.length === 0) {
      showNotification("Warning", "Please select at least one item.");
      return;
    }

    // API endpoint for batch status update (Corrected to align with Phase 2.2 conventions)
    const apiUrl = `/api/v3/${sourceTablePlural}/status`;

    $.ajax({
      url: apiUrl,
      type: "PUT",
      contentType: "application/json",
      // Add headers for auth if needed: headers: { "Authorization": "Bearer " + getJwtToken() },
      data: JSON.stringify({
        ids: selectedIds,
        status: newCurationStatusValue, // Send the target {WorkflowNameTitleCase}CurationStatus string value
      }),
      success: function (response) {
        showNotification("Success", response.message || "Status updated successfully");
        loadData(); // Refresh the table
      },
      error: function (error) {
        const errorMsg =
          error.responseJSON?.detail ||
          `Failed to update status to ${newCurationStatusValue}. Check console.`;
        showNotification("Error", errorMsg);
        console.error("Update error:", error);
      },
    });
  }

  // --- Event Handlers ---
  selectAllCheckbox.on("click", function () {
    $(`.${itemCheckboxClass}`).prop("checked", $(this).prop("checked"));
  });

  queueSelectedBtn.on("click", function () {
    // For the main action that queues items for processing, use the "Queued" status.
    updateStatus(curationStatusEnum.Queued);
  });

  markSkippedBtn.on("click", function () {
    updateStatus(curationStatusEnum.Skipped);
  });

  // Add handlers for other buttons, ensuring the status string matches a valid CurationStatus Enum member...
  // Example for an "Error" button:
  // $(`#update-${sourceTablePlural}-status-error`).on("click", function () {
  //   updateStatus(curationStatusEnum.Error);
  // });

  // --- Initial Load ---
  loadData();
});

// --- Simple Notification Helper ---
function showNotification(title, message) {
  // Replace with a more sophisticated notification system if available (e.g., Toastr, SweetAlert)
  console.log(`Notification - ${title}: ${message}`);
  alert(`${title}: ${message}`); // Simple alert for example purposes
}
```

> **Reference:** See [Curation Workflow Operating Manual](../../Docs_6_Architecture_and_Status/0.4_Curation%20Workflow%20Operating%20Manual.md) for frontend integration patterns.

## Phase 5: End-to-End Testing

The final phase validates that all components work together correctly.

### 5.1 Testing Checklist & Methodology

Develop a comprehensive testing strategy covering unit, integration, and end-to-end tests where appropriate. Focus on verifying the interactions between components (API, Scheduler, Service) and correct state transitions.

**Overall Checklist:**

- [ ] Database schema changes are correctly applied (Verified via migrations and/or direct inspection)
- [ ] API endpoints function correctly (contract, validation, responses) (Integration/API tests)
- [ ] Frontend UI displays correctly and interacts with API as expected (Manual testing, E2E tests if applicable)

**Incremental Testing Methodology (as per project standards):**

1.  **Component Isolation**

    - [ ] Service functions testable in isolation
    - [ ] Mock external dependencies

2.  **Progressive Testing Sequence**

    - [ ] Foundation: Test with minimal valid data
    - [ ] Component: Test individual service/scheduler functions
    - [ ] Integration: Test API → DB → Scheduler → Service chain
    - [ ] End-to-End: Manual verification via UI

3.  **Required Test Coverage (refer to `CONVENTIONS_AND_PATTERNS_GUIDE.md` Section 12):**

    - [ ] Service logic in `tests/services/test_{workflow_name}_service.py`
    - [ ] Scheduler logic in `tests/scheduler/test_{workflow_name}_scheduler.py`
    - [ ] End-to-end workflow in `tests/workflows/test_{workflow_name}_workflow.py` (Component Flow Test)
    - [ ] API endpoints in `tests/routers/test_{workflow_name}_router.py`

4.  **Verification Checklist (Detailed):**
    - [ ] Background scheduler correctly polls, locks, and triggers processing (Integration tests, log verification)
    - [ ] Processing service executes custom logic and updates status accurately (Unit/Integration tests)
    - [ ] Status fields transition correctly through the entire workflow cycle (API -> Queued -> Processing -> Completed/Error) (Integration tests, manual E2E tests)
    - [ ] Error handling mechanisms (API, Scheduler, Service) function as designed (Integration tests for failure scenarios)
    - [ ] Idempotency checks prevent duplicate processing (Integration tests with simulated retries/duplicates)

### 5.2 Test Cases (Example using Pytest)

Create tests in `tests/` directory, following naming conventions from `CONVENTIONS_AND_PATTERNS_GUIDE.md` Section 12.

```python
# Example File: tests/workflows/test_{workflow_name}_workflow.py (for end-to-end component flow)
# Or tests/services/test_{workflow_name}_service.py (for service unit/integration tests)
import pytest
from httpx import AsyncClient
from uuid import uuid4, UUID

# Assuming FastAPI app instance is accessible, e.g., from src.main import app if needed for client
# from src.main import app

# Import source model, e.g., from src.models.page import Page
from src.models.{source_table_name} import {SourceTableTitleCase}
# Import enums from model file, e.g., from src.models.page import PageCurationStatus, PageProcessingStatus
from src.models.{source_table_name} import {WorkflowNameTitleCase}CurationStatus, {WorkflowNameTitleCase}ProcessingStatus

# Import test utilities, fixtures (e.g., db_session, async_client, create_test_{source_table_name})
# These would typically be in tests/conftest.py or workflow-specific test files

# Example Test: API Endpoint & Dual-Status Update (Component Flow Test style)
@pytest.mark.asyncio
async def test_{workflow_name}_api_status_update_and_queueing(
    async_client: AsyncClient,
    db_session # Assuming a fixture that provides a test DB session
):
    # Setup: Create a test {source_table_name} record in the 'New' state
    # Example: test_record = await create_test_page(db_session, page_curation_status=PageCurationStatus.New)
    # Assumes a helper fixture `create_test_{source_table_name}` exists
    test_record = await create_test_{source_table_name}(
        db_session,
        {workflow_name}_curation_status={WorkflowNameTitleCase}CurationStatus.New
    )
    test_id = test_record.id

    # Execute: Call API to update status to trigger queueing (e.g., 'Queued')
    # API path should match Phase 2.2: /api/v3/{source_table_plural_name}/status
    response = await async_client.put(
        f"/api/v3/{source_table_plural_name}/status",
        json={"ids": [str(test_id)], "status": {WorkflowNameTitleCase}CurationStatus.Queued.value}
    )

    # Verify: API Response
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["message"].startswith("Updated 1") # Or check updated_ids based on your response schema
    assert str(test_id) in response_data["updated_ids"] # Assumes response schema includes updated_ids

    # Verify: Database State after API call
    await db_session.refresh(test_record) # Refresh object state from DB
    assert test_record.{workflow_name}_curation_status == {WorkflowNameTitleCase}CurationStatus.Queued
    assert test_record.{workflow_name}_processing_status == {WorkflowNameTitleCase}ProcessingStatus.Queued # Critical dual-status check
    assert test_record.{workflow_name}_processing_error is None

# Example Test: Processing Service Logic (Happy Path - Update Source)
@pytest.mark.asyncio
async def test_{workflow_name}_service_processing_success(
    db_session # Assuming a fixture
):
    # Import the service function to test directly
    from src.services.{workflow_name}_service import process_single_{source_table_name}_for_{workflow_name}

    # Setup: Create a record ready for processing (status already marked as 'Processing' by a hypothetical scheduler step)
    # Example: test_record = await create_test_page(db_session, page_processing_status=PageProcessingStatus.Processing)
    # Assumes a helper fixture `create_test_{source_table_name}` exists
    test_record = await create_test_{source_table_name}(
        db_session,
        {workflow_name}_curation_status={WorkflowNameTitleCase}CurationStatus.Queued, # Initial state before processing
        {workflow_name}_processing_status={WorkflowNameTitleCase}ProcessingStatus.Processing, # Simulate scheduler having marked it
        # Add any other required fields for processing logic
    )
    test_id = test_record.id

    # Execute: Call the processing function directly
    await process_single_{source_table_name}_for_{workflow_name}(db_session, test_id)

    # Verify: Database State after service execution
    await db_session.refresh(test_record)
    assert test_record.{workflow_name}_processing_status == {WorkflowNameTitleCase}ProcessingStatus.Completed
    assert test_record.{workflow_name}_processing_error is None
    # Optionally check curation status if it should change (e.g., to a 'Processed' state if one exists):
    # assert test_record.{workflow_name}_curation_status == {WorkflowNameTitleCase}CurationStatus.Processed

# --- Add More Granular Tests for Error Handling and Edge Cases ---

# Example: Test API with invalid input (e.g., bad UUID, invalid status value)
# async def test_{workflow_name}_api_invalid_input(async_client: AsyncClient, db_session):
#   - Setup: Prepare invalid request payload (e.g., non-UUID string in ids, status value not in Enum).
#   - Execute: Call API with invalid data.
#   - Verify: Assert appropriate 422 Unprocessable Entity error response.
#   - Verify: Ensure no changes were made to the database for valid IDs that might have been included.

# Example: Test Service Processing Failure (e.g., custom logic raises an exception)
# @pytest.mark.asyncio
# async def test_{workflow_name}_service_processing_error(db_session, mocker):
#   - Setup: Create a record ready for processing.
#   - Mock the custom extraction/processing logic (e.g., `perform_custom_extraction`) to raise an exception.
#     # e.g., mocker.patch('src.services.{workflow_name}_service.perform_custom_extraction', side_effect=ValueError("Test processing error"))
#   - Execute: Call `process_single_{source_table_name}_for_{workflow_name}`.
#   - Verify: Assert the specific exception is raised (as expected by scheduler to catch and handle).
#   - Verify: Check the record status in the DB; it should still be 'Processing' as the service function failed before completing the final update transaction.

# Example: Test Scheduler Logic (Conceptual - involves mocking the processing service call)
# @pytest.mark.asyncio
# async def test_{workflow_name}_scheduler_finds_and_processes(db_session, mocker):
#   - Setup: Create records with `{workflow_name}_processing_status` as 'Queued'.
#   - Mock `src.services.{workflow_name}_service.process_single_{source_table_name}_for_{workflow_name}` to simulate success or failure.
#     # e.g., mock_process = mocker.patch('src.services.{workflow_name}_scheduler.process_single_{source_table_name}_for_{workflow_name}')
#     # If testing error handling, use: mock_process.side_effect = ValueError("Simulated processing error")
#   - Execute: Call `process_{workflow_name}_queue` (from the scheduler module).
#   - Verify: Check that records were updated to 'Processing' in the DB by the scheduler initially.
#   - Verify: Assert that the mocked `process_single...` was called with the correct record IDs.
#   - Verify (if mocking success): The scheduler loop should complete without error.
#   - Verify (if mocking failure): Check logs for scheduler catching the error; check DB to ensure scheduler marked the item as 'Error' and recorded the error message.

# Add more tests for different statuses, idempotency scenarios (e.g., calling process_single twice for same ID), etc.
```

**Mocking Note:** If your processing service relies on external dependencies (e.g., APIs, libraries), use mocking libraries (like `pytest-mock` or `unittest.mock`) to isolate your service logic during unit/integration testing.

> **Reference:** See [Comprehensive Test Plan](../../Docs_1_AI_GUIDES/06-COMPREHENSIVE_TEST_PLAN.md) and `CONVENTIONS_AND_PATTERNS_GUIDE.md` Section 12 for detailed testing strategies and fixture guidance.

### 5.3 Manual Testing Procedure

1.  **Setup:** Start the application (e.g., `docker-compose up`). Ensure the scheduler is enabled. Prepare test data (identify/create source records in 'New' status using the UI or direct DB manipulation if needed).

2.  **Trigger:** Navigate to the workflow tab in the UI (e.g., `/static/scraper-sky-mvp.html`). Use the UI buttons to select items and update their curation status to trigger processing (typically by setting to `Queued`).

3.  **Verify API/UI:** Confirm UI table updates (curation status to `Queued`, processing status should also become `Queued` almost immediately due to dual-status update). Check browser console/network tab for successful API response from the `/status` endpoint.

4.  **Verify Scheduler Pickup:** Monitor application logs (`docker-compose logs -f app` or similar). Look for logs indicating the `{workflow_name}_scheduler` (specifically `process_{workflow_name}_queue` function) found items (IDs) and marked their `processing_status` as `Processing`.

5.  **Verify Service Execution:** Look for logs from `process_single_{source_table_name}_for_{workflow_name}` indicating it started and completed successfully for the item IDs.

6.  **Verify Final State (Happy Path):** Refresh UI or check DB directly. Confirm `{workflow_name}_processing_status` is `Completed` and `{workflow_name}_processing_error` field is null/empty. The `{workflow_name}_curation_status` should remain as `Queued` (or whatever triggered processing) unless the service logic explicitly changes it to another terminal state like `Processed` (if such a state exists in your CurationStatus enum).

7.  **Test Error Path:** If possible, introduce a condition that would cause `process_single_{source_table_name}_for_{workflow_name}` to raise an error for a test item. Trigger this item for processing.

    - Verify logs show the error being caught by the scheduler's item processing loop.
    - Verify the item's `{workflow_name}_processing_status` updates to `Error` in the DB/UI.
    - Verify the error message is recorded in the `{workflow_name}_processing_error` field.

8.  **Test Other Curation Paths:** Use UI buttons for other curation statuses (e.g., `Skipped`, `Error` if user-settable, or any custom terminal states you might have). Verify the correct `{workflow_name}_curation_status` is set and that these do not incorrectly trigger the `{workflow_name}_processing_status` to `Queued` (unless that is intended design for a specific status).

### 5.4 Final Documentation Considerations (Optional)

- Document any specific failure modes identified during testing and the expected manual or automated recovery procedures.
- Consider creating a simple state machine diagram illustrating the `{workflow_name}_curation_status` and `{workflow_name}_processing_status` transitions, including how they interact.
- If this workflow produces data for or consumes data from other workflows, ensure these relationships are documented in the "Cross-Workflow References" section at the end of this cheat sheet and in relevant Canonical YAMLs.

## Implementation Checklist

Use this checklist during and after implementation:

- [ ] **Phase 1: Definition & Schema**
  - [ ] Workflow purpose and tables defined (Questionnaire 1.1, 1.2)
  - [ ] Database enum types created manually (SQL 1.4)
  - [ ] Status fields added to source table via migration (SQL 1.3)
  - [ ] Python enum classes defined in codebase (Python 1.5)
- [ ] **Phase 2: Consumer Endpoint**
  - [ ] API request schema created (Python 2.1)
  - [ ] Router endpoint implemented with dual-status logic (Python 2.2)
  - [ ] Router registered in main.py (Python 2.3)
- [ ] **Phase 3: Background Service**
  - [ ] Scheduler function implemented (locking, marking, calling service) (Python 3.1)
  - [ ] Scheduler job registered in schedulers.py (Python 3.2)
- [ ] **Phase 4: Curation Service**
  - [ ] Processing service function implemented (retrieval, custom logic, final status update) (Python 4.1)
  - [ ] Logic correctly handles update-source vs create-destination pattern
- [ ] **Phase 4.5: Frontend Components (if UI-driven)**
  - [ ] HTML tab structure added (HTML 4.5.1)
  - [ ] JavaScript logic implemented for loading, selection, and API calls (JS 4.5.2)
- [ ] **Phase 5: Testing**
  - [ ] Unit/Integration tests created for API and service logic (Pytest 5.2)
  - [ ] Manual testing procedure completed (Checklist 5.3)
  - [ ] Error scenarios tested

## Additional Resources

- [Standard Curation Workflow Blueprint](../../Docs_7_Workflow_Canon/BP-01-Standard_Curation_Workflow.md)
- [Curation Workflow Cookbook](<../../Docs_6_Architecture_and_Status/0.5_Curation%20Workflow%20Cookbook%20(Developer%20On%E2%80%91Ramping%20Guide).md>)
- [Architecture Flow and Components](../../Docs_6_Architecture_and_Status/0.1_ScraperSky_Architecture_Flow_and_Components.md)
- [Background Service Pattern and Router Crosswalk](../../Docs_6_Architecture_and_Status/BACKGROUND_SERVICE_PATTERN_AND_ROUTER_CROSSWALK.md)
- [Core Architectural Principles](../../Docs_1_AI_GUIDES/17-CORE_ARCHITECTURAL_PRINCIPLES.md)
- _Link to a state machine diagram for this workflow (if available/created)_

## Cross-Workflow References

If this workflow is part of a larger producer-consumer chain, document the relationships here:

- **Upstream Producers:** _List any workflows that produce items consumed by this workflow_
- **Downstream Consumers:** _List any workflows that consume items produced by this workflow_
