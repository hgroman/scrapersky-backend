# Key Insights from Workflow Standardization Q&A

## Related Documentation

- **[1.0-ARCH-TRUTH-Definitive_Reference.md](./1.0-ARCH-TRUTH-Definitive_Reference.md)** - Definitive architectural reference
- **[2.0-ARCH-TRUTH-Implementation_Strategy.md](./2.0-ARCH-TRUTH-Implementation_Strategy.md)** - Implementation strategy for architectural alignment
- **[3.0-ARCH-TRUTH-Layer_Classification_Analysis.md](./3.0-ARCH-TRUTH-Layer_Classification_Analysis.md)** - Comprehensive analysis of layer classification
- **[CONVENTIONS_AND_PATTERNS_GUIDE.md](./CONVENTIONS_AND_PATTERNS_GUIDE.md)** - Detailed naming conventions and patterns

This document summarizes the most important findings and standards derived from the workflow standardization questions and follow-ups, providing a quick reference to the core patterns and requirements for ScraperSky workflows.

## Section 1: Base Identifiers

### Workflow Naming and Source Tables

- **Workflow Naming Derivation**: All `workflow_name` values are derived directly from the core purpose of the workflow (e.g., `domain_curation`, `sitemap_import`)

- **Source Table Alignment**: The `source_table_name` must match an existing SQLAlchemy model in `src/models/`. For new workflows requiring new tables, the database model must be created first

- **Recommended Naming Patterns**: For new workflows, the recommended pattern is `{entity}_curation` or `{entity}_import` where appropriate

- **Pluralization Consistency**: Table pluralization follows standard English rules and must be consistent across database tables, API endpoints, and router filenames

- **Tab Display Text**: Tab button text typically uses direct title-cased conversion of `workflow_name`, but descriptive modifications appear in panel headers for clarity, not in the tab buttons themselves

## Section 2: Layer 6: UI Components

### Panel and Element IDs

- **Tab/Panel ID Standard**: `{workflowNameCamelCase}Panel` is a strict requirement for both the `data-panel` attribute on the tab and the `id` attribute on the panel `div`

- **Element ID Conventions**: Element IDs must follow strict conventions like `{workflowNameCamelCase}StatusFilter` and `apply{WorkflowNameTitleCase}FiltersBtn` with absolutely no deviations

- **Domain Panel as Reference**: The Domain Curation panel implementation provides the standard reference model that all new workflows must precisely follow

### Status Dropdowns and API Integration

- **Descriptive Status Text**: Add descriptive context like "(Queue for Processing)" only when the status selection directly triggers a workflow action that may not be immediately obvious

- **Standard Format**: Use the format `"{EnumValueTitleCase} (Queue for {ProcessName})"` when adding explanatory text

- **Dropdown Values for New Workflows**: For new workflows using standard enums, the UI dropdown should use the actual enum values (e.g., "Queued") rather than non-standard terms like "Selected"

- **No JavaScript Translation**: Status values selected in the UI are sent directly to the API without translation - they must match what the API expects

## Section 3: Layer 6: JavaScript Files & Variables

### File and Variable Naming

- **JS Filename Standard**: JavaScript files strictly follow the `{workflow-name-kebab-case}-tab.js` pattern without exceptions

- **Variable Scoping Options**: Two approaches are used for scoping:

  - Full camelCase prefixes (`domainCurationStatusFilter`) for most variables and functions
  - Abbreviation suffixes (`getJwtTokenDC`) for frequently used utility functions

- **Long Name Handling**: For long workflow names, abbreviation-based scoping is documented with explicit code comments explaining the abbreviation chosen

### Creating New Workflow JavaScript

- **De Facto Template**: Though no official template exists, `domain-curation-tab.js` serves as the de facto standard for new implementations

- **Comprehensive Updates Required**: When cloning, all DOM selectors, state variables, function names, API endpoints, and comments must be thoroughly updated

- **Core Reusable Patterns**: Data loading, status filtering, batch selection, and pagination handling follow consistent patterns across workflows

- **Workflow-Specific Areas**: Data structure logic, workflow-specific triggers, and custom UI interactions require the most customization

### Layer 1: Python Backend - Models & ENUMs

- **Status Enum Naming Convention**: Status enums **must** follow the `{WorkflowNameTitleCase}CurationStatus` and `{WorkflowNameTitleCase}ProcessingStatus` pattern (e.g., `PageCurationStatus`) rather than the source table name

- **Standard Enum Values**:

  - Curation Status: `New, Queued, Processing, Complete, Error, Skipped`
  - Processing Status: `Queued, Processing, Complete, Error`

- **Enum Definition Style**: Standard enums should be defined using `str, Enum` base classes and without the "Enum" suffix in the class name

- **Legacy Inconsistencies**: Several enums (e.g., `SitemapCurationStatusEnum`, `SitemapImportCurationStatusEnum`) deviate from standard naming and values, classified as technical debt

- **Status Field Implementation**: Status fields should be implemented using SQLAlchemy Enum types with explicit non-null constraints and appropriate default values

### Layer 1: Python Backend - Database ENUM Types

- **PostgreSQL Type Naming**: Database enum type names follow the pattern `{workflow_name}curationstatus` and `{workflow_name}processingstatus` - direct concatenation without separators

- **Manual Type Creation**: Database enum types must be created via migrations before application code uses them; never auto-generated

- **SQLAlchemy Configuration**: All enum column definitions must use `create_type=False` in their `PgEnum` or `SQLAlchemyEnum` constructor

- **Workflow Name Preservation**: Multi-word workflow names (with underscores) are kept intact when forming enum type names (e.g., `sitemap_importcurationstatus`)

- **Reference Implementation**: See `page_curation_status` and `page_processing_status` in `src/models/page.py` for the standard pattern

### Layer 2: Python Backend - Schemas (Pydantic)

- **Schema File Location**: Use `src/schemas/{workflow_name}.py` for workflow-specific schemas and `src/schemas/{source_table_name}.py` only for genuinely generic, reusable schemas

- **Request/Response Naming**:

  - Always use `{WorkflowNameTitleCase}` prefix to clearly associate with a specific workflow
  - Request models must end with `Request` suffix (e.g., `PageCurationUpdateRequest`)
  - Response models must end with `Response` suffix (e.g., `PageCurationUpdateResponse`)
  - Include `Batch` in the name for operations that process multiple records

- **Schema Organization**:

  - Workflow-specific files should contain only schemas needed for that workflow's operations
  - Entity-based files should follow the Base/Create/Update/Read pattern for general CRUD operations

- **Reference Implementation**: See `src/schemas/page_curation.py` for the workflow-specific pattern and `src/schemas/sitemap_file.py` for the entity-based pattern

### Layer 3: Python Backend - Routers

- **Router File Location and Naming**:

  - Use `src/routers/{workflow}_CRUD.py` for routers that handle both entity CRUD operations and workflow-specific curation with dual-purpose updates
  - This naming pattern explicitly signals the router's dual role in handling both data access and workflow operations

- **Endpoint Path Construction**:

  - In `{workflow}_CRUD.py` routers: Use `@router.put("/status", ...)` for status update endpoints
  - For get/list operations, use standard RESTful patterns (`@router.get("/", ...)` or `@router.get("/{id}", ...)`)

- **Endpoint Function Naming**:

  - For status updates: `update_{workflow}_status_batch`
  - For CRUD operations: `create_{entity}`, `get_{entity}`, `list_{entity}`, `update_{entity}`, `delete_{entity}`

- **Implementation Pattern**:

  - These routers should implement the standard dual-status update pattern where selecting a curation status triggers updates to both the curation and processing status fields
  - The implementation should be consistent and cookie-cutter across workflows
  - Fields required for dual-purpose updates should be standardized

- **Transition Approach**:
  - New workflows should adopt this clear naming convention immediately
  - Existing routers with mixed responsibilities should be noted as technical debt to be addressed in future refactoring

### Layer 4: Python Backend - Services

- **Scheduler Organization**:

  - Each workflow MUST have its own dedicated `{workflow_name}_scheduler.py` file - no exceptions
  - Scheduler files handle polling for records with the appropriate status for processing
  - Separation provides clear boundaries, independent scaling, and isolated error handling

- **Scheduler Function Naming**:

  - Primary pattern: `process_{workflow_name}_queue()`
  - Always start with `process_`
  - Include the entity being processed
  - End with a collective noun or plural form
  - Include clear docstring explaining purpose

- **Processing Service Function Naming**:

  - Standard pattern: `process_single_{source_table_name}_for_{workflow_name}`
  - This pattern makes both the entity type and workflow context explicit
  - All functions must include proper type hints and docstrings
  - Use consistent parameter ordering (ID first, then session, then optional params)

- **Service Implementation**:

  - Each service class should be dedicated to a single workflow's processing needs
  - Processing logic must be separated from scheduling logic
  - Use standardized error handling and status updates

- **Scheduler Registration Pattern**:

  - Each workflow must implement a `setup_{workflow_name}_scheduler()` function
  - This function must be imported and called in FastAPI's `lifespan` event in `src/main.py`
  - The function must register with the shared APScheduler instance from `src/scheduler_instance.py`
  - Job parameters must be configured through settings variables: `{WORKFLOW_NAME}_SCHEDULER_BATCH_SIZE` and `{WORKFLOW_NAME}_INTERVAL_MINUTES`

- **Settings Import Pattern**:
  - MUST import the settings instance directly: `from ..config.settings import settings`
  - NEVER import the module: `from ..config import settings` (causes AttributeError)
  - Always access configuration via the settings instance: `settings.SOME_SETTING`

### Layer 4: Python Backend - Task Management

- **Task Definition Location**:

  - Default location for task functions is within `src/services/{workflow_name}_scheduler.py`
  - Each scheduler file contains its own task definition and scheduling logic
  - Only create separate task files when the task requires complex pre/post-processing or is called by multiple schedulers

- **Task Function Naming**:

  - Main processing function: `process_pending_{workflow_name}s()` (note the plural form)
  - Setup function: `setup_{workflow_name}_scheduler()`
  - Job ID: Similar to function name, typically `process_{workflow_name}s` or `process_pending_{workflow_name}s`

- **Task Registration Pattern**:

  - Each task must be registered with the shared APScheduler instance
  - Registration happens via the setup function called during application startup
  - Jobs must use consistent interval, batch size, and max instances parameters from settings
  - All registrations should be idempotent (remove existing jobs before registering)

- **Task Configuration**:
  - Each task must read configuration from the settings instance
  - Standard settings pattern: `{WORKFLOW_NAME}_SCHEDULER_INTERVAL_MINUTES`, `{WORKFLOW_NAME}_SCHEDULER_BATCH_SIZE`, and `{WORKFLOW_NAME}_SCHEDULER_MAX_INSTANCES`
  - All tasks should use the standardized `run_job_loop` helper when following the common pattern of processing items with a specific status

### Layer 5: Configuration and Environment Variables

- **Environment Variable Naming**:

  - Current pattern for workflow-specific settings: `{WORKFLOW_NAME}_SCHEDULER_{PARAMETER}`
  - Recommended stricter convention for new workflows: `SCS_{WORKFLOW_NAME}_{SETTING_NAME}`
  - Always use UPPERCASE for the entire variable name
  - Always include the workflow name as the prefix to prevent ambiguity
  - For scheduler settings specifically: `{WORKFLOW_NAME}_SCHEDULER_{PARAMETER}`

- **Configuration Loading**:

  - All environment variables must be defined in the `Settings` class in `src/config/settings.py`
  - New variables must be added to both `settings.py` and `.env.example` with documentation
  - Access settings via the `settings` instance, not the `Settings` class:
    ```python
    from ..config.settings import settings  # Correct
    batch_size = settings.WORKFLOW_SCHEDULER_BATCH_SIZE
    ```

- **Application Startup Configuration**:
  - Workflow-specific initialization must be defined in a setup function in the workflow's scheduler file
  - All setup functions must be called from the FastAPI `lifespan` context manager in `main.py`
  - Each workflow setup call should be wrapped in its own try/except block for isolation
  - This hybrid approach balances centralized startup with decentralized workflow-specific logic

### Layer 7: Testing

- **Test Organization**:

  - Test files are organized by component type (`tests/services/`, `tests/scheduler/`)
  - Component-based organization is preferred over strict unit/integration division
  - Each workflow should have dedicated test files for its key components

- **Incremental Testing Methodology** (from project's test methodology documentation):

  - **Component Isolation**: Break down the system into smallest testable units
  - **Progressive Testing Sequence**: Test in order of dependency
    1. **Foundation Testing**: Basic infrastructure components (DB connections)
    2. **Component Testing**: Individual functional units (services, models)
    3. **Integration Testing**: Component interactions (service + scheduler)
    4. **End-to-End Testing**: Complete workflows (API → DB → processing → final state)
  - **Diagnostic Logging**: Implement comprehensive logging in test scripts for:
    - Function entry/exit points
    - Database operations
    - Status changes
    - Error conditions
    - Performance metrics

- **Required Test Coverage**:

  - **High Priority (MUST have)**:
    - Service files (`tests/services/test_{workflow_name}_service.py`)
    - Scheduler files (`tests/scheduler/test_{workflow_name}_scheduler.py`)
  - **Medium Priority (SHOULD have)**:
    - Router files for critical API endpoints
    - Complex schema validation
  - **Lower Priority** (as resources allow):
    - Models and utility functions (typically covered indirectly)

- **Workflow Integration Tests**:

  - Should cover the complete workflow lifecycle with clearly defined success criteria:
    1. API endpoint testing (status update) → Verify response/status codes
    2. Database status verification (curation_status) → Verify field values
    3. Processing status checks (dual-status pattern) → Verify state transitions
    4. Scheduler execution (direct or mocked) → Verify call parameters
    5. Final state verification → Verify database state after processing
    6. Side effects verification → Verify related records created/updated
  - All steps should be included in a dedicated workflow test file

- **Test Fixtures**:

  - **Global fixtures** in `conftest.py`:
    - Database session fixture
    - Common utility fixtures
    - Shared model creation fixtures
  - **Workflow-specific fixtures** in test files:
    - Entity fixtures with specific workflow states
    - Mocked service responses
    - Test data specific to workflow requirements

- **Component-Specific Test Scripts** (based on project test plan):
  - **Database Connection Tests**: Verify basic connectivity and session management
  - **Entity Creation Tests**: Verify entity creation in expected states
  - **Processing Tests**: Verify background task execution and status transitions
  - **Status Monitoring Tests**: Verify status reporting and progress tracking
  - **End-to-End Tests**: Verify complete workflow with all components

---

This document will be updated as more sections of the workflow standardization Q&A are completed.
