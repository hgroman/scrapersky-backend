# ScraperSky Naming & Structural Conventions Guide

**Date:** YYYY-MM-DD (To be updated on creation/modification)
**Version:** 1.0

**Objective:** This document serves as the definitive guide for all naming and structural conventions within the ScraperSky backend project. It is synthesized from existing project documentation, code examples, and canonical workflow definitions. Adherence to these conventions is crucial for maintaining consistency, readability, and maintainability across the codebase.

---

## Core Principle

Consistency is paramount. Most names are derived from a `workflow_name` (snake_case) and/or a `source_table_name` (singular, snake_case). This guide explicitly details these derivations.

---

## 1. Base Identifiers

These are the foundational names from which many others are derived. Every new workflow should clearly define these upfront, **ideally during the planning phase and documented in the workflow's canonical YAML or initial planning documents (e.g., in `/Docs/Docs_4_Planning/`).**

- **`workflow_name`**

  - **Format:** `snake_case` (e.g., `page_curation`, `single_search`, `domain_curation`).
  - **Derivation & Authority:** Defined by the core purpose of the workflow. **While there isn't a formal, documented approval step specifically for `workflow_name` in cheat sheets or YAML files, new workflow names are typically reviewed informally during planning meetings or pull request reviews by senior developers. This review ensures clarity, consistency with existing workflows (e.g., the recommended patterns `{entity}_curation` or `{entity}_import`), and helps prevent conflicts. The name should be descriptive of the workflow's primary function.**
    - **Example of derivation (`workflow_name = sitemap_import`):** Core purpose: Importing URLs from sitemap files. Direct derivation: "sitemap" (data source) + "import" (action).
  - **Prohibited Patterns/Keywords:** **Avoid names that are SQL reserved words or could cause conflicts with existing system components. Adherence to common patterns like `{entity}_curation` or `{entity}_import` is strongly recommended for consistency and clarity.**
  - **Example:** For a workflow curating pages, `workflow_name` is `page_curation`.

- **`{WorkflowNameTitleCase}`**

  - **Format:** The `workflow_name` converted to `TitleCase` (first letter of each word capitalized, no spaces).
  - **Derivation:** From `workflow_name`.
  - **Example:** If `workflow_name` is `page_curation`, then `{WorkflowNameTitleCase}` is `PageCuration`.

- **`{workflowNameCamelCase}`**

  - **Format:** The `workflow_name` converted to `camelCase` (first letter of first word lowercase, subsequent words capitalized, no spaces).
  - **Derivation:** From `workflow_name`.
  - **Example:** If `workflow_name` is `page_curation`, then `{workflowNameCamelCase}` is `pageCuration`.

- **`source_table_name`**

  - **Format:** Singular, `snake_case`. Represents the primary database table the workflow interacts with or is centered around.
  - **Derivation & Authority:** Determined by the primary data entity of the workflow. **If a new table is required, its name is decided during the preliminary database design phase, which occurs before formal workflow implementation begins. The SQLAlchemy model file (e.g., `src/models/new_entity.py`) is typically created and committed before the workflow implementation, effectively solidifying this name.**
    - **Example (`source_table_name = sitemap_file` for the `sitemap_import` workflow):** This `source_table_name` directly corresponds to the model file `src/models/sitemap_file.py` and the SQLAlchemy model class `SitemapFile`.
  - **Prohibited Patterns/Keywords:** **Avoid names that are SQL reserved words. Always check existing database table names to prevent conflicts.**
  - **Example:** `page`, `domain`, `place`, `sitemap_file`, `local_business`.

- **`{SourceTableTitleCase}`**

  - **Format:** The `source_table_name` converted to `TitleCase`.
  - **Derivation:** From `source_table_name`.
  - **Example:** If `source_table_name` is `page`, then `{SourceTableTitleCase}` is `Page`.

- **`source_table_plural_name`**
  - **Format:** Plural, `snake_case`.
  - **Derivation:** From `source_table_name`. Standard English pluralization rules apply (e.g., `page` → `pages`, `sitemap_file` → `sitemap_files`). **Crucially, ensure consistency with the actual database table names (e.g., if the database table is named `sitemaps`, then `source_table_plural_name` for the `sitemap` entity should be `sitemaps`).**
  - **Example (`source_table_name = page`):** `pages`.
  - **Example (`source_table_name = sitemap_file`):** `sitemap_files`.

---

## Layer 1: Python Backend - Models & ENUMs

- **File Names:**

  - **Convention:** `source_table_name.py` (singular, snake_case).
  - **Derivation:** Based on the primary data entity.
  - **Example (`source_table_name = page`):** `page.py`.

- **SQLAlchemy Model Class Names:**

  - **Convention:** `{SourceTableTitleCase}`.
  - **Derivation:** From `source_table_name`.
  - **Example (`source_table_name = page`):** `Page`.

- **Status Enum Python Class Names (e.g., CurationStatus, ProcessingStatus):**

  - **Strict Convention:** Python Enum classes for workflow-specific statuses **MUST** always be named using the `{WorkflowNameTitleCase}` prefix.
    - **Format:** `{WorkflowNameTitleCase}CurationStatus`, `{WorkflowNameTitleCase}ProcessingStatus`.
    - **Base Class:** These enums should inherit from `(str, Enum)`.
  - **Rationale:** This ensures clear association with the specific workflow and maintains universal consistency. Using `{SourceTableTitleCase}` as a prefix for these workflow-specific enums is incorrect.
  - **Example (for `workflow_name = page_curation`):** `PageCurationStatus`, `PageProcessingStatus` (defined in `src/models/page.py`).
  - **Technical Debt:** Existing deviations (e.g., `SitemapImportCurationStatusEnum` in `sitemap.py` using an "Enum" suffix and a different base class, or `SitemapCurationStatusEnum` in `domain.py` using a source table prefix) are considered technical debt and should be refactored.
  - **Standard Values (Mandatory for New Workflows):**
    - `{WorkflowNameTitleCase}CurationStatus`: Members **MUST** be `New = "New"`, `Queued = "Queued"`, `Processing = "Processing"`, `Complete = "Complete"`, `Error = "Error"`, `Skipped = "Skipped"`. No custom additions to this primary curation enum are permitted.
    - `{WorkflowNameTitleCase}ProcessingStatus`: Members **MUST** be `Queued = "Queued"`, `Processing = "Processing"`, `Complete = "Complete"`, `Error = "Error"`.

- **SQLAlchemy Column Names (Primary Status Fields on Model):**

  - **Curation Status Column:**
    - **Name:** `{workflow_name}_curation_status`.
    - **Example (`workflow_name = page_curation`):** `page_curation_status`.
    - **Type Definition Example:** `Column(PgEnum(PageCurationStatus, name="pagecurationstatus", create_type=False), nullable=False, server_default=PageCurationStatus.New.value, index=True)`
  - **Processing Status Column:**
    - **Name:** `{workflow_name}_processing_status`.
    - **Example (`workflow_name = page_curation`):** `page_processing_status`.
    - **Type Definition Example:** `Column(PgEnum(PageProcessingStatus, name="pageprocessingstatus", create_type=False), nullable=True, index=True)`
  - **Processing Error Column:**
    - **Name:** `{workflow_name}_processing_error`.
    - **Example (`workflow_name = page_curation`):** `page_processing_error`.
    - **Type Definition Example:** `Column(Text, nullable=True)`

- **Handling Justified Non-Standard User States (Additional Status Fields):**
  - **Context:** In rare, highly justified cases where a workflow requires an additional user-selectable state not covered by the standard `{WorkflowNameTitleCase}CurationStatus` Enum values (e.g., "On Hold," "Pending External Review") and this state does _not_ directly trigger the primary processing queue.
  - **Strict Mandate:** Such additional states **MUST NOT** modify the standard `{WorkflowNameTitleCase}CurationStatus` or `{WorkflowNameTitleCase}ProcessingStatus` Enums or their primary columns.
  - **Solution:** The additional state **MUST** be managed by:
    1.  A **new, separate status field** on the SQLAlchemy model.
    2.  A **new, dedicated Python Enum class** for this specific status purpose.
  - **Naming Convention for Additional Status Field:**
    - **Column Name:** `{workflow_name}_{status_purpose}_status` (e.g., `page_curation_review_status`).
    - **Python Enum Class Name:** `{WorkflowNameTitleCase}{StatusPurpose}Status` (e.g., `PageCurationReviewStatus`). This Enum defines the values for the additional status.
  - **Database ENUM Type:** A corresponding new PostgreSQL ENUM type would need to be manually created (e.g., `pagecurationreviewstatus`).
  - **Integration:** The update logic for this additional status is managed independently of the primary dual-status (curation/processing) flow unless explicitly designed to interact in a controlled manner.
  - **Discouragement & Justification:** Adding such fields is **strongly discouraged** to maintain simplicity. Implementation requires:
    - Significant justification for its necessity.
    - Formal review and approval.
    - Clear documentation of its purpose, values, and interaction logic in the workflow's canonical YAML and the `CONVENTIONS_AND_PATTERNS_GUIDE.md` itself if it becomes a recurring pattern.

---

## Layer 2: Python Backend - Schemas

Pydantic schemas are used to define the structure of API request and response bodies, ensuring data validation and clear contracts.

- **File Names:**

  - **Primary Convention (Mandatory for New Workflows):** For Pydantic schemas related to specific workflow actions (e.g., batch status updates, workflow-specific request/response models), the file **MUST** be named `src/schemas/{workflow_name}.py`.
    - **Rationale:** This aligns with clear separation of concerns and emphasizes the workflow-specific nature of these operations.
    - **Example (`workflow_name = page_curation`):** `src/schemas/page_curation.py` (contains `PageCurationUpdateRequest`, `PageCurationUpdateResponse`).
  - **Secondary Convention (for Generic Entity Schemas):** If schemas are genuinely generic, intended for reuse by _other distinct workflows_, or define core CRUD operations for an entity (unrelated to a specific workflow's actions), they should be placed in `src/schemas/{source_table_name}.py`.
    - **Example (`source_table_name = sitemap_file`):** `src/schemas/sitemap_file.py` (contains generic `SitemapFileBase`, `SitemapFileCreate`, `SitemapFileRead`).
    - **Note:** Workflow-specific schemas (like batch updates) should _not_ reside in these entity-based files, even if they operate on that entity.

- **Request & Response Model Naming (for Workflow-Specific Actions):**
  - **Strict Naming Convention (Mandatory for New Workflows):**
    - **Prefix:** Models **MUST** use the `{WorkflowNameTitleCase}` prefix. This ensures clarity and consistency with Python Enum naming (Section 4). Using `{SourceTableTitleCase}` for workflow-specific action schemas is generally incorrect unless the schema is truly generic and resides in a `{source_table_name}.py` file (see above).
    - **Suffixes:** Request models **MUST** end with "Request". Response models **MUST** end with "Response".
    - **Core Structure:**
      - Request: `{WorkflowNameTitleCase}[ActionDescription][Batch]Request`
      - Response: `{WorkflowNameTitleCase}[ActionDescription][Batch]Response`
    - **Specific Example (Batch Status Update):**
      - Request: `{WorkflowNameTitleCase}BatchStatusUpdateRequest`
        - **Example (`workflow_name = page_curation`):** `PageCurationBatchStatusUpdateRequest`.
      - Response: `{WorkflowNameTitleCase}BatchStatusUpdateResponse`
        - **Example (`workflow_name = page_curation`):** `PageCurationBatchStatusUpdateResponse`.
    - **Example (Single Item Update/Create - if needed specifically for a workflow beyond generic CRUD):**
      - Request: `{WorkflowNameTitleCase}StatusUpdateRequest`, `{WorkflowNameTitleCase}CreateRequest`
      - Response: `{WorkflowNameTitleCase}StatusUpdateResponse`, `{WorkflowNameTitleCase}CreateResponse`
  - **Example (from `src/schemas/page_curation.py`):**
    - `PageCurationUpdateRequest`
    - `PageCurationUpdateResponse`
  - **Technical Debt:** Existing schemas like `SitemapFileBatchUpdate` (in `sitemap_file.py`) that do not use the `{WorkflowNameTitleCase}` prefix for a workflow-specific action or omit the "Request"/"Response" suffix are considered technical debt. It should ideally be in a `sitemap_import.py` schema file and named `SitemapImportBatchUpdateRequest`.

---

## Layer 3: Python Backend - Routers

Routers define the API endpoints, linking HTTP methods and paths to specific handler functions.

- **File Names:**

  - **Primary Convention (Mandatory for New Workflows):** For new routers primarily handling workflow-specific operations (e.g., batch status updates for a particular workflow), the file **MUST** be named `src/routers/{workflow_name}.py`.
    - **Rationale:** Ensures clear separation of concerns and maintainability.
    - **Example (`workflow_name = page_curation`):** `src/routers/page_curation.py`.
  - **Secondary Convention (Adding to Existing Entity-Based Routers):** A workflow-specific endpoint may be added to an existing `src/routers/{source_table_plural_name}.py` file **only if ALL** of the following conditions are met:
    1.  The file already exists and is actively maintained for that entity.
    2.  The new endpoint is a minor addition, closely related to the entity's general management.
    3.  The workflow is very tightly coupled to this single entity and doesn't involve complex inter-entity logic within this endpoint.
    4.  Creating a separate `{workflow_name}.py` file would result in a trivially small file (e.g., only one very simple endpoint).
    - **Example (`source_table_plural_name = sitemap_files`):** `src/routers/sitemap_files.py` (currently handles general CRUD for sitemap files and some workflow-specific operations, though new workflow-specific logic should ideally go into its own file).

- **Router Variable Name (declared within the file):**

  - **Convention:** `router = APIRouter()`.
  - **Example (`router file = page_curation.py`):** `page_curation_router`.

- **API Endpoint Path Construction (for batch status updates):**

  - **Base Path:** All API v3 endpoints are prefixed with `/api/v3/`. This is typically applied at the application level (in `main.py`) or when including the main API router.
  - **Router-Level Prefix:** Routers themselves are often grouped by the primary entity they operate on. This prefix is defined when the specific router (e.g., `page_curation_router` or `pages_router`) is included in a parent router or the main application.
    - **Convention:** `/{source_table_plural_name}` (e.g., `/pages`, `/domains`).
  - **Endpoint-Specific Path (Strict Rules for New Workflows):** This is the path defined on the `@router.put(...)` decorator.
    - **If router file is `src/routers/{workflow_name}.py` (workflow-specific):**
      - **Path:** `/status` (or other direct action like `/submit`, `/analyze`).
      - **Rationale:** The workflow context is already defined by the router file and its inclusion prefix.
      - **Full Example (`workflow_name = page_curation`, `source_table_plural_name = pages`):**
        - Router file: `src/routers/page_curation.py`
        - Router included with prefix `/pages` (e.g., `app.include_router(page_curation_router, prefix="/pages")`)
        - Endpoint decorator: `@router.put("/status")`
        - Resulting Full Path: `PUT /api/v3/pages/status`
    - **If router file is `src/routers/{source_table_plural_name}.py` (entity-specific):**
      - **Path:** `/{workflow_name}/status` (or other workflow-specific action).
      - **Rationale:** The workflow context needs to be specified in the path to differentiate actions for this entity that belong to different workflows.
      - **Full Example (`workflow_name = page_curation`, `source_table_plural_name = pages`):**
        - Router file: `src/routers/pages.py`
        - Router included with prefix (if any, often none if it's a primary entity router included directly)
        - Endpoint decorator: `@router.put("/page_curation/status")` (assuming router prefix for `/pages` is handled during its inclusion or this router handles multiple entities)
        - Resulting Full Path: `PUT /api/v3/pages/page_curation/status` (if `pages.py` router is mounted at `/pages`).
  - **Technical Debt:** Existing endpoint paths that do not strictly follow this logic (e.g., `src/routers/page_curation.py` using `/pages/curation-status` or `src/routers/sitemap_files.py` using `/status` for a workflow action) should be noted as deviations and potential candidates for refactoring to align with these stricter conventions.

- **Endpoint Function Names (for batch status updates):**
  - **Default (Most Explicit):** `update_{source_table_name}_{workflow_name}_status_batch`.
  - **Strict Shortening Rules (Mandatory for New Workflows):**
    - **In `src/routers/{workflow_name}.py` (Workflow-Specific Router):** Omit the `_{workflow_name}_` part from the default.
      - **Convention:** `update_{source_table_name}_status_batch`.
      - **Example (`workflow_name = page_curation`, `source_table_name = page` in `src/routers/page_curation.py`):** `update_page_status_batch`.
    - **In `src/routers/{source_table_plural_name}.py` (Entity-Specific Router):** Omit the `_{source_table_name}_` part from the default.
      - **Convention:** `update_{workflow_name}_status_batch`.
      - **Example (`workflow_name = page_curation`, `source_table_name = page` in `src/routers/pages.py`):** `update_page_curation_status_batch`.
  - **Rationale for Shortening:** Avoids redundancy with the context provided by the router's file name and purpose, while maintaining clarity.
  - **Technical Debt:** Existing function names that don't align with this default or the strict shortening rules (e.g., `update_page_curation_status_batch` found in `src/routers/page_curation.py`, which should be `update_page_status_batch` by the strict rule) are considered deviations.

---

## Layer 4: Python Backend - Services

Services encapsulate the business logic for workflows, including schedulers for background tasks and the core processing logic.

- **Scheduler File Names & Structure:**

  - **Strict Convention (Absolute Rule):** For _any_ new workflow that includes a background processing component initiated by a scheduler (e.g., polling for a `_processing_status` of `Queued`), a new, dedicated scheduler file **MUST** be created in `src/services/` and named `{workflow_name}_scheduler.py`.
    - **Rationale:** This ensures clear separation of concerns, allows for independent deployment/scaling of workflows, provides centralized error handling per workflow, and simplifies maintenance. Sharing scheduler files is strongly discouraged and would create technical debt.
    - **Examples:** `src/services/sitemap_import_scheduler.py`, `src/services/domain_scheduler.py`.
    - **Deviation Protocol:** Exceptions are extremely discouraged. Any consideration requires written justification, technical lead approval, explicit code comments, and documentation in canonical YAMLs and the technical debt register.
  - **Standard Helper:** Schedulers typically utilize the `run_job_loop` helper function (from `src/common/curation_sdk/scheduler_loop.py`) for the standard polling pattern.

- **Processing Service File Names:**

  - **Strict Convention:** Core processing logic for a workflow **MUST** reside in a dedicated service file named `src/services/{workflow_name}_service.py`.
  - **Derivation:** From `workflow_name`.
  - **Example (`workflow_name = page_curation`):** `src/services/page_curation_service.py`.

- **Scheduler Job Function Names (main polling function within `{workflow_name}_scheduler.py`):**

  - **Strong Guideline (Default):** `async def process_{workflow_name}_queue():`
  - **Alternative (Less Preferred for New Work):** An existing pattern is `async def process_pending_{entity_plural}():` (e.g., `process_pending_sitemap_imports()`).
  - **Rules for Deviation:** If deviating from the default for significant clarity:
    1.  MUST start with `process_`.
    2.  MUST include the entity being processed.
    3.  MUST clearly describe the action.
    4.  SHOULD end with a collective noun or plural form.
    5.  MUST have a docstring explaining its purpose and any deviation from the standard name.
  - **Example (`workflow_name = page_curation`):** Default is `async def process_page_curation_queue():`.

- **Processing Service Function Names (within `{workflow_name}_service.py` for processing a single item):**

  - **Strict Convention (Mandatory):** `async def process_single_{source_table_name}_for_{workflow_name}(session: AsyncSession, record_id: UUID) -> None:`
  - **Rationale:** Provides maximum clarity on the action (processing a single item), the entity involved (`source_table_name`), and the specific workflow context (`for_{workflow_name}`).
  - **Example (`workflow_name = page_curation`, `source_table_name = page`):** `async def process_single_page_for_page_curation(...)`.
  - **Technical Debt:** Existing deviations are considered technical debt:
    - E.g., `process_single_sitemap_file` in `sitemap_import_service.py` (missing `_for_sitemap_import`).
    - Workflows handling batch processing directly in the scheduler instead of delegating single item processing to a service function with this naming convention.
    - Workflows lacking a dedicated processing service file and function.

- **Scheduler Registration & Settings Pattern (Mandatory for New Workflows):**
  - **Setup Function:** Each `src/services/{workflow_name}_scheduler.py` file **MUST** implement a setup function: `def setup_{workflow_name}_scheduler() -> None:`. This function is responsible for adding the workflow's job(s) to the shared APScheduler instance.
    - **Example (`workflow_name = page_curation`):** `def setup_page_curation_scheduler() -> None:`
  - **Registration in `main.py`:** The `setup_{workflow_name}_scheduler()` function **MUST** be imported into `src/main.py` and called within the `lifespan` context manager to register the job(s) upon application startup.
  - **Settings Import:** Configuration values within service/scheduler files **MUST** be accessed by importing the `settings` instance: `from ..config.settings import settings` (then `settings.YOUR_SETTING`).
  - **Job Configuration Settings Variables:** Parameters for scheduler jobs (e.g., interval, batch size) **MUST** be defined in `src/config/settings.py` and `.env.example` using the convention: `{WORKFLOW_NAME_UPPERCASE}_SCHEDULER_{PARAMETER_NAME}`.
    - **Examples:** `PAGE_CURATION_SCHEDULER_INTERVAL_MINUTES`, `PAGE_CURATION_SCHEDULER_BATCH_SIZE`.

---

## Layer 5: Python Backend - Configuration

Proper configuration management is essential for application stability, security, and adaptability across different environments.

- **Environment Variable Naming:**

  - **Strict Convention (for New Workflow-Specific Settings):** All new environment variables specific to a ScraperSky workflow **MUST** use the `SCS_` prefix, followed by the `WORKFLOW_NAME_UPPERCASE`, and then a descriptive `SETTING_NAME`.
    - **Format:** `SCS_{WORKFLOW_NAME_UPPERCASE}_{SETTING_NAME}`
    - **Example (`workflow_name = page_curation`, setting for batch size):** `SCS_PAGE_CURATION_BATCH_SIZE`
    - **Rationale:** Provides a clear namespace for all ScraperSky variables, prevents collisions, and improves discoverability.
  - **Existing/Legacy Patterns (to be aware of, for refactoring):**
    - Scheduler settings currently often follow `{WORKFLOW_NAME_UPPERCASE}_SCHEDULER_{PARAMETER}` (e.g., `DOMAIN_SCHEDULER_INTERVAL_MINUTES`). While functional, new settings should adopt the `SCS_` prefix.
  - **General Rules:**
    - Always use `UPPERCASE_WITH_UNDERSCORES`.
    - Ensure names are descriptive enough to avoid ambiguity, especially if not using the `SCS_` prefix for legacy variables.

- **Defining and Loading Settings:**

  - **`.env` and `.env.example`:** All environment variables MUST be defined in `.env` for local development (and managed appropriately for deployed environments) and **MUST** have a corresponding entry (with a default or placeholder value) in `.env.example`.
  - **Pydantic Settings (`src/config/settings.py`):** Environment variables are loaded into the application using Pydantic's `BaseSettings` class in `src/config/settings.py`.

    - Each configurable variable must be defined as an attribute on the `Settings` class with its type hint.
    - **Example (in `src/config/settings.py`):**

      ```python
      class Settings(BaseSettings):
          # ... other settings ...
          SCS_PAGE_CURATION_BATCH_SIZE: int = Field(default=10, description="Batch size for page curation processing.")
          # Legacy example:
          DOMAIN_SCHEDULER_INTERVAL_MINUTES: int = 1

          model_config = SettingsConfigDict(
              env_file=".env", case_sensitive=False, extra="allow"
          )

      settings = Settings() # Singleton instance
      ```

  - **Accessing Settings in Code:** Settings **MUST** be accessed by importing the singleton `settings` instance from `src/config/settings.py`.
    - **Correct Usage:**
      ```python
      from src.config.settings import settings
      # ...
      batch_size = settings.SCS_PAGE_CURATION_BATCH_SIZE
      ```
    - **Incorrect Usage:** Do not import the `Settings` class directly for accessing values.

- **Workflow-Specific Initializations (at Application Startup):**
  - **Location:** Workflow-specific initializations that need to occur at application startup (beyond router inclusion or basic scheduler job registration covered in Section 8) are managed via setup functions called from the FastAPI `lifespan` context manager in `src/main.py`.
  - **Pattern:**
    1.  Define a dedicated setup function within the relevant workflow module (e.g., in its `_scheduler.py` or `_service.py` file if it's closely related to service initialization).
    2.  Import this setup function into `src/main.py`.
    3.  Call the setup function within the `async def lifespan(app: FastAPI):` context manager.
  - **Example Usage:** This pattern is primarily used for registering scheduler jobs (see Section 8). If a workflow requires initializing a unique client, setting specific Sentry tags at startup, or other one-time setup routines, this is the place to integrate it. Ensure any such custom initialization is clearly documented.
  - **Refer to Section 8:** The detailed pattern for scheduler job registration (`setup_{workflow_name}_scheduler()`) provides the primary example of this startup integration.

---

## Layer 6: UI - Components

User interface component identifiers are primarily derived from `{workflowNameCamelCase}` to ensure uniqueness and predictability. **All new workflows MUST adhere strictly to these naming conventions to ensure consistency and proper functioning of associated JavaScript.**

- **Tab Button Text & Panel Header:**

  - **Convention (Tab Button):** Generally, the direct Title Case of `workflow_name` with spaces (e.g., "Page Curation" from `page_curation`).
  - **Convention (Panel Header):** If further clarity or disambiguation is needed (e.g., multiple workflows on the same entity), the panel header (`<h3>` or `<h4>`) can use a more descriptive text.
  - **Derivation:** Convert `workflow_name` to Title Case and replace underscores with spaces for the base tab button text.
  - **Example (`workflow_name = domain_curation`):**
    - Tab Button Text: "Domain Curation"
    - Panel Header Text (for clarity): "Domain Curation for Sitemap Analysis"
  - **Guideline:** The guiding principle for modifications in the panel header is function disambiguation. The tab button itself should aim for brevity.

- **Tab `data-panel` Attribute:**

  - **Convention:** `{workflowNameCamelCase}Panel`
  - **Derivation:** Convert `workflow_name` to `camelCase` and append "Panel".
  - **Strict Requirement:** **For all new workflows, adherence to this convention is mandatory.**
  - **Example (`workflow_name = page_curation`):** `pageCurationPanel`
  - **Reference:** The `domainCurationPanel` implementation (e.g., `static/scraper-sky-mvp.html` line 577 for tab, line 809 for panel) serves as a definitive example.

- **Panel `div` `id`:**

  - **Convention:** Must match the `data-panel` attribute: `{workflowNameCamelCase}Panel`.
  - **Derivation:** Same as Tab `data-panel` attribute.
  - **Strict Requirement:** **For all new workflows, adherence to this convention is mandatory.**
  - **Example (`workflow_name = page_curation`):** `pageCurationPanel`

- **Filter and Action Control IDs (General Pattern):**

  - **Mandatory Adherence:** The following ID patterns are **exact and mandatory** for all new workflows. The `domainCurationPanel` section in `static/scraper-sky-mvp.html` serves as the reference model.
  - Let `PanelBaseName = {workflowNameCamelCase}` (e.g., `pageCuration` from `page_curation`).
  - Let `PanelTitleCase = {WorkflowNameTitleCase}` (e.g., `PageCuration` from `page_curation`).
  - **Status Filter `select` `id`:** `{PanelBaseName}StatusFilter` (e.g., `pageCurationStatusFilter`)
  - **Name/Identifier Filter `input` `id`:** `{PanelBaseName}NameFilter` (e.g., `pageCurationNameFilter`). **Note:** The "Name" part can be adapted to the specific field being filtered (e.g., `domainCurationDomainFilter`, `sitemapUrlFilter`).
  - **Apply Filters Button `id`:** `apply{PanelTitleCase}FiltersBtn` (e.g., `applyPageCurationFiltersBtn`)
  - **Reset Filters Button `id`:** `reset{PanelTitleCase}FiltersBtn` (e.g., `resetPageCurationFiltersBtn`)

- **Data Table & Body (General Pattern):**

  - Let `PanelBaseName = {workflowNameCamelCase}`.
  - **Table `id`:** `{PanelBaseName}Table` (e.g., `pageCurationTable`)
  - **Table Body `tbody` `id`:** `{PanelBaseName}TableBody` (e.g., `pageCurationTableBody`)

- **Select All Checkbox `id` (General Pattern):**

  - Let `PanelBaseName = {workflowNameCamelCase}`.
  - **Convention:** `selectAll{PanelTitleCase}Checkbox` (e.g., `selectAllPageCurationCheckbox`)

- **Batch Update Controls (General Pattern):**

  - **Mandatory Adherence:** The following ID patterns are **exact and mandatory.**
  - Let `PanelBaseName = {workflowNameCamelCase}`.
  - Let `PanelTitleCase = {WorkflowNameTitleCase}`.
  - **Batch Controls `div` `id`:** `{PanelBaseName}BatchUpdateControls` (e.g., `pageCurationBatchUpdateControls`)
  - **Batch Status `select` `id`:** `{PanelBaseName}BatchStatusUpdate` (e.g., `pageCurationBatchStatusUpdate`)
  - **Apply Batch Update Button `id`:** `apply{PanelTitleCase}BatchUpdateBtn` (e.g., `applyPageCurationBatchUpdateBtn`)
  - **Clear Selection Button `id`:** `clear{PanelTitleCase}SelectionBtn` (e.g., `clearPageCurationSelectionBtn`)

- **Batch Status Dropdown Options (UI Text vs. Backend Value):**
  - **Context:** This defines how UI dropdown options for status updates relate to backend Enum values, particularly for triggering the dual-status update (CurationStatus -> ProcessingStatus).
  - **Standard for New Workflows (Using Standard Enums like `PageCurationStatus`):**
    - **UI Text:** The dropdown option text **MUST** use the actual backend Enum member value, with optional descriptive text in parentheses for clarity if the action is non-obvious.
      - **Format:** `"{EnumValueTitleCase} (Queue for {ProcessDescription})"` or `"{EnumValueTitleCase} (Start {ProcessDescription})"`.
      - **Example (Triggering processing):** If `PageCurationStatus.Queued` triggers processing, the UI option should be: `<option value="Queued">Queued (Start Processing)</option>` or `<option value="Queued">Queued (Queue for Page Processing)</option>`.
    - **JavaScript Behavior:** The JavaScript associated with this tab **MUST** send the exact `value` selected in the dropdown (e.g., "Queued") to the API endpoint. **No client-side translation of UI text to a different backend Enum value is permitted for new standard workflows.**
    - **API Behavior:** The API endpoint will receive this exact Enum string (e.g., "Queued") and use it to update the `curation_status` field. The dual-status update logic (setting `processing_status` to `Queued`) is triggered within the API based on this received `curation_status` value.
  - **Rationale:** This ensures type safety with Pydantic validation at the API level and maintains a clear, direct link between the UI selection and the backend Enum value, simplifying the dual-status update mechanism.
  - **Legacy Note:** Older workflows might exhibit different patterns (e.g., UI "Selected" mapping to a backend "Selected" status which then triggers queuing). These are considered technical debt if they don't align with the standard Enum values (`New, Queued, Processing, Complete, Error, Skipped`). New workflows MUST use "Queued" as the primary CurationStatus value to trigger the processing queue.

---

## Layer 7: Testing

Robust testing is crucial for ensuring workflow reliability and maintainability. A combination of component-focused tests and workflow integration tests should be implemented.

- **General Test Structure:**

  - Tests are primarily organized by component type within the `tests/` directory (e.g., `tests/services/`, `tests/scheduler/`, `tests/routers/`, `tests/workflows/`).
  - Test files are generally named `test_{module_or_feature_being_tested}.py`.

- **Unit/Component Test Focus & Priority:**

  - **High Priority (MUST have coverage):**
    - **Service Logic (`tests/services/test_{workflow_name}_service.py`):**
      - Primary processing function (e.g., `process_single_{source_table_name}_for_{workflow_name}`).
      - Correct status transitions (e.g., New -> Queued -> Processing -> Complete/Error).
      - Error handling paths and exception management.
    - **Scheduler Logic (`tests/scheduler/test_{workflow_name}_scheduler.py`):**
      - Correct registration with the shared APScheduler instance via its `setup_{workflow_name}_scheduler()` function.
      - Verification that the main scheduler job function (e.g., `process_{workflow_name}_queue()`) correctly calls helper functions (like `run_job_loop`) or service functions with appropriate arguments. Mocking is often used here.
      - Example: `tests/scheduler/test_process_pending_deep_scrapes.py`.
  - **Medium Priority (SHOULD have coverage):**
    - **Routers (`tests/routers/test_{workflow_name}_router.py` or `test_{entity}_routers.py`):**
      - Critical API endpoints, especially status update endpoints.
      - Basic validation of request/response schemas.
    - **Schema Validation:** For complex Pydantic schemas, dedicated tests for validation logic if not covered by router tests.
  - **Lower Priority (Covered as resources allow, or indirectly):**
    - Models (often indirectly tested via service and router tests).
    - Simpler schemas.
    - Utility functions (if not covered by tests of their primary consumers).
  - **Example of Service Test (`tests/services/test_sitemap_deep_scrape_service.py`):** Demonstrates testing individual functions within a service.

- **Workflow Integration Tests (Component Flow Tests):**

  - **Location:** Typically in a dedicated workflow test file, e.g., `tests/workflows/test_{workflow_name}_workflow.py`.
  - **Scope (Mandatory):** For a new workflow, the integration test **MUST** cover the end-to-end flow:
    1.  **Setup:** Create necessary prerequisite data (e.g., source records in the initial state) using fixtures.
    2.  **API Call:** Trigger the workflow by calling the relevant API endpoint (e.g., the Curation Status Update endpoint) using an async test client.
    3.  **Database Verification (Initial):** Assert that the `curation_status` is updated correctly in the database and `processing_status` is set to `Queued` (dual-status update).
    4.  **Scheduler/Processing Execution:**
        - **Option A (Direct Call):** Directly invoke the scheduler's main job function (e.g., `await process_{workflow_name}_queue()`). This provides more thorough testing.
        - **Option B (Mocking):** Mock the single-item processing service function (e.g., `process_single_{source_table_name}_for_{workflow_name}`) to verify it's called correctly by the scheduler. Useful for isolating scheduler logic or avoiding complex dependencies of the service.
    5.  **Database Verification (Final):** Assert that the `processing_status` transitions to `Complete` (or `Error` in failure scenario tests).
    6.  **Side-Effect Verification:** If the processing service has side-effects (e.g., creates new records in another table, calls external services that can be mocked), verify these outcomes.
  - **Example Reference:** While no single existing test may cover all points perfectly, elements of this can be seen in scheduler tests that mock service calls. New workflow integration tests should aim for this comprehensive scope.

- **Test Data Management & Fixtures (`tests/conftest.py` and local fixtures):**

  - **Shared Fixtures (`tests/conftest.py`):**
    - **Database Session:** A fixture providing a test database session with automatic transaction rollback (e.g., `db_session`).
    - **API Client:** An async HTTP client for making API calls (e.g., `async_client`).
    - **Generic Model Creation Utilities/Fixtures:** Reusable fixtures for creating common base entities (e.g., a `test_domain` fixture).
  - **Workflow-Specific Fixtures (in `tests/workflows/test_{workflow_name}_workflow.py` or `tests/services/test_{workflow_name}_service.py`):**

    - Create fixtures to set up entities in specific states required for testing that particular workflow.
    - **Example (for `page_curation`):**

      ```python
      @pytest.fixture
      async def page_for_curation(db_session, test_domain):
          # Creates a Page record in 'New' status
          # ...
          return page

      @pytest.fixture
      async def queued_page_for_processing(db_session, test_domain):
          # Creates a Page record in 'Queued' status
          # ...
          return page
      ```

  - **Guidance:** Strive for a balance: make genuinely reusable fixtures global in `conftest.py`, and keep test-specific or workflow-specific setup close to the tests that use them.

---

This guide is intended to be a living document. As new patterns emerge or existing ones are refined, this document should be updated to reflect the current best practices for the ScraperSky project.
