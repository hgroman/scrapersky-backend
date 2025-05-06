# ScraperSky Workflow Builder Cheat Sheet

## Introduction: The Strategy-First Approach

This guide provides a methodical, strategic approach to creating new ScraperSky workflows based on the producer-consumer pattern. **IMPORTANT:** Building a workflow is NOT simply coding from templates—it requires careful planning, system analysis, and deliberate decision-making.

Each workflow implementation follows three key stages:

1. **PLAN**: Analyze requirements, survey existing code, and make strategic decisions
2. **VALIDATE**: Review your plan with peers, document rationales, and confirm compatibility
3. **IMPLEMENT**: Execute the validated plan following ScraperSky architectural principles

Never rush to implementation before thoroughly completing the planning and validation stages. The checklists and decision points in this document are designed to guide your planning process, not simply list files to create.

### Using This Document Effectively

1. **System Analysis First**: Before writing any code, thoroughly assess how your workflow will integrate with existing components
2. **Document Decisions**: Use the decision points to record your rationale and approach
3. **File Verification**: Always check if files already exist before creating new ones
4. **Strategic Integration**: Consider how your additions impact the overall system architecture

> **Reference:** See the [Producer-Consumer Workflow Pattern](../Docs_7_Workflow_Canon/PRODUCER_CONSUMER_WORKFLOW_PATTERN.md) document for the authoritative pattern definition.

## CRITICAL NAMING CONVENTION

**THE WORKFLOW NAME DEFINES ALL NAMING CONVENTIONS THROUGHOUT THE IMPLEMENTATION**

The workflow name you choose in Phase 1 (e.g., "contact_extraction") will define:

- Database field names (`contact_extraction_curation_status`, `contact_extraction_status`)
- Enum type names (`contactextractionstatusenum`)
- Service file names (`contact_extraction_service.py`, `contact_extraction_scheduler.py`)
- UI component IDs (`contact-extraction-tab`)
- Function names (`process_contact_extraction_queue`)

This consistency is **MANDATORY** and ensures all components are correctly linked throughout the system.

## Implementation Workflow Summary

Each workflow follows five strategic phases that correspond to both planning and implementation steps:

1. **Phase 1: Strategic Planning & Schema Design** - Define workflow purpose and data structures
2. **Phase 2: Consumer Interface Architecture** - Design APIs and user interaction patterns
3. **Phase 3: Processing Pipeline Design** - Architect background processing components
4. **Phase 4: Enrichment Logic Development** - Design data transformation approach
5. **Phase 5: Verification & Validation** - Create test strategies and validation mechanisms

## Progress Tracking

- [ ] Phase 1: Strategic Planning & Schema Design
  - [ ] Step 1.1.1: Analyze workflow requirements
  - [ ] Step 1.1.2: Map data relationships
  - [ ] Step 1.2.1: Design database schema changes
  - [ ] Step 1.3.1: Plan enum structure
  - [ ] Step 1.4.1: Design Python model representations

- [ ] Phase 2: Consumer Interface Architecture
  - [ ] Step 2.1.1: Design API contract
  - [ ] Step 2.2.1: Plan router structure
  - [ ] Step 2.3.1: Analyze main.py integration
  - [ ] Step 2.4.1: Assess frontend integration needs
  - [ ] Step 2.4.2: Plan UI component structure (if needed)
  - [ ] Step 2.4.3: Design UI interactions (if needed)

- [ ] Phase 3: Processing Pipeline Design
  - [ ] Step 3.1.1: Design background processor architecture
  - [ ] Step 3.2.1: Plan scheduler configuration

- [ ] Phase 4: Enrichment Logic Development
  - [ ] Step 4.1.1: Design service architecture
  - [ ] Step 4.2.1: Architect data extraction approach

- [ ] Phase 5: Verification & Validation
  - [ ] Step 5.1.1: Design verification strategy
  - [ ] Step 5.2.1: Plan automated testing approach
  - [ ] Step 5.3.1: Develop manual testing protocol

## Phase 1: Strategic Planning & Schema Design

### Phase 1 Overview

The first phase focuses on understanding the workflow's purpose, data flow, and integration points **before** any implementation occurs. This planning phase is critical to ensure your workflow aligns with ScraperSky's architecture.

### 1.1 Workflow Analysis

#### System Integration Assessment

- [ ] **STEP 1.1.1: Analyze workflow requirements**

Before making any decisions, analyze how this workflow fits within the broader system:

1. **Examine Existing Workflows**: Review similar workflows in the system
   ```
   Document similar workflows you reviewed:


   ```

2. **Identify Integration Points**: Where will this workflow connect with existing components?
   ```
   Record key integration points:


   ```

3. **Define Core Parameters**: Now that you understand the system context, define your workflow's core parameters:

| Question                                    | Example Answer                            | Your Answer | Rationale for Your Answer |
| ------------------------------------------- | ----------------------------------------- | ----------- | ------------------------- |
| **What is the workflow name?** (snake_case) | `contact_extraction`                      |             |                           |
| What is the purpose of the data enrichment? | Extract contact information from webpages |             |                           |
| What is the source table?                   | `pages`                                   |             |                           |
| What is the destination table?              | `contacts`                                |             |                           |

> **CRITICAL**: The workflow name you choose (e.g., `contact_extraction`) determines ALL naming patterns throughout your implementation. It must be in snake_case format and should clearly describe the workflow's purpose.

4. **Verify Table Existence**: Before proceeding, confirm if the tables already exist or need creation
   ```
   Document your findings about existing tables:

   Source table status: [Exists/Needs Creation]
   Destination table status: [Exists/Needs Creation]
   ```

**✓ CHECKPOINT**: Have you completed the workflow analysis with a thorough understanding of the system context? Discuss with your team before proceeding.

### 1.2 Data Flow Analysis

- [ ] **STEP 1.1.2: Map data relationships and process requirements**

Before considering implementation details, analyze the data and processing requirements:

1. **Process Characteristics Analysis**:

| Question                                            | Example Answer               | Your Answer | Strategic Implications |
| --------------------------------------------------- | ---------------------------- | ----------- | ---------------------- |
| Will this have a UI component?                      | Yes                          |             |                        |
| Is this a background-only process?                  | No                           |             |                        |
| Does it update existing records or create new ones? | Creates new records          |             |                        |
| Estimated processing time per record                | > 5 seconds (background)     |             |                        |
| What specific fields from source table are needed?  | page_content, url            |             |                        |
| What verification/validation is required?           | Check for valid email format |             |                        |

2. **Data Dependency Map**: Document how data flows between components
   ```
   Describe the data flow path from source to destination:


   ```

3. **Processing Volume Assessment**: Estimate processing load and frequency
   ```
   Document your throughput expectations:

   Estimated records per day:
   Peak processing periods:
   Impact on other system components:
   ```

**✓ CHECKPOINT**: Have you documented the complete data flow and processing requirements? Review with your team before proceeding.

### 1.3 Schema Design

- [ ] **STEP 1.2.1: Design database schema changes**

Based on your workflow analysis, now design the necessary database schema changes:

1. **Schema Change Strategy**: Before writing any SQL, consider:
   - Will these changes impact existing workflows?
   - Are there existing fields that serve similar purposes?
   - Is this schema design consistent with similar workflows?

   ```
   Document your schema design rationale:


   ```

2. **Review Existing Schema**: Check if similar fields already exist
   ```
   Document your findings from existing schema review:


   ```

3. **Schema Change Design**: Now draft your schema changes

```sql
-- Add to source table (e.g., pages)
ALTER TABLE {source_table} ADD COLUMN {workflow_name}_curation_status {source_table}curationstatus NOT NULL DEFAULT 'New';

-- NOTE: The processing status column (below) should typically allow NULLs and default to NULL.
-- It should only be set to 'Queued' (or other initial processing state) when the curation status
-- is explicitly updated via the API (e.g., to 'Selected' or 'Queued').
ALTER TABLE {source_table} ADD COLUMN {output_table}_extraction_status {output_table}extractionstatusenum NULL;

-- Add an error field if the processing step can fail
-- ALTER TABLE {source_table} ADD COLUMN {output_table}_extraction_error TEXT NULL;
```

**DECISION POINT**: After reviewing the system, which schema approach will you use?
- [ ] Standard schema pattern (above) - justify why this is appropriate
- [ ] Modified schema pattern - explain required modifications and why
- [ ] Alternative approach - describe your approach and rationale

Justify your decision:
```


```

> **Reference:** See [Database Schema Change Guide](../Docs_1_AI_GUIDES/18-DATABASE_SCHEMA_CHANGE_GUIDE.md) for standardized table modifications.

### 1.4 Enum Strategy

- [ ] **STEP 1.3.1: Plan enum structure**

Before implementing enums, evaluate the status tracking needs and system integration requirements:

1. **Status Tracking Analysis**: Analyze the workflow stages and status tracking requirements
   ```
   Document your analysis of the workflow stages:

   User-facing states needed:
   Background processing states needed:
   Special conditions or exceptions to handle:
   ```

2. **Enum Location Strategy**: Determine where enums should be defined
   ```
   Document your enum location strategy:

   Check for existing enum patterns in similar workflows:
   Assess potential for enum reuse across workflows:
   Determine optimal location for new enums:
   ```

3. **Database Enum Design**: Based on your analysis, design your database enums

```sql
-- Curation status enum (user-driven queue)
CREATE TYPE {source_table}curationstatus AS ENUM ('New', 'Queued', 'Processing', 'Complete', 'Error', 'Skipped');

-- Processing status enum (background processing)
CREATE TYPE {output_table}extractionstatusenum AS ENUM ('New', 'Queued', 'Processing', 'Complete', 'Error');
```

**DECISION POINT**: After analyzing existing patterns, which enum approach will you use?

- [ ] Standard enum patterns (above) - explain why these meet your requirements
- [ ] Modified enum values - specify modifications and justify them
- [ ] Alternative approach - describe in detail with rationale

Justify your decision:
```


```

> **Reference:** See [Enum Handling Standards](../Docs_1_AI_GUIDES/27-ENUM_HANDLING_STANDARDS.md) and [Database Enum Isolation](../Docs_1_AI_GUIDES/29-DATABASE_ENUM_ISOLATION.md).

### 1.5 Python Model Design

- [ ] **STEP 1.4.1: Design Python model representations**

After designing the database structure, plan how Python will represent these enums:

1. **Code Organization Strategy**: Consider the optimal location for these enums
   ```
   Document your enum code organization strategy:

   Examine where similar enums are defined in the codebase:
   Assess the impact of your placement decision on imports elsewhere:
   Determine if a new file is needed or existing files should be extended:
   ```

2. **File Existence Check**: Look for files where these enums might need to be added
   ```
   Document your file check findings:

   Does src/models/enums.py exist? [Yes/No]
   If yes, what similar enums are already defined there?
   Would adding these enums create circular imports? [Yes/No/Needs Investigation]
   ```

3. **Python Enum Design**: Based on your research, design your Python enum classes

```python
class {SourceTable}CurationStatus(str, Enum):
    New = "New"
    Queued = "Queued"
    Processing = "Processing"
    Complete = "Complete"
    Error = "Error"
    Skipped = "Skipped"

class {OutputTable}ExtractionStatusEnum(str, Enum):
    New = "New"
    Queued = "Queued"
    Processing = "Processing"
    Complete = "Complete"
    Error = "Error"
```

**DECISION POINT**: After examining the codebase, how will you implement Python enums?

- [ ] Standard pattern in src/models/enums.py - justify this approach
- [ ] Alternative location - specify where and why
- [ ] Different implementation pattern - describe and justify

Justify your decision with references to existing code:
```


```

> **Reference:** See [Enum Handling Standards](../Docs_1_AI_GUIDES/27-ENUM_HANDLING_STANDARDS.md)

**✓ CHECKPOINT**: Have you completed the planning stages of Phase 1? Review your decisions with your team before proceeding to Phase 2.

## Phase 2: Consumer Endpoint Construction

This phase creates the CRUD interface for user row selection and batch updates.

class {SourceTable}BatchStatusUpdateRequest(BaseModel):
    ids: List[UUID]
    status: {SourceTable}CurationStatus
```

**DECISION POINT**: After analyzing existing patterns, which request schema approach will you use?

- [ ] Standard pattern shown above - explain why this meets your requirements
- [ ] Modified schema - specify additions/changes and justify them
- [ ] Alternative approach - describe in detail with rationale

Justify your decision with reference to existing code patterns:
```


```

> **Reference:** See [API Standardization Guide](../Docs_1_AI_GUIDES/15-API_STANDARDIZATION_GUIDE.md) for request model patterns.

### 2.2 Endpoint Architecture

- [ ] **STEP 2.2.1: Plan router structure and implementation strategy**

Before implementing the router, design the endpoint architecture:

1. **Router File Analysis**: Determine if you should extend an existing router or create a new one
   ```
   Document your router file analysis:

   Examine existing router files:
   Does a router for similar functionality already exist? [Yes/No]
   If yes, which file and what endpoints does it already handle?
   If creating a new router, what should it be named and what URL prefix should it use?
   ```

2. **State Update Strategy**: Design how status changes will flow through the system
   ```
   Document your state update strategy:

   Will this follow the dual-status update pattern? [Yes/No] Why?
   What database operations will be required?
   How will the router handle optimistic locking or concurrent updates?
   ```

3. **Transaction Boundary Planning**: Determine the transaction scope for your endpoint
   ```
   Document your transaction boundary plan:

   What operations need to be atomic?
   Are there any operations that should be outside the transaction?
   How will you handle partial failures?
   ```

4. **Endpoint Implementation Design**: Based on your analysis, design your endpoint structure:

```python
# Planned for src/routers/{source_table}s.py or src/routers/{workflow_name}.py
@router.post("/api/v3/{source_table}s/update-{workflow_name}-status", response_model=GenericResponse)
async def update_{source_table}_{workflow_name}_status(
    request: {SourceTable}BatchStatusUpdateRequest,
    session: AsyncSession = Depends(get_session_dependency),
    current_user: UserInToken = Depends(get_current_user),
```

**DECISION POINT**: After analyzing the system, which endpoint implementation approach will you use?

- [ ] Standard implementation shown above - explain why this meets your requirements
- [ ] Modified implementation - specify key changes and justify them
- [ ] Alternative approach - describe in detail with rationale

Justify your decision with reference to architectural principles and existing patterns:
```


```

> **Reference:** See [Authentication Boundary](../Docs_1_AI_GUIDES/11-AUTHENTICATION_BOUNDARY.md), [Transaction Management Guide](../Docs_1_AI_GUIDES/13-TRANSACTION_MANAGEMENT_GUIDE.md), and [FastAPI Router Prefix Convention](../Docs_1_AI_GUIDES/23-FASTAPI_ROUTER_PREFIX_CONVENTION.md).

### 2.3 Application Integration Planning

- [ ] **STEP 2.3.1: Analyze main.py integration**

Before modifying the application's entry point, analyze how your router will integrate:

1. **main.py Structure Analysis**: Examine the current structure of main.py
   ```
   Document your main.py analysis:

   Current router registration pattern:
   Tag naming conventions observed:
   Import organization strategy:
   ```

2. **Integration Impact Assessment**: Consider the impact of your addition
   ```
   Document your integration impact assessment:

   Will this router affect startup sequence?
   Are there any dependency conflicts to consider?
   How will this change impact application routes documentation?
   ```

3. **Router Registration Design**: Based on your analysis, design your router registration:

```python
# Planned addition to src/main.py
from src.routers.{source_table}s import router as {source_table}_router
# ...
app.include_router({source_table}_router, tags=["{source_table.title()}s"])
```

**DECISION POINT**: After analyzing the application structure, how will you integrate your router?

- [ ] Standard pattern shown above - explain why this meets your requirements
- [ ] Modified approach - specify what needs to be different and why
- [ ] Alternative implementation - describe in detail with rationale

Justify your decision with reference to the existing main.py structure:
```


```

**✓ CHECKPOINT**: Have you completed the planning for API components? Review your decisions before proceeding.

### 2.4 Frontend Integration Strategy (if applicable)

- [ ] **STEP 2.4.1: Assess frontend integration needs**

If your workflow requires user interface components, strategize how they'll integrate:

1. **UI Requirement Analysis**: Determine if and what UI components are needed
   ```
   Document your UI requirement analysis:

   Does this workflow need user interaction? [Yes/No] Why?
   What selection/filtering capabilities are required?
   What status information needs to be displayed?
   ```

2. **UI Integration Points**: Identify where and how UI components will integrate
   ```
   Document your UI integration strategy:

   Should this be a separate tab or integrated into existing views?
   Are there existing UI patterns for similar workflows?
   What frontend technologies/frameworks will be used?
   ```

**DECISION POINT**: Based on your analysis, what frontend approach will you take?

- [ ] This workflow does not require UI components - explain why
- [ ] Build standard UI components following existing patterns - describe which patterns
- [ ] Create custom UI components - justify why custom components are needed

Justify your decision:
```


```

**✓ CHECKPOINT**: Have you completed all planning steps for Phase 2? Review with your team before proceeding to Phase 3.

## Phase 3: Processing Pipeline Design

### Phase 3 Overview

This phase focuses on architecting the background processing system that will monitor for queued records and process them. Before implementing any code, carefully consider how this component integrates with the existing scheduler infrastructure.

### 3.1 Background Processor Architecture

- [ ] **STEP 3.1.1: Design background processor architecture**

Before implementing the scheduler, analyze and design your background processing approach:

1. **Scheduler Pattern Analysis**: Review existing scheduler patterns in the system
   ```
   Document your scheduler pattern analysis:

   Existing scheduler patterns for similar workflows:
   Common batch sizes and processing strategies:
   Error handling approaches in other schedulers:
   ```

2. **Concurrency Strategy**: Determine how to handle concurrent processing
   ```
   Document your concurrency strategy:

   How will you prevent duplicate processing of records?
   What locking mechanism is appropriate?
   How will you handle long-running processes?
   ```

3. **Transaction Design**: Plan transaction boundaries for your processor
   ```
   Document your transaction boundary plan:

   Which operations need to be in the same transaction?
   What operations should be outside transaction boundaries?
   How will you handle failure scenarios?
   ```

4. **Scheduler Implementation Design**: Based on your analysis, design your scheduler structure:

```python
# Planned for src/schedulers/{workflow_name}_scheduler.py
async def process_{source_table}_queue():
    session = await get_background_session()
    try:
        # First transaction: find and lock records for processing
        async with session.begin():
            # Find records with curation status 'Queued'
            stmt = (
                select({SourceTable})
                .where({SourceTable}.{workflow_name}_curation_status == {SourceTable}CurationStatus.Queued)
                .with_for_update(skip_locked=True)
                .limit(10)  # Process in batches
            )
            result = await session.execute(stmt)
            records = result.scalars().all()

            # Mark them as 'Processing'
            if records:
                record_ids = [record.id for record in records]
                update_stmt = (
                    update({SourceTable})
                    .where({SourceTable}.id.in_(record_ids))
                    .values({workflow_name}_curation_status={SourceTable}CurationStatus.Processing)
                )
                await session.execute(update_stmt)

        # Process each record outside the transaction
        for record_id in record_ids:
            try:
                await process_single_{source_table}(session, record_id)
            except Exception as e:
                logger.error(f"Error processing {source_table} {record_id}: {str(e)}")
                # Update status to Error
                async with session.begin():
                    error_stmt = (
                        update({SourceTable})
                        .where({SourceTable}.id == record_id)
                        .values(
                            {workflow_name}_curation_status={SourceTable}CurationStatus.Error,
                            error_message=str(e)
                        )
                    )
                    await session.execute(error_stmt)

    except Exception as e:
        logger.error(f"Error in {source_table} processing scheduler: {str(e)}")
    finally:
        await session.close()
```

**DECISION POINT**: After analyzing existing schedulers, which scheduler implementation approach will you use?

- [ ] Standard pattern shown above - explain why this meets your requirements
- [ ] Modified implementation - specify key modifications and justify them
- [ ] Alternative approach - describe your custom approach and rationale

Justify your decision with reference to system requirements and existing patterns:
```


```

> **Reference:** See [Scheduled Tasks APScheduler Pattern](../Docs_1_AI_GUIDES/21-SCHEDULED_TASKS_APSCHEDULER_PATTERN.md), [Shared Scheduler Integration Guide](../Docs_1_AI_GUIDES/24-SHARED_SCHEDULER_INTEGRATION_GUIDE.md), and [Background Services Architecture](../Docs_6_Architecture_and_Status/BACKGROUND_SERVICES_ARCHITECTURE.md).

### 3.2 Scheduler Configuration Planning

- [ ] **STEP 3.2.1: Plan scheduler configuration**

Before registering your scheduler, analyze configuration requirements:

1. **Scheduler Integration Analysis**: Examine the current scheduler infrastructure
   ```
   Document your scheduler integration analysis:

   Current scheduler configuration patterns:
   Job naming conventions in use:
   Typical intervals for similar jobs:
   ```

2. **Resource Impact Assessment**: Evaluate the processing load impact
   ```
   Document your resource impact assessment:

   Estimated processing time per record:
   Expected queue volumes:
   Potential impact on database load:
   ```

3. **Scheduling Strategy**: Determine appropriate interval and configuration
   ```
   Document your scheduling strategy:

   Optimal processing interval (and why):
   Job priority considerations:
   Graceful shutdown requirements:
   ```

4. **Scheduler Registration Design**: Based on your analysis, design your job registration:

```python
# Planned addition to src/schedulers.py
scheduler.add_job(
    process_{source_table}_queue,
    'interval',
    seconds=30,
    id=f"{output_table}_extraction_scheduler",
    replace_existing=True
)
```

**DECISION POINT**: Based on your system analysis, what scheduler configuration will you use?

- [ ] Standard configuration (30-second interval) - explain why this is appropriate
- [ ] Custom interval - specify interval and justify with workload calculations
- [ ] Advanced configuration - describe additional parameters needed and why

Justify your decision with workload analysis:
```


```

> **Reference:** See [Scheduler and Settings Patterns](../Docs_1_AI_GUIDES/28-SCHEDULER_AND_SETTINGS_PATTERNS.md) for scheduler registration standards.

**✓ CHECKPOINT**: Have you completed the planning for your background processing pipeline? Review with your team before proceeding to Phase 4.

## Phase 4: Enrichment Logic Development

### Phase 4 Overview

This phase focuses on designing the core data transformation logic that powers your workflow. Before implementing code, carefully plan how your service will handle the data enrichment process.

### 4.1 Service Architecture Design

- [ ] **STEP 4.1.1: Design service architecture**

Before implementing the service, analyze requirements and design your approach:

1. **Service Pattern Analysis**: Review existing service patterns in the system
   ```
   Document your service pattern analysis:

   Similar services in the codebase:
   Common transaction patterns observed:
   Error handling strategies used elsewhere:
   ```

2. **Transaction Boundary Planning**: Design your transaction boundaries
   ```
   Document your transaction strategy:

   Which operations must be atomic?
   What operations should be outside transactions?
   How will you handle partial success/failure?
   ```

3. **Error Handling Strategy**: Plan how to handle and report errors
   ```
   Document your error handling strategy:

   What types of errors do you anticipate?
   How will error information be preserved?
   Will retries be implemented?
   ```

4. **Service Implementation Design**: Based on your analysis, design your service structure:

```python
# Planned for src/services/{output_table}_extraction_service.py
async def process_single_{source_table}(
    session: AsyncSession,
    {source_table}_id: UUID,
) -> None:
    try:
        # Step 1: Retrieve the source record
        async with session.begin():
            stmt = select({SourceTable}).where({SourceTable}.id == {source_table}_id)
            result = await session.execute(stmt)
            source_record = result.scalars().first()

            if not source_record:
                raise ValueError(f"{SourceTable} with ID {source_table}_id not found")

            # Update extraction status to Processing
            source_record.{output_table}_extraction_status = {OutputTable}ExtractionStatusEnum.Processing

        # Step 2: Perform the actual data enrichment (outside transaction)
        # Example: Extract emails from page content
        extracted_data = await perform_extraction(source_record)

        # Step 3: Create output records with results
        async with session.begin():
            # Create new records in destination table
            for item in extracted_data:
                new_record = {OutputTable}(
                    id=uuid4(),
                    {source_table}_id=source_record.id,
                    # Add other fields from extracted_data
                    created_at=datetime.utcnow()
                )
                session.add(new_record)

            # Update source record status to Complete
            update_stmt = (
                update({SourceTable})
                .where({SourceTable}.id == {source_table}_id)
                .values(
                    {workflow_name}_curation_status={SourceTable}CurationStatus.Complete,
                    {output_table}_extraction_status={OutputTable}ExtractionStatusEnum.Complete,
                )
            )
            await session.execute(update_stmt)

    except Exception as e:
        # Update statuses to Error on exception
        async with session.begin():
            error_stmt = (
                update({SourceTable})
                .where({SourceTable}.id == {source_table}_id)
                .values(
                    {workflow_name}_curation_status={SourceTable}CurationStatus.Error,
                    {output_table}_extraction_status={OutputTable}ExtractionStatusEnum.Error,
                    error_message=str(e)
                )
            )
            await session.execute(error_stmt)
        raise

# Helper function for the actual data extraction
async def perform_extraction(source_record):
    # Implement your specific extraction logic here
    # Example: Extract emails from page content
    extracted = []

    # Simple example: extract email-like patterns from page content
    if hasattr(source_record, 'content') and source_record.content:
        import re
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        emails = re.findall(email_pattern, source_record.content)
        for email in emails:
            extracted.append({"email": email})

    return extracted
```

**DECISION POINT**: After analyzing the system, which service architecture will you implement?

- [ ] Standard service pattern shown above - explain why this meets your requirements
- [ ] Modified service structure - specify your changes and justify them
- [ ] Alternative approach - describe in detail with rationale

Justify your decision with reference to architectural principles and existing patterns:
```


```

### 4.2 Data Extraction Strategy

- [ ] **STEP 4.2.1: Architect data extraction approach**

Before implementing the data extraction logic, design your approach:

1. **Data Transformation Requirements**: Identify exactly what data needs to be extracted and transformed
   ```
   Document your data transformation requirements:

   Source data fields to process:
   Target data structure needed:
   Required transformations or enrichments:
   ```

2. **Algorithm Selection Strategy**: Determine the most appropriate extraction techniques
   ```
   Document your algorithm selection strategy:

   Potential techniques for extraction (regex, ML, parsing, etc.):
   Performance considerations for chosen approaches:
   Error tolerance and validation requirements:
   ```

3. **External Dependencies**: Identify any external services or libraries needed
   ```
   Document your dependency strategy:

   External libraries or services required:
   Fallback mechanisms if dependencies fail:
   Performance impact of external calls:
   ```

4. **Extraction Logic Design**: Based on your analysis, design your extraction approach:

```python
# Planned implementation for the extraction logic
async def perform_extraction(source_record):
    # Implement your specific extraction logic here
    # Example: Extract emails from page content
    extracted = []

    # Simple example: extract email-like patterns from page content
    if hasattr(source_record, 'content') and source_record.content:
        import re
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        emails = re.findall(email_pattern, source_record.content)
        for email in emails:
            extracted.append({"email": email})

    return extracted
```

**DECISION POINT**: After analyzing requirements, which extraction approach will you implement?

- [ ] Standard approach shown above - explain why this meets your requirements
- [ ] Custom algorithm - describe your algorithm and justify its selection
- [ ] External service integration - describe the service and integration approach

Justify your decision with reference to data requirements and performance considerations:
```


```

> **Reference:** See [Service Layer Pattern](../Docs_1_AI_GUIDES/07-SERVICE_LAYER_PATTERN.md), [Absolute ORM Requirement](../Docs_1_AI_GUIDES/01-ABSOLUTE_ORM_REQUIREMENT.md), and [Transaction Management Guide](../Docs_1_AI_GUIDES/13-TRANSACTION_MANAGEMENT_GUIDE.md).

**✓ CHECKPOINT**: Have you completed planning for the data enrichment components? Review with your team before proceeding to Phase 5.

### 2.4 Frontend Components (if UI-driven)

Create the necessary frontend components for user interaction:

#### 2.4.1 HTML Tab

Add to `templates/scraper-sky-mvp.html`:

```html
<div class="tab-pane" id="{workflow-name}-tab">
  <div class="container">
    <div class="row mt-3">
      <div class="col-12">
        <h4>{WorkflowName} Management</h4>
        <div class="card">
</div>
```

**DECISION POINT**: Will you use the standard HTML table template above?
- [ ] Yes, use the standard template (recommended)
- [ ] No, I need to customize the HTML for my specific needs

If you selected "No", please describe your custom HTML requirements:
```html
<!-- Your custom HTML here -->
```

#### 2.4.3 JavaScript for Batch Selection and Updates

- [ ] **STEP 2.4.3: Create JavaScript for UI interactions**

```javascript
$(document).ready(function() {
    // Load initial data
    load{SourceTable}Data();
{{ ... }}
$(document).ready(function() {
    // Load initial data
    load{SourceTable}Data();

    // Select all checkbox
    $("#selectAll").on("change", function() {
        $(".row-checkbox").prop("checked", $(this).prop("checked"));
    });

    // Queue selected items
    $("#queueSelected").on("click", function() {
        updateSelectedStatus('{SourceTable}CurationStatus.Queued');
    });

    // Skip selected items
    $("#skipSelected").on("click", function() {
        updateSelectedStatus('{SourceTable}CurationStatus.Skipped');
    });
});

function load{SourceTable}Data() {
    $.ajax({
{{ ... }}
    });
});

function load{SourceTable}Data() {
    $.ajax({
        url: '/api/v3/{source_table}s',
        method: 'GET',
        success: function(response) {
            const {source_table}s = response.{source_table}s || [];
            populateTable({source_table}s);
        },
        error: function(error) {
            console.error('Error loading {source_table}s:', error);
        }
    });
}

function populateTable({source_table}s) {
    const tbody = $("#{source_table}Table tbody");
    tbody.empty();

    {source_table}s.forEach(function({source_table}) {
        tbody.append(`
            <tr>
                <td><input type="checkbox" class="row-checkbox" value="${{{source_table}.id}}"></td>
                <td>${{{source_table}.id}}</td>
                <td>${{{source_table}.title || {source_table}.name || 'N/A'}}</td>
                <td>${{{source_table}.{workflow_name}_curation_status}}</td>
                <td>
                    <button class="btn btn-sm btn-info view-btn" data-id="${{{source_table}.id}}">View</button>
                </td>
            </tr>
        `);
    });
}

{{ ... }}
            </tr>
        `);
    });
}

function updateSelectedStatus(status) {
    const selectedIds = [];
    $(".row-checkbox:checked").each(function() {
        selectedIds.push($(this).val());
    });

    if (selectedIds.length === 0) {
        alert('Please select at least one {source_table}');
        return;
    }

    $.ajax({
        url: '/api/v3/{source_table}s/update-{workflow_name}-status',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({
            ids: selectedIds,
            status: status
        }),
        success: function(response) {
            alert(response.message);
            load{SourceTable}Data(); // Reload the table
        },
        error: function(error) {
            console.error('Error updating status:', error);
            alert('Error updating status. See console for details.');
        }
    });
}
```

**DECISION POINT**: Will you use the standard JavaScript implementation above?
- [ ] Yes, use the standard implementation (recommended)
- [ ] No, I need to customize the JavaScript for my specific needs

If you selected "No", please describe your custom JavaScript requirements:
```javascript
// Your custom JavaScript here
```

**✓ CHECKPOINT**: Have you completed all of Phase 2, including frontend components if needed? Type `Yes` to continue to Phase 3.
function showNotification(title, message) {
    // Implement notification display
    alert(`${title}: ${message}`);
}
```
{{ ... }}
> **Reference:** See [Curation Workflow Operating Manual](../Docs_6_Architecture_and_Status/0.4_Curation%20Workflow%20Operating%20Manual.md) for frontend integration patterns.

## Phase 5: Verification & Validation

### Phase 5 Overview

The final phase focuses on designing a comprehensive testing strategy to ensure that all components work correctly together. Before implementing any tests, plan your verification approach carefully.

### 5.1 Verification Strategy Design

- [ ] **STEP 5.1.1: Design verification strategy**

Before testing, design a comprehensive verification strategy:

1. **Testing Requirements Analysis**: Identify critical verification points
   ```
   Document your verification requirements:

   Critical workflow states to verify:
   Key integration points that need testing:
   Potential failure scenarios to test:
   ```

2. **Test Coverage Planning**: Design a coverage strategy for verification
   ```
   Document your test coverage plan:

   Components requiring unit tests:
   Integration test boundaries:
   End-to-end test scenarios:
   ```

3. **Validation Success Criteria**: Define what constitutes successful validation
   ```
   Document your success criteria:

   Database state expectations:
   Performance requirements:
   Error handling expectations:
   ```

4. **Verification Checklist**: Based on your analysis, create a comprehensive verification plan:

- [ ] Database schema verification strategy:
   ```
   How will you verify schema changes?
   ```
- [ ] API endpoint validation approach:
   ```
   How will you test API contracts and responses?
   ```
- [ ] UI interaction verification plan:
   ```
   How will you test frontend interactions?
   ```
- [ ] Background processing verification method:
   ```
   How will you validate the scheduler and processing logic?
   ```
- [ ] Status transition validation strategy:
   ```
   How will you verify all status transitions work correctly?
   ```
- [ ] Error handling verification approach:
   ```
   How will you test error conditions?
   ```

### 5.2 Test Architecture Design

- [ ] **STEP 5.2.1: Plan automated testing approach**

After defining your verification strategy, design your test architecture:

1. **Test Framework Selection**: Choose appropriate testing tools and frameworks
   ```
   Document your test framework decisions:

   Unit testing approach:
   Integration testing tools:
   Mock/stub strategy:
   ```

2. **Test Data Strategy**: Plan how to create and manage test data
   ```
   Document your test data strategy:

   Test data generation approach:
   Database fixture requirements:
   Test isolation approach:
   ```

3. **Test Implementation Design**: Based on your strategy, design your tests:

```python
# Planned test implementation for {workflow_name} workflow

# 1. API endpoint test design
async def test_{source_table}_status_update():
    # Setup: Create test records
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Execute: Update status
        response = await client.post(
            f"/api/v3/{source_table}s/update-{workflow_name}-status",
            json={"ids": [test_id], "status": "{SourceTable}CurationStatus.Queued"}
        )
        # Verify: Status code and response structure
        assert response.status_code == 200
        assert "message" in response.json()

# Additional test designs based on your verification strategy...
```

**DECISION POINT**: Based on your analysis, which testing approach will you implement?

- [ ] Comprehensive automated test suite - describe scope and coverage
- [ ] Hybrid approach with both automated and manual tests - describe balance
- [ ] Primarily manual testing with key automated tests - justify this approach

Justify your decision with reference to project requirements and resource constraints:
```


```

> **Reference:** See [Comprehensive Test Plan](../Docs_1_AI_GUIDES/06-COMPREHENSIVE_TEST_PLAN.md) for testing methodology and patterns.

### 5.3 Validation Protocol Design

- [ ] **STEP 5.3.1: Develop manual testing protocol**

Design a repeatable protocol for manual verification when needed:

1. **Validation Scenario Design**: Create comprehensive test scenarios
   ```
   Document your validation scenarios:

   Happy path validation scenarios:
   Error path validation scenarios:
   Edge case validation scenarios:
   ```

2. **Verification Protocol**: Design step-by-step verification steps
   ```
   Document your verification protocol:

   1. System preparation steps:
   2. Test execution process:
   3. Verification checkpoints:
   4. Results documentation approach:
   ```

3. **Production Readiness Criteria**: Define when the workflow is ready for production
   ```
   Document your production readiness criteria:

   Required test pass rate:
   Performance thresholds:
   Documentation requirements:
   ```

**✓ CHECKPOINT**: Have you completed the planning for verification and validation? Review with your team before proceeding to implementation.

## Planning Phase Complete

Congratulations! You have completed the strategic planning for all phases of your ScraperSky workflow. With this comprehensive plan, you are now prepared to proceed to the implementation phase with a clear understanding of:

1. How your workflow integrates with the system architecture
2. The exact components you'll need to implement
3. Where potential challenges might arise
4. How you'll verify that everything works correctly

This planning-first approach ensures that your implementation will be both efficient and aligned with ScraperSky's architectural principles.

**NEXT STEP**: Proceed to implementation following your strategic plan, or review any parts of the plan that need refinement before beginning implementation.

## Implementation Checklist

Use this checklist to ensure all components are implemented correctly:

- [ ] **Phase 1: Definition & Schema**

  - [ ] Workflow purpose defined
  - [ ] Source and destination tables identified
  - [ ] Database enum types created
  - [ ] Status fields added to source table
  - [ ] Python enum classes defined

- [ ] **Phase 2: Consumer Endpoint**

  - [ ] API request schema created
  - [ ] Router implemented with status update endpoint
  - [ ] Router registered in main.py
  - [ ] Frontend components created (if UI-driven)

- [ ] **Phase 3: Background Service**

  - [ ] Scheduler implemented
  - [ ] Scheduler registered in schedulers.py
  - [ ] Error handling implemented

- [ ] **Phase 4: Curation Service**

  - [ ] Data enrichment service implemented
  - [ ] Transaction boundaries properly managed
  - [ ] Status updates handled correctly
  - [ ] Error cases handled gracefully

- [ ] **Phase 5: Testing**
  - [ ] Unit tests created
  - [ ] Integration tests created
  - [ ] Manual testing completed
  - [ ] Error scenarios tested

## Example: Pages to Contacts Workflow Implementation

Following the 5-phase approach for extracting emails from pages to contacts:

### Phase 1: Questionnaire & Schema

- **Purpose:** Extract contact information (emails) from web pages
- **Source table:** `pages`
- **Destination table:** `contacts`
- **Status fields:** `contact_extraction_curation_status`, `contact_extraction_status`
- **Enum types:** `pagecurationstatus`, `contactextractionstatusenum`

### Phase 2: Consumer Endpoint

- **Router:** `src/routers/pages.py` with `/api/v3/pages/update-status`
- **UI:** Contact extraction tab with page selection and queue button

### Phase 3: Background Service

- **Scheduler:** `src/services/contact_extraction_scheduler.py`
- **Registration:** Added to `src/schedulers.py`

### Phase 4: Curation Service

- **Service:** `src/services/contact_extraction_service.py`
- **Logic:** Extracts emails using regex pattern, creates contact records

### Phase 5: Testing

- **Tests:** Unit tests for email extraction, integration tests for workflow

## Additional Resources

- [Standard Curation Workflow Blueprint](../Docs_7_Workflow_Canon/BP-01-Standard_Curation_Workflow.md)
- [Curation Workflow Cookbook](<../Docs_6_Architecture_and_Status/0.5_Curation%20Workflow%20Cookbook%20(Developer%20On%E2%80%91Ramping%20Guide).md>)
- [Architecture Flow and Components](../Docs_6_Architecture_and_Status/0.1_ScraperSky_Architecture_Flow_and_Components.md)
- [Background Service Pattern and Router Crosswalk](../Docs_6_Architecture_and_Status/BACKGROUND_SERVICE_PATTERN_AND_ROUTER_CROSSWALK.md)
- [Core Architectural Principles](../Docs_1_AI_GUIDES/17-CORE_ARCHITECTURAL_PRINCIPLES.md)
