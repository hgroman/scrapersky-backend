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
>     # ... other statuses ...
>     Skipped = "Skipped"
> ```
>
> For the full enum definitions, see: [Docs/Docs_Code_Snippets/Workflow_Templates/workflow_model_updates_example.py](Docs/Docs_Code_Snippets/Workflow_Templates/workflow_model_updates_example.py)

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
- All table relationships must be defined in Layer 1: Models & ENUMs
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
| Will this have a Layer 6: UI Component?             | Yes                          |             |
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

Add the required status fields to the source table. Ensure Enum types are created first (see 1.4).

```sql
-- Add to source table ({source_table})
ALTER TABLE {source_table} ADD COLUMN {workflow_name}_curation_status {workflow_name}curationstatus NOT NULL DEFAULT \'New\';
ALTER TABLE {source_table} ADD COLUMN {workflow_name}_processing_status {workflow_name}processingstatus NULL;
-- Optional: ALTER TABLE {source_table} ADD COLUMN {workflow_name}_processing_error TEXT NULL;
```

These snippets illustrate the essential DDL for adding status columns. For complete migration files, always refer to the project's `supabase/migrations/` directory for the specific workflow.

### 1.4 Required Database Enum Types

Create both enum types in PostgreSQL.

```sql
-- Curation status enum (user-driven selection/trigger)
CREATE TYPE {workflow_name}curationstatus AS ENUM (\'New\', \'Queued\', \'Processing\', \'Complete\', \'Error\', \'Skipped\');

-- Processing status enum (background processing lifecycle)
CREATE TYPE {workflow_name}processingstatus AS ENUM (\'Queued\', \'Processing\', \'Complete\', \'Error\');
```

> **IMPORTANT:** These standardized enum values should be used consistently across ALL workflows!

#### Verification Queries

After creating your ENUM types and adding columns, use these queries to verify success.
For the full verification queries, see: [Docs/Docs_Code_Snippets/Workflow_Templates/workflow_db_verification_queries.sql](Docs/Docs_Code_Snippets/Workflow_Templates/workflow_db_verification_queries.sql)

> **Reference:** See [Enum Handling Standards](../../Docs_1_AI_GUIDES/27-ENUM_HANDLING_STANDARDS.md) and [Database Enum Isolation](../../Docs_1_AI_GUIDES/29-DATABASE_ENUM_ISOLATION.md).

### 1.5 Layer 1: Models & ENUMs Updates

> **STANDARDIZATION NOTE:** Place workflow enums in the same module as their related models (domain-based placement).
> This approach (model-based placement) is our preferred pattern going forward to support better separation of concerns.
> While you may see legacy enums in `src/models/enums.py` or `src/models/api_models.py`, new workflow status enums should follow the domain-based pattern.

After planning your database schema changes and creating a migration using Supabase MCP, you MUST update the corresponding SQLAlchemy Layer 1: Model file. This involves defining the Python Layer 1: Enum classes and adding the new `Column` definitions that match the schema changes you applied through MCP migrations.

For a full example of the SQLAlchemy model updates, including Enum definitions and new Column additions, see: [Docs/Docs_Code_Snippets/Workflow_Templates/workflow_model_updates_example.py](Docs/Docs_Code_Snippets/Workflow_Templates/workflow_model_updates_example.py)

A brief illustration of adding columns:

```python
# In src/models/{source_table}.py
# ...
class {SourceTableTitle}(Base, BaseModel):
    # ... existing columns ...
    {workflow_name}_curation_status = Column(PgEnum({WorkflowName}CurationStatus, ...), ...)
    {workflow_name}_processing_status = Column(PgEnum({WorkflowName}ProcessingStatus, ...), ...)
    {workflow_name}_processing_error = Column(Text, nullable=True)
    # ...
```

> **IMPORTANT NOTE ON `create_type=False`:**
> Since database ENUM types are created and managed manually via SQL (as per project standards outlined in sections 1.3 & 1.4, and the AI Collaboration Constitution), `create_type=False` is **CRITICAL** in your `PgEnum` definitions. This parameter tells SQLAlchemy _not_ to attempt to create the ENUM type in the database, preventing conflicts with our manual SQL-first approach. Always ensure this is set for ENUMs managed this way.

> **Reference:** See [Enum Handling Standards](../../Docs_1_AI_GUIDES/27-ENUM_HANDLING_STANDARDS.md)

## Phase 2: Consumer Endpoint Construction

This phase creates the API endpoint for user row selection and batch status updates.

> **DUAL-STATUS UPDATE PATTERN**: This is the cornerstone pattern of all workflows. When a user sets the curation status to trigger processing (usually "Queued"), the endpoint MUST ALSO set the processing_status to "Queued" in the same transaction. This producer-consumer pattern is what connects UI actions to background processing.

### 2.1 Layer 3: Router and Endpoints

This phase focuses on building the API endpoints that allow users or other services to interact with the workflow, primarily for selecting rows for processing and checking their status.

#### 2.1.1 API Request Schema

Plan the Pydantic request models, typically placed in `src/schemas/`.
Conventionally, Layer 2: Schemas for workflow-specific actions (like batch status updates) **MUST** be placed in `src/schemas/{workflow_name}.py`.

For an example of batch status update request and response schemas (e.g., `{WorkflowNameTitleCase}BatchStatusUpdateRequest`), see: [Docs/Docs_Code_Snippets/Workflow_Templates/workflow_batch_update_schemas_example.py](Docs/Docs_Code_Snippets/Workflow_Templates/workflow_batch_update_schemas_example.py)

An illustrative snippet:

```python
# Example File: src/schemas/{workflow_name}.py
class {WorkflowNameTitleCase}BatchStatusUpdateRequest(BaseModel):
    ids: List[UUID]
    status: {WorkflowNameTitleCase}CurationStatus
```

> **Reference:** See [API Standardization Guide](../../Docs_1_AI_GUIDES/15-API_STANDARDIZATION_GUIDE.md) and Section 6 of `CONVENTIONS_AND_PATTERNS_GUIDE.md`.

#### 2.1.2 API Router Implementation

> **CRITICAL ARCHITECTURE PATTERN: DUAL-STATUS UPDATE**
> The API endpoint must implement the **dual-status update pattern**:
>
> 1. When user sets {workflow_name}\_curation_status to **`{WorkflowNameTitleCase}CurationStatus.Queued`** via the API (as per `CONVENTIONS_AND_PATTERNS_GUIDE.md` Section 2 & 4).
> 2. The endpoint MUST ALSO set {workflow_name}\_processing_status to `{WorkflowNameTitleCase}ProcessingStatus.Queued`.
> 3. This triggers the background scheduler to process this record.
>
> This producer-consumer pattern is fundamental to all workflows and MUST be implemented consistently.

Create/update router, typically in `src/routers/{workflow_name}.py`.
This router handles incoming API requests, validates them, interacts with the database (e.g., updating status fields), and implements the crucial dual-status update pattern.

For a full example of the API router implementation, including dependency injection, dual-status update logic, and error handling, see: [Docs/Docs_Code_Snippets/Workflow_Templates/workflow_api_router_example.py](Docs/Docs_Code_Snippets/Workflow_Templates/workflow_api_router_example.py)

Key aspects illustrated:

```python
# Example File: src/routers/{workflow_name}.py
# ... imports ...
router = APIRouter()

@router.put("/status", response_model={WorkflowNameTitleCase}BatchStatusUpdateResponse)
async def update_{source_table_name}_status_batch(
    request: {WorkflowNameTitleCase}BatchStatusUpdateRequest,
    # ... dependencies ...
):
    # ...
    # Dual-status update logic:
    if should_queue_processing:
        update_values["{workflow_name}_processing_status"] = {WorkflowNameTitleCase}ProcessingStatus.Queued
    # ...
    # Database update via SQLAlchemy:
    await session.execute(stmt)
    # ...
```

> **Note on Router File Location & Naming:** The primary convention for new, workflow-specific routers is `src/routers/{workflow_name}.py`. This router is then typically included in `main.py` with a prefix like `/api/v3/{source_table_plural_name}`.
> **Confirm the desired path, name, and prefixing strategy with the User** if any doubt exists, adhering to the "Zero Assumptions" principle.

> **CRITICAL: Standard FastAPI Session Dependency**
> For injecting the SQLAlchemy `AsyncSession` into your FastAPI endpoints, you **MUST** use the project's standard dependency.

#### 2.1.3 Register Router in main.py

Add to `src/main.py` (or your main API router aggregation file, e.g., `src/api.py`). This makes your new workflow endpoints accessible.

For an example of how to import and include your workflow-specific router in `main.py` with appropriate prefixes and tags, see: [Docs/Docs_Code_Snippets/Workflow_Templates/workflow_main_py_router_registration_example.py](Docs/Docs_Code_Snippets/Workflow_Templates/workflow_main_py_router_registration_example.py)

Illustrative snippet:

```python
# In src/main.py
from src.routers.{workflow_name} import router as {workflow_name}_router

app.include_router(
    {workflow_name}_router,
    tags=["{WorkflowNameTitleCase} | {SourceTableTitleCasePlural}"],
    prefix="/api/v3/{source_table_plural_name}"
)
```

> **Note on Router Instance and Prefixing Strategy:**
> The router instance (e.g., `{workflow_name}_router` from `src/routers/{workflow_name}.py`) defines endpoints relative to its own path (e.g., `/status`).
> The full path is constructed by how this specific router is included into the main application router or the FastAPI app itself.
> **Consult existing patterns in `src/main.py` or `src/api.py` and confirm with the User if unsure.**

### 2.2 Layer 2: Schemas for API I/O

Create Layer 2: Pydantic Schemas for handling request and response data validation and serialization.
Place these schemas in `src/schemas/{workflow_name}_schemas.py`. These might include schemas for detailed item views or other specific selection criteria beyond batch updates.

For examples of general Pydantic schemas like `{WorkflowNameTitleCase}SelectionSchema` and `{WorkflowNameTitleCase}DetailSchema`, see: [Docs/Docs_Code_Snippets/Workflow_Templates/workflow_general_api_schemas_example.py](Docs/Docs_Code_Snippets/Workflow_Templates/workflow_general_api_schemas_example.py)

An illustrative snippet for a detail schema:

```python
# Example File: src/schemas/{workflow_name}_schemas.py
class {WorkflowNameTitleCase}DetailSchema(BaseModel):
    id: UUID
    {workflow_name}_curation_status: {WorkflowNameTitleCase}CurationStatus
    {workflow_name}_processing_status: Optional[{WorkflowNameTitleCase}ProcessingStatus]
```

## Phase 3: Background Service Implementation

This phase outlines the creation of a background scheduler responsible for monitoring items that are ready for processing.

### 3.1 Layer 4: Scheduler (Polling Logic)

This service, typically located in `src/services/{workflow_name}_scheduler.py`, contains the `process_{workflow_name}_queue` function. This function queries for items ready for processing, locks them, updates their status to 'Processing', and then calls the main curation service (Phase 4) for each item.

For a full example of the `process_{workflow_name}_queue` function, including database interaction, locking, batching, and error handling for individual items, see the `process_{workflow_name}_queue` function within: [Docs/Docs_Code_Snippets/Workflow_Templates/workflow_scheduler_example.py](Docs/Docs_Code_Snippets/Workflow_Templates/workflow_scheduler_example.py)

Key logic:

```python
# In src/services/{workflow_name}_scheduler.py
async def process_{workflow_name}_queue():
    # ...
    # Select items with {workflow_name}_processing_status == Queued
    # Lock items and update {workflow_name}_processing_status to Processing
    # For each item, call:
    #   await process_single_{source_table_name}_for_{workflow_name}(item_session, record_id)
    # Handle errors, update status to Error if item processing fails
    # ...
```

> **Reference:** See [Scheduled Tasks APScheduler Pattern](../../Docs_1_AI_GUIDES/21-SCHEDULED_TASKS_APSCHEDULER_PATTERN.md), [Shared Scheduler Integration Guide](../../Docs_1_AI_GUIDES/24-SHARED_SCHEDULER_INTEGRATION_GUIDE.md), and [Background Services Architecture](../../Docs_6_Architecture_and_Status/BACKGROUND_SERVICES_ARCHITECTURE.md).

### 3.2 Register Scheduler

As per the `CONVENTIONS_AND_PATTERNS_GUIDE.md` (Section 8), scheduler registration follows a specific pattern for modularity and clarity. Each workflow's scheduler defines its own setup function, which is then called from `src/main.py`.

**Step 1: Define Setup Function in `src/services/{workflow_name}_scheduler.py`**

Add a setup function (e.g., `setup_{workflow_name}_scheduler`) to your `src/services/{workflow_name}_scheduler.py` file. This function configures and adds the `process_{workflow_name}_queue` job to the APScheduler.

For a full example of this setup function, see the `setup_{workflow_name}_scheduler` function within: [Docs/Docs_Code_Snippets/Workflow_Templates/workflow_scheduler_example.py](Docs/Docs_Code_Snippets/Workflow_Templates/workflow_scheduler_example.py)

Illustrative snippet:

```python
# In src/services/{workflow_name}_scheduler.py
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from src.config.settings import settings

def setup_{workflow_name}_scheduler(scheduler: AsyncIOScheduler) -> None:
    job_id = f"{workflow_name}_scheduler"
    interval_minutes = getattr(settings, f"{workflow_name.upper()}_SCHEDULER_INTERVAL_MINUTES", 1)
    scheduler.add_job(process_{workflow_name}_queue, \'interval\', minutes=interval_minutes, ...)
```

**Step 2: Call Setup Function from `src/main.py` Lifespan Event**

Import and call your `setup_{workflow_name}_scheduler` function within the `lifespan` context manager in `src/main.py`. This ensures your scheduled job starts when the application starts.

For a complete example of integrating the scheduler setup into the `main.py` lifespan event, including starting and stopping the main scheduler, see: [Docs/Docs_Code_Snippets/Workflow_Templates/workflow_main_py_scheduler_registration_example.py](Docs/Docs_Code_Snippets/Workflow_Templates/workflow_main_py_scheduler_registration_example.py)

Illustrative snippet:

```python
# In src/main.py
from src.schedulers import scheduler
from src.services.{workflow_name}_scheduler import setup_{workflow_name}_scheduler

@asynccontextmanager
async def lifespan(app: FastAPI):
    # ... scheduler.start() ...
    setup_{workflow_name}_scheduler(scheduler)
    yield
    # ... scheduler.shutdown() ...
```

**Note:** The `minutes=1` default interval in `add_job` is an example. Determine the appropriate frequency based on workflow needs and performance impact. This **MUST** be configured via `settings` as shown.

> **Reference:** See [Scheduler and Settings Patterns](../../Docs_1_AI_GUIDES/28-SCHEDULER_AND_SETTINGS_PATTERNS.md) and Section 8 of `CONVENTIONS_AND_PATTERNS_GUIDE.md`.

## Phase 4: Curation Service Development

This phase implements the core data enrichment or processing functionality called by the scheduler.

### 4.1 Data Enrichment/Processing Service

Create the service function, typically in `src/services/{workflow_name}_service.py`. This function, `process_single_{source_table_name}_for_{workflow_name}`, contains the core business logic for processing a single item. It retrieves the item, performs necessary operations (e.g., data extraction, transformation, external API calls), and then updates the item's status to 'Completed' or 'Error'.

**Transactional Boundary Note:** The `async with session.begin():` block ensures that all database updates within Step 3 are committed together.
**Resource Management Note:** If your custom processing logic acquires other resources, ensure they are properly closed.
**External Integration Note:** Implement robust error handling, timeouts, and consider retries for external API calls.

For a full example of the `process_single_{source_table_name}_for_{workflow_name}` function, including transaction management, idempotency checks, and options for updating the source table or creating new records in a destination table, see: [Docs/Docs_Code_Snippets/Workflow_Templates/workflow_curation_service_example.py](Docs/Docs_Code_Snippets/Workflow_Templates/workflow_curation_service_example.py)

Key steps in the function:

```python
# In src/services/{workflow_name}_service.py
async def process_single_{source_table_name}_for_{workflow_name}(session: AsyncSession, record_id: UUID) -> None:
    # 1. Retrieve the source record.
    # 2. Perform idempotency check (ensure status is still \'Processing\').
    # 3. Perform custom data enrichment/processing logic.
    #    (This might call a helper like `perform_custom_extraction(source_record)`)
    # 4. Within a transaction (session.begin()):
    #    a. Update source record\'s {workflow_name}_processing_status to \'Completed\'.
    #    b. OR create new records in a destination table and then update source.
    #    c. Clear any {workflow_name}_processing_error.
    # Handle exceptions by raising them, to be caught by the calling scheduler task.
```

> **Reference:** See [Absolute ORM Requirement](../../Docs_1_AI_GUIDES/01-ABSOLUTE_ORM_REQUIREMENT.md), [Core Architectural Principles - Error Handling](../../Docs_1_AI_GUIDES/17-CORE_ARCHITECTURAL_PRINCIPLES.md#6-error-handling), and [Transaction Management Guide](../../Docs_1_AI_GUIDES/13-TRANSACTION_MANAGEMENT_GUIDE.md).

## Phase 4.5: Frontend Components (if UI-driven)

If the workflow involves user interaction, create the necessary frontend components.

### 4.5.1 HTML Tab

Add to `templates/scraper-sky-mvp.html`. This HTML structure defines the tab, table for displaying items, and buttons for user actions.

For the complete HTML structure for a workflow tab, including placeholders for IDs, table headers, and action buttons, see: [Docs/Docs_Code_Snippets/Workflow_Templates/workflow_ui_tab_example.html](Docs/Docs_Code_Snippets/Workflow_Templates/workflow_ui_tab_example.html)

A conceptual overview:

```html
<!-- In templates/scraper-sky-mvp.html -->
<div class="tab-pane" id="{workflow_name}-tab">
  <h4>{WorkflowNameTitleCase} Management</h4>
  <table id="{workflowNameCamelCase}Table">
    <thead>
      <!-- ... headers for ID, statuses, etc. ... -->
    </thead>
    <tbody id="{workflowNameCamelCase}TableBody">
      <!-- Rows populated by JS -->
    </tbody>
  </table>
  <button id="update-{source_table_plural_name}-status-queued">Queue Selected</button>
  <!-- ... other buttons ... -->
</div>
```

### 4.5.2 JavaScript File

Create in `static/js/{workflow_name_kebab_case}-tab.js`. This file handles loading data into the table, user selections, and making API calls to the backend when action buttons are clicked. Ensure all DOM selectors precisely match the HTML IDs defined in section 4.5.1 and follow conventions.

For a full example of the JavaScript logic, including DOM manipulation with jQuery, API calls for loading data and updating statuses, and event handling for buttons and checkboxes, see: [Docs/Docs_Code_Snippets/Workflow_Templates/workflow_ui_tab_example.js](Docs/Docs_Code_Snippets/Workflow_Templates/workflow_ui_tab_example.js)

Core JavaScript functionalities:

```javascript
// In static/js/{workflow_name_kebab_case}-tab.js
$(document).ready(function () {
  // Define constants (workflowName, selectors)
  // function loadData() { /* AJAX call to /api/v3/{source_table_plural}/list */ }
  // function populateTable(items) { /* Fill tableBody */ }
  // function getSelectedIds() { /* Get IDs from checkboxes */ }
  // function updateStatus(newStatus) {
  //   /* AJAX PUT to /api/v3/{source_table_plural}/status with selectedIds and newStatus */
  // }
  // Event handlers for selectAllCheckbox, queueSelectedBtn, markSkippedBtn, etc.
  // loadData(); // Initial load
});
```

> **Reference:** See [Curation Workflow Operating Manual](../../Docs_6_Architecture_and_Status/0.4_Curation%20Workflow%20Operating%20Manual.md) for frontend integration patterns.

## Phase 5: End-to-End Testing

The final phase validates that all components work together correctly.

### 5.1 Testing Checklist & Methodology

Develop a comprehensive testing strategy covering unit, integration, and end-to-end tests. Focus on verifying the interactions between components and correct state transitions. Refer to `CONVENTIONS_AND_PATTERNS_GUIDE.md` Section 12 for required test coverage.

**Overall Checklist & Methodology Highlights:**

- [ ] Database schema changes applied.
- [ ] API endpoints function correctly.
- [ ] Frontend UI interacts with API as expected.
- [ ] Service functions testable in isolation.
- [ ] Progressive testing: Foundation -> Component -> Integration -> End-to-End.
- [ ] Background scheduler polls, locks, and triggers processing correctly.
- [ ] Processing service executes custom logic and updates status accurately.
- [ ] Status fields transition correctly through the entire workflow cycle.
- [ ] Error handling mechanisms function as designed.
- [ ] Idempotency checks prevent duplicate processing.

### 5.2 Test Cases (Example using Pytest)

Create tests in `tests/` directory, following naming conventions.

For comprehensive examples of Pytest test cases, including:

- Testing the API endpoint for status updates and dual-status queueing.
- Testing the processing service logic (happy path and error scenarios).
- Conceptual tests for scheduler behavior.
- Usage of fixtures like `async_client` and `db_session`.
  See: [Docs/Docs_Code_Snippets/Workflow_Templates/workflow_pytest_examples.py](Docs/Docs_Code_Snippets/Workflow_Templates/workflow_pytest_examples.py)

An example of an API test structure:

```python
# In tests/workflows/test_{workflow_name}_workflow.py
@pytest.mark.asyncio
async def test_{workflow_name}_api_status_update_and_queueing(async_client, db_session, create_test_{source_table_name}):
    # Setup: Create a test record
    # Execute: Call API endpoint (e.g., PUT /api/v3/{source_table_plural_name}/status)
    # Verify: API response (status code, message)
    # Verify: Database state (curation_status, processing_status)
```

An example of a service test structure:

```python
# In tests/services/test_{workflow_name}_service.py
@pytest.mark.asyncio
async def test_{workflow_name}_service_processing_success(db_session, create_test_{source_table_name}):
    # Setup: Create a record ready for processing
    # Execute: Call the service function (e.g., process_single_{source_table_name}_for_{workflow_name})
    # Verify: Database state (processing_status should be \'Completed\')
```

**Mocking Note:** Use mocking libraries for external dependencies in service logic during unit/integration testing.

> **Reference:** See [Comprehensive Test Plan](../../Docs_1_AI_GUIDES/06-COMPREHENSIVE_TEST_PLAN.md) and `CONVENTIONS_AND_PATTERNS_GUIDE.md` Section 12.

### 5.3 Manual Testing Procedure

1.  **Setup:** Start application, ensure scheduler is enabled. Prepare test data.
2.  **Trigger:** Use UI to select items and update curation status to `Queued`.
3.  **Verify API/UI:** Confirm UI table updates, check browser console for API success.
4.  **Verify Scheduler Pickup:** Monitor application logs for scheduler activity.
5.  **Verify Service Execution:** Monitor logs for service function activity.
6.  **Verify Final State (Happy Path):** Refresh UI/DB, confirm `processing_status` is `Completed`.
7.  **Test Error Path:** Introduce a condition for service error, trigger processing. Verify logs, error status, and error message in DB/UI.
8.  **Test Other Curation Paths:** Use UI for `Skipped`, `Error`, etc. Verify correct `curation_status` and no incorrect processing triggers.

### 5.4 Final Documentation Considerations (Optional)

- Document specific failure modes and recovery procedures.
- Consider a state machine diagram for status transitions.
- Document cross-workflow references if applicable.

## Implementation Checklist

Use this checklist during and after implementation:

- [ ] **Phase 1: Definition & Schema**
  - [ ] Workflow purpose and tables defined (Questionnaire 1.1, 1.2)
  - [ ] Database enum types created manually (SQL 1.4)
  - [ ] Status fields added to source table via migration (SQL 1.3)
  - [ ] Python enum classes defined in codebase (Python 1.5)
- [ ] **Phase 2: Consumer Endpoint**
  - [ ] API request schema created (Python 2.1.1)
  - [ ] Router endpoint implemented with dual-status logic (Python 2.1.2)
  - [ ] Router registered in main.py (Python 2.1.3)
  - [ ] General API schemas created (Python 2.2)
- [ ] **Phase 3: Background Service**
  - [ ] Scheduler polling function implemented (Python 3.1)
  - [ ] Scheduler setup function defined (Python 3.2, Step 1)
  - [ ] Scheduler setup called from main.py (Python 3.2, Step 2)
- [ ] **Phase 4: Curation Service**
  - [ ] Processing service function implemented (Python 4.1)
  - [ ] Logic correctly handles update-source vs create-destination pattern
- [ ] **Phase 4.5: Frontend Components (if UI-driven)**
  - [ ] HTML tab structure added (HTML 4.5.1)
  - [ ] JavaScript logic implemented for loading, selection, and API calls (JS 4.5.2)
- [ ] **Phase 5: Testing**
  - [ ] Unit/Integration tests created (Pytest 5.2)
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

</rewritten_file>
