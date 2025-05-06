# ScraperSky Workflow Builder Cheat Sheet (Revised)

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

> **Reference:** See [Database Schema Change Guide](../../Docs_1_AI_GUIDES/18-DATABASE_SCHEMA_CHANGE_GUIDE.md)

### 1.4 Required Database Enum Types

Create both enum types in PostgreSQL **(Manual SQL Execution Required)**. Names should match Python class names (CamelCase converted to lowercase).

```sql
-- Curation status enum (user-driven selection/trigger)
-- Example Name: pagecurationstatus
CREATE TYPE {workflow_name}curationstatus AS ENUM ('New', 'Selected', 'Rejected', 'Archived'); -- Adjust values as needed

-- Processing status enum (background processing lifecycle)
-- Example Name: pageprocessingstatus
CREATE TYPE {workflow_name}processingstatus AS ENUM ('Queued', 'Processing', 'Completed', 'Error');
```

> **Reference:** See [Enum Handling Standards](../../Docs_1_AI_GUIDES/27-ENUM_HANDLING_STANDARDS.md) and [Database Enum Isolation](../../Docs_1_AI_GUIDES/29-DATABASE_ENUM_ISOLATION.md).

### 1.5 Python Enum Definitions

Create/update enum classes, typically in `src/models/enums.py`. Use CamelCase class names matching the workflow.

```python
from enum import Enum

# Example Name: PageCurationStatus
class {WorkflowName}CurationStatus(str, Enum):
    New = "New"
    Selected = "Selected" # Often triggers 'Queued' for processing status
    Rejected = "Rejected"
    Archived = "Archived"
    # Add other values as defined in DB Enum

# Example Name: PageProcessingStatus
class {WorkflowName}ProcessingStatus(str, Enum):
    Queued = "Queued"
    Processing = "Processing"
    Completed = "Completed"
    Error = "Error"
```

> **Reference:** See [Enum Handling Standards](../../Docs_1_AI_GUIDES/27-ENUM_HANDLING_STANDARDS.md)

## Phase 2: Consumer Endpoint Construction

This phase creates the API endpoint for user row selection and batch status updates.

### 2.1 API Request Schema

Create request models in `src/schemas/`.

```python
# Example File: src/schemas/{source_table}.py or src/schemas/{workflow_name}.py
from typing import List
from uuid import UUID
from pydantic import BaseModel
from src.models.enums import {WorkflowName}CurationStatus # Import from correct location

# Example Name: PageBatchStatusUpdateRequest
class {SourceTableTitle}BatchStatusUpdateRequest(BaseModel):
    ids: List[UUID]
    status: {WorkflowName}CurationStatus # Use the CURATION status enum here
```

> **Reference:** See [API Standardization Guide](../../Docs_1_AI_GUIDES/15-API_STANDARDIZATION_GUIDE.md)

### 2.2 API Router Implementation

Create/update router, typically in `src/routers/{source_table}s.py`.

```python
# Example File: src/routers/{source_table}s.py
import logging
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_session_dependency
from src.models.{source_table} import {SourceTableTitle} # Import source model
# Import BOTH curation and processing enums
from src.models.enums import {WorkflowName}CurationStatus, {WorkflowName}ProcessingStatus
from src.schemas.{source_table} import {SourceTableTitle}BatchStatusUpdateRequest # Import request schema
from src.schemas.response import GenericResponse
from src.auth.jwt_auth import UserInToken, get_current_user

# Ensure router instance exists (or create it)
# router = APIRouter()
logger = logging.getLogger(__name__)

# Example Name: update_page_status_batch
@router.put("/api/v3/{source_table}s/status", response_model=GenericResponse) # Adjust URL as needed
async def update_{source_table}_status_batch(
    request: {SourceTableTitle}BatchStatusUpdateRequest,
    session: AsyncSession = Depends(get_session_dependency),
    current_user: UserInToken = Depends(get_current_user),
):
    """
    Update the {workflow_name}_curation_status for a batch of {source_table}s.

    If the target curation status triggers processing (e.g., 'Selected'),
    also updates the {workflow_name}_processing_status to 'Queued'.
    """
    try:
        target_curation_status = request.status
        logger.info(
            f"User {current_user.sub} updating {len(request.ids)} {source_table}s "
            f"to curation status {target_curation_status.value}"
        )

        # --- Determine if queueing for background processing is needed ---
        # Adjust condition as needed (e.g., might be 'Queued' status instead of 'Selected')
        should_queue_processing = (target_curation_status == {WorkflowName}CurationStatus.Selected)

        async with session.begin():
            # Base update values: Update the CURATION status field
            update_values = {
                "{workflow_name}_curation_status": target_curation_status
                # Add updated_by=current_user.sub if tracking is needed
            }

            # --- Apply Dual-Status Update Logic ---
            if should_queue_processing:
                logger.debug(f"Queueing {source_table}s {request.ids} for {workflow_name} processing.")
                # Set the PROCESSING status field to 'Queued' and clear any previous error
                update_values["{workflow_name}_processing_status"] = {WorkflowName}ProcessingStatus.Queued
                update_values["{workflow_name}_processing_error"] = None # Clear previous errors
            else:
                 # Optional: Decide if changing to other curation statuses should affect processing status
                 # e.g., update_values["{workflow_name}_processing_status"] = None
                 pass # Keep processing status as is unless explicitly clearing

            stmt = (
                update({SourceTableTitle})
                .where({SourceTableTitle}.id.in_(request.ids))
                .values(**update_values)
                .returning({SourceTableTitle}.id)
            )
            result = await session.execute(stmt)
            updated_ids = result.scalars().all()
            count = len(updated_ids)
            logger.info(f"Database update successful for {count} {source_table} IDs.")
            if count != len(request.ids):
                 logger.warning(f"Requested {len(request.ids)} updates, but only {count} were found/updated.")


        response_message = f"Updated {count} {source_table} records to curation status '{target_curation_status.value}'."
        if should_queue_processing and count > 0:
             response_message += f" Queued {count} for {workflow_name} processing."

        return GenericResponse(message=response_message, details={"updated_ids": updated_ids})

    except Exception as e:
        logger.exception(
            f"Error updating {source_table} status for IDs {request.ids} by user {current_user.sub}: {str(e)}",
            exc_info=True
        )
        # Consider more specific error codes if possible
        raise HTTPException(status_code=500, detail=f"Error updating {source_table} status.")

```

### 2.3 Register Router in main.py

Add to `src/main.py` (ensure the router instance you added the endpoint to is imported).

```python
# Example assuming endpoint was added to src.routers.{source_table}s.router
from src.routers.{source_table}s import router as {source_table}_router
# ...
app.include_router({source_table}_router, tags=["{SourceTableTitle}s"]) # Adjust tags as needed
```

## Phase 3: Background Service Implementation

This phase creates the monitoring service (scheduler) that checks for records marked 'Queued' (or similar) for processing.

### 3.1 Background Scheduler Implementation

Create the scheduler function, typically within `src/services/{workflow_name}_scheduler.py` or added to an existing shared scheduler file.

```python
# Example File: src/services/{workflow_name}_scheduler.py
import logging
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_background_session # Use background session getter
from src.models.{source_table} import {SourceTableTitle} # Import source model
# Import BOTH curation and processing enums
from src.models.enums import {WorkflowName}CurationStatus, {WorkflowName}ProcessingStatus
# Import the actual processing function (defined in Phase 4)
from src.services.{workflow_name}_service import process_single_{source_table}_for_{workflow_name}

logger = logging.getLogger(__name__)
SCHEDULER_BATCH_SIZE = 10 # Example: Make configurable

# Example Name: process_page_curation_queue
async def process_{workflow_name}_queue():
    """
    Scheduler job to find {source_table} records queued for {workflow_name} processing
    and trigger the processing for each.
    """
    session: AsyncSession = await get_background_session()
    processed_ids = []
    try:
        async with session.begin():
            # Find records where the PROCESSING status is 'Queued'
            stmt = (
                select({SourceTableTitle})
                .where({SourceTableTitle}.{workflow_name}_processing_status == {WorkflowName}ProcessingStatus.Queued)
                .with_for_update(skip_locked=True) # Avoid race conditions
                .limit(SCHEDULER_BATCH_SIZE)
            )
            result = await session.execute(stmt)
            records_to_process = result.scalars().all()

            if not records_to_process:
                # logger.debug(f"No {source_table}s found queued for {workflow_name} processing.")
                return # Exit early if nothing to do

            record_ids = [record.id for record in records_to_process]
            logger.info(f"Found {len(record_ids)} {source_table}s queued for {workflow_name}. Locking and marking as Processing.")

            # Mark the PROCESSING status as 'Processing'
            update_stmt = (
                update({SourceTableTitle})
                .where({SourceTableTitle}.id.in_(record_ids))
                .values({workflow_name}_processing_status={WorkflowName}ProcessingStatus.Processing)
            )
            await session.execute(update_stmt)
            processed_ids = record_ids # Keep track of IDs to process outside transaction

        # --- Process each record OUTSIDE the initial transaction ---
        logger.info(f"Processing {len(processed_ids)} {source_table} records for {workflow_name}...")
        for record_id in processed_ids:
            # Create a new session for each item to isolate transactions
            item_session: AsyncSession = await get_background_session()
            try:
                # Call the actual processing function (defined in Phase 4)
                await process_single_{source_table}_for_{workflow_name}(item_session, record_id)
                logger.debug(f"Successfully processed {source_table} {record_id} for {workflow_name}.")
            except Exception as item_error:
                # If processing fails, update the specific item's status to Error
                logger.exception(f"Error processing {source_table} {record_id} for {workflow_name}: {item_error}", exc_info=True)
                try:
                    async with item_session.begin():
                        error_stmt = (
                            update({SourceTableTitle})
                            .where({SourceTableTitle}.id == record_id)
                            .values(
                                {workflow_name}_processing_status={WorkflowName}ProcessingStatus.Error,
                                {workflow_name}_processing_error=str(item_error)[:1000] # Truncate error
                            )
                        )
                        await item_session.execute(error_stmt)
                except Exception as update_err:
                     logger.error(f"Failed to update error status for {source_table} {record_id}: {update_err}")
            finally:
                 await item_session.close() # Close the item-specific session

    except Exception as main_error:
        logger.exception(f"Error in {workflow_name} scheduler main loop: {main_error}", exc_info=True)
    finally:
        await session.close() # Close the main loop session
```

> **Reference:** See [Scheduled Tasks APScheduler Pattern](../../Docs_1_AI_GUIDES/21-SCHEDULED_TASKS_APSCHEDULER_PATTERN.md), [Shared Scheduler Integration Guide](../../Docs_1_AI_GUIDES/24-SHARED_SCHEDULER_INTEGRATION_GUIDE.md), and [Background Services Architecture](../../Docs_6_Architecture_and_Status/BACKGROUND_SERVICES_ARCHITECTURE.md).

### 3.2 Register Scheduler

Add the job to `src/schedulers.py`.

```python
from src.services.{workflow_name}_scheduler import process_{workflow_name}_queue # Import scheduler function

# Example ID: page_curation_scheduler
scheduler.add_job(
    process_{workflow_name}_queue,
    'interval',
    minutes=1, # Adjust interval as needed, make configurable
    id=f"{workflow_name}_scheduler",
    replace_existing=True,
    max_instances=1 # Usually 1 to prevent race conditions unless designed for concurrency
)
```

> **Reference:** See [Scheduler and Settings Patterns](../../Docs_1_AI_GUIDES/28-SCHEDULER_AND_SETTINGS_PATTERNS.md)

## Phase 4: Curation Service Development

This phase implements the core data enrichment or processing functionality called by the scheduler.

### 4.1 Data Enrichment/Processing Service

Create the service function, typically in `src/services/{workflow_name}_service.py`.

```python
# Example File: src/services/{workflow_name}_service.py
import logging
from uuid import UUID
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.{source_table} import {SourceTableTitle} # Import source model
# Import the PROCESSING enum
from src.models.enums import {WorkflowName}ProcessingStatus
# If creating new records, import destination model:
# from src.models.{destination_table} import {DestinationTableTitle}

logger = logging.getLogger(__name__)

# Example Name: process_single_page_for_page_curation
async def process_single_{source_table}_for_{workflow_name}(
    session: AsyncSession, # Note: Session is passed in from scheduler
    record_id: UUID,
) -> None:
    """
    Processes a single {source_table} record for the {workflow_name} workflow.
    Handles transaction management for this specific record.
    """
    try:
        # --- Step 1: Retrieve the source record ---
        # No need for transaction here, retrieval only
        stmt = select({SourceTableTitle}).where({SourceTableTitle}.id == record_id)
        result = await session.execute(stmt)
        source_record = result.scalars().first()

        if not source_record:
            # This case should ideally be rare if scheduler locks correctly
            logger.warning(f"{workflow_name} processing: {SourceTableTitle} with ID {record_id} not found.")
            # Optionally update status if needed, but record doesn't exist...
            return # Exit if record vanished

        # Optional: Check if status is still 'Processing', otherwise maybe skip
        if source_record.{workflow_name}_processing_status != {WorkflowName}ProcessingStatus.Processing:
            logger.warning(f"{workflow_name} processing: {SourceTableTitle} {record_id} status changed "
                           f"to {source_record.{workflow_name}_processing_status}. Skipping.")
            return

        # --- Step 2: Perform the actual data enrichment/processing ---
        # This part is custom and should ideally happen outside a transaction
        # if it involves long-running tasks or external calls.
        logger.debug(f"Performing {workflow_name} processing for {source_table} {record_id}...")
        # extracted_data = await perform_custom_extraction(source_record) # Example call

        # --- Step 3: Update status and/or create output records ---
        async with session.begin(): # Start transaction for final updates
            # >> Your custom logic result handling here <<

            # --- Option A: Update Source Table (e.g., Page Curation) ---
            # // NOTE: Use this block for workflows updating the source table.
            logger.debug(f"Updating {source_table} {record_id} status to Completed for {workflow_name}.")
            final_update_stmt = (
                update({SourceTableTitle})
                .where({SourceTableTitle}.id == record_id)
                .values(
                    {workflow_name}_processing_status={WorkflowName}ProcessingStatus.Completed,
                    {workflow_name}_processing_error=None # Clear any previous error on success
                    # Optionally update curation status too if needed, e.g., 'Processed'
                    # {workflow_name}_curation_status = {WorkflowName}CurationStatus.Processed
                )
            )
            await session.execute(final_update_stmt)

            # --- Option B: Create New Records in Destination Table (e.g., Contact Extraction) ---
            # // NOTE: Use this block for workflows creating new records.
            # // Ensure extracted_data is defined from Step 2
            # logger.debug(f"Creating {destination_table} records for {source_table} {record_id}...")
            # for item_data in extracted_data: # Assuming extracted_data is a list of dicts
            #     new_record = {DestinationTableTitle}(
            #         id=uuid.uuid4(),
            #         {source_table}_id=record_id, # Link back to source
            #         **item_data # Populate fields from extracted data
            #     )
            #     session.add(new_record)
            #
            # # Update source record's processing status to Completed
            # final_update_stmt = (
            #     update({SourceTableTitle})
            #     .where({SourceTableTitle}.id == record_id)
            #     .values(
            #         {workflow_name}_processing_status={WorkflowName}ProcessingStatus.Completed,
            #         {workflow_name}_processing_error=None
            #     )
            # )
            # await session.execute(final_update_stmt)
            # --- End Option B ---

        # Transaction automatically commits on success here

    except Exception as e:
        # Raise the exception to be caught by the scheduler's item processing loop,
        # which will handle logging and updating the status to Error.
        logger.error(f"Error during process_single_{source_table}_for_{workflow_name} for ID {record_id}: {e}")
        raise # Re-raise exception for scheduler to handle status update

# --- Helper function for custom logic ---
# async def perform_custom_extraction(source_record: {SourceTableTitle}) -> List[Dict]:
#     # Implement your specific extraction/processing logic here.
#     # This function should ideally be independent of the database session.
#     # Example:
#     # if source_record.content:
#     #    emails = re.findall(r'[\w\.-]+@[\w\.-]+', source_record.content)
#     #    return [{"email": email} for email in emails]
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
  <div class="container">
    <div class="row mt-3">
      <div class="col-12">
        <!-- Example Title: Page Curation Management -->
        <h4>{WorkflowNameTitle} Management</h4>
        <div class="card">
          <div class="card-header bg-primary text-white">
            {SourceTableTitle} Selection
          </div>
          <div class="card-body">
            <!-- Example ID: pages-table -->
            <table id="{source_table}s-table" class="table table-striped">
              <thead>
                <tr>
                  <th>
                    <!-- Example ID: select-all-pages -->
                    <input type="checkbox" id="select-all-{source_table}s" />
                  </th>
                  <th>ID</th>
                  <th>{WorkflowNameTitle} Curation Status</th>
                  <th>{WorkflowNameTitle} Processing Status</th>
                  <!-- Add other relevant fields -->
                </tr>
              </thead>
              <!-- Example ID: pages-tbody -->
              <tbody id="{source_table}s-tbody">
                <!-- Rows will be populated by JavaScript -->
              </tbody>
            </table>
          </div>
          <div class="card-footer">
            <!-- Example ID: update-pages-status-selected -->
            <button
              id="update-{source_table}s-status-selected"
              class="btn btn-success"
            >
              Mark Selected
            </button>
            <button
              id="update-{source_table}s-status-rejected"
              class="btn btn-warning"
            >
              Mark Rejected
            </button>
            <button
              id="update-{source_table}s-status-archived"
              class="btn btn-secondary"
            >
              Mark Archived
            </button>
            <!-- Add other action buttons as needed -->
          </div>
        </div>
      </div>
    </div>
  </div>
</div>
```

### 4.5.2 JavaScript File

Create in `static/js/{workflow_name}-tab.js`:

```javascript
// Example File: static/js/page-curation-tab.js
$(document).ready(function () {
  const sourceTable = "{source_table}s"; // e.g., "pages"
  const workflowName = "{workflow_name}"; // e.g., "page_curation"
  const curationStatusEnum = {
    // Get actual enum values if possible, else hardcode
    Selected: "Selected",
    Rejected: "Rejected",
    Archived: "Archived",
    // Add other relevant curation statuses
  };

  const tableBody = $(`#${sourceTable}-tbody`);
  const selectAllCheckbox = $(`#select-all-${sourceTable}`);

  // --- Load initial data ---
  function loadData() {
    // Add filters if needed, e.g., status=New
    $.ajax({
      url: `/api/v3/${sourceTable}/list`, // Adjust API endpoint if needed
      type: "GET",
      success: function (response) {
        populateTable(response.items || []); // Adjust based on API response structure
        selectAllCheckbox.prop("checked", false); // Reset select all
      },
      error: function (error) {
        showNotification("Error", `Failed to load ${sourceTable} data`);
        console.error("Load error:", error);
      },
    });
  }

  // --- Populate Table ---
  function populateTable(items) {
    tableBody.empty();
    if (!items || items.length === 0) {
      tableBody.append('<tr><td colspan="4">No items found.</td></tr>'); // Adjust colspan
      return;
    }
    items.forEach((item) => {
      // Adjust field names based on your model
      const curationStatus = item[`${workflowName}_curation_status`] || "New";
      const processingStatus =
        item[`${workflowName}_processing_status`] || "N/A";
      tableBody.append(`
                <tr>
                    <td><input type="checkbox" class="${sourceTable}-checkbox" data-id="${item.id}"></td>
                    <td>${item.id}</td>
                    <td>${curationStatus}</td>
                    <td>${processingStatus}</td>
                    <!-- Add other relevant fields -->
                </tr>
            `);
    });
  }

  // --- Get Selected IDs ---
  function getSelectedIds() {
    return $(`.${sourceTable}-checkbox:checked`)
      .map(function () {
        return $(this).data("id");
      })
      .get();
  }

  // --- Update Status Function ---
  function updateStatus(statusValue) {
    const selectedIds = getSelectedIds();
    if (selectedIds.length === 0) {
      showNotification("Warning", "Please select at least one item.");
      return;
    }

    $.ajax({
      url: `/api/v3/${sourceTable}/status`, // Use the correct batch update endpoint
      type: "PUT", // Use PUT for updates
      contentType: "application/json",
      data: JSON.stringify({
        ids: selectedIds,
        status: statusValue, // Send the selected curation status
      }),
      success: function (response) {
        showNotification(
          "Success",
          response.message || "Status updated successfully"
        );
        loadData(); // Refresh the table
      },
      error: function (error) {
        const errorMsg =
          error.responseJSON?.detail ||
          `Failed to update status to ${statusValue}`;
        showNotification("Error", errorMsg);
        console.error("Update error:", error);
      },
    });
  }

  // --- Event Handlers ---
  selectAllCheckbox.click(function () {
    $(`.${sourceTable}-checkbox`).prop("checked", $(this).prop("checked"));
  });

  $(`#update-${sourceTable}-status-selected`).click(function () {
    updateStatus(curationStatusEnum.Selected);
  });
  $(`#update-${sourceTable}-status-rejected`).click(function () {
    updateStatus(curationStatusEnum.Rejected);
  });
  $(`#update-${sourceTable}-status-archived`).click(function () {
    updateStatus(curationStatusEnum.Archived);
  });
  // Add handlers for other buttons...

  // --- Initial Load ---
  loadData();
});

// --- Simple Notification Helper ---
function showNotification(title, message) {
  // Replace with a more sophisticated notification system if available
  alert(`${title}: ${message}`);
}
```

> **Reference:** See [Curation Workflow Operating Manual](../../Docs_6_Architecture_and_Status/0.4_Curation%20Workflow%20Operating%20Manual.md) for frontend integration patterns.

## Phase 5: End-to-End Testing

The final phase validates that all components work together correctly.

### 5.1 Testing Checklist

- [ ] Database schema changes are correctly applied (manual verification or migration test)
- [ ] API endpoints respond with expected status codes and payloads (integration tests)
- [ ] Frontend UI displays correctly and sends proper requests (manual testing or E2E tests)
- [ ] Background scheduler picks up queued items (integration/manual tests, log verification)
- [ ] Processing service successfully processes records and updates status (integration/manual tests)
- [ ] Status fields update appropriately throughout the workflow (integration/manual tests)
- [ ] Error handling works as expected (integration/manual tests, trigger error conditions)

### 5.2 Test Cases (Example using Pytest)

Create tests in `tests/` directory.

```python
# Example File: tests/services/test_{workflow_name}_workflow.py
import pytest
from httpx import AsyncClient
from uuid import uuid4, UUID

from src.main import app # Assuming FastAPI app instance is accessible
from src.models.{source_table} import {SourceTableTitle}
from src.models.enums import {WorkflowName}CurationStatus, {WorkflowName}ProcessingStatus
# Import test utilities, fixtures (e.g., get_test_session, create_test_{source_table})

# Example Test: API Endpoint
@pytest.mark.asyncio
async def test_{workflow_name}_api_status_update(async_client: AsyncClient, test_session):
    # Setup: Create test {source_table} record(s)
    test_record = await create_test_{source_table}(test_session, {workflow_name}_curation_status={WorkflowName}CurationStatus.New)
    test_id = test_record.id

    # Execute: Call API to update status to 'Selected'
    response = await async_client.put(
        f"/api/v3/{source_table}s/status", # Adjust URL if needed
        json={"ids": [str(test_id)], "status": {WorkflowName}CurationStatus.Selected.value}
    )

    # Verify: API Response
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["message"].startswith("Updated 1")
    assert str(test_id) in response_data["details"]["updated_ids"]

    # Verify: Database State
    await test_session.refresh(test_record) # Refresh object state from DB
    assert test_record.{workflow_name}_curation_status == {WorkflowName}CurationStatus.Selected
    assert test_record.{workflow_name}_processing_status == {WorkflowName}ProcessingStatus.Queued # Check dual-status update
    assert test_record.{workflow_name}_processing_error is None

# Example Test: Processing Service Logic (Happy Path - Update Source)
@pytest.mark.asyncio
async def test_{workflow_name}_service_processing_success(test_session):
    from src.services.{workflow_name}_service import process_single_{source_table}_for_{workflow_name}

    # Setup: Create a record ready for processing
    test_record = await create_test_{source_table}(
        test_session,
        {workflow_name}_curation_status={WorkflowName}CurationStatus.Selected, # Or whatever state processing expects
        {workflow_name}_processing_status={WorkflowName}ProcessingStatus.Processing # Simulate scheduler having marked it
        # Add any other required fields for processing logic
    )
    test_id = test_record.id

    # Execute: Call the processing function directly
    await process_single_{source_table}_for_{workflow_name}(test_session, test_id)

    # Verify: Database State
    await test_session.refresh(test_record)
    assert test_record.{workflow_name}_processing_status == {WorkflowName}ProcessingStatus.Completed
    assert test_record.{workflow_name}_processing_error is None
    # Optionally check curation status if it should change:
    # assert test_record.{workflow_name}_curation_status == {WorkflowName}CurationStatus.Processed

# Add more tests for error cases, different statuses, scheduler interaction etc.

```

> **Reference:** See [Comprehensive Test Plan](../../Docs_1_AI_GUIDES/06-COMPREHENSIVE_TEST_PLAN.md)

### 5.3 Manual Testing Procedure

1.  Start the application (e.g., `docker-compose up`). Ensure the scheduler is enabled.
2.  Navigate to the workflow tab in the UI (e.g., `/static/scraper-sky-mvp.html`).
3.  Create/identify source records in a state ready for curation (e.g., `New`).
4.  Use the UI buttons to select items and update their curation status (e.g., to 'Selected').
5.  Verify UI table updates correctly, showing the new curation status and 'Queued' processing status.
6.  Monitor application logs (`docker-compose logs -f app`). Look for messages indicating the scheduler picked up the items and marked them as 'Processing'.
7.  Look for logs indicating the processing service completed successfully for the items.
8.  Refresh the UI or check the database directly to verify the processing status is updated to 'Completed' and the error field is clear.
9.  Test error paths: Intentionally cause the processing logic to fail (if possible) and verify the status updates to 'Error' and an error message is recorded.
10. Test other UI actions (e.g., 'Rejected', 'Archived') and verify the correct curation status is set and processing is _not_ triggered.

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
