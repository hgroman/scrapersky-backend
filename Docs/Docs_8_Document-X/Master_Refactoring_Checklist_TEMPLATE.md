# Master Refactoring Checklist TEMPLATE for: `{WorkflowName}`

**Workflow Being Refactored:** `_________________________` (e.g., WF1-SingleSearch)
**Canonical Workflow Name (for naming conventions):** `_________________________` (e.g., `single_search`)
**Date Initiated:** `_________________________`

---

## 0. Instructions & Pre-Checks

**How to Use This Template:**

1.  **Copy & Rename:** Make a copy of this template file (e.g., `WF1-SingleSearch_Refactor_Checklist.md`).
2.  **Fill in Header:** Update the `{WorkflowName}` in the title and the fields above. The "Canonical Workflow Name" is crucial for deriving correct file and variable names (e.g., if your workflow is "User Profile Update", the canonical name might be `user_profile_update`).
3.  **Consult Core Guides:** Keep `CONVENTIONS_AND_PATTERNS_GUIDE.md` and `Q&A_Key_Insights.md` handy for detailed explanations of standards. This checklist provides direct checks and summaries but those are your ultimate references.
4.  **Iterate per Component:** Go through each section below, assessing the current state of your workflow's components against the defined standards.
5.  **Document & Refactor:** Note deviations and plan refactoring steps. Mark items as complete `[x]` as you go.
6.  **Commit Systematically:** Make small, logical commits as you refactor parts of the workflow.

**Pre-Checks:**

- [ ] Review `Audit/WORKFLOW_AUDIT_JOURNAL.md` for any existing notes or technical debt identified for this specific workflow. Incorporate findings into the relevant sections below.
- [ ] Ensure a backup or version control branch is in place before starting major refactoring.

---

## 1. Layer 6: UI Components (HTML Templates / Jinja2)

**Relevant Files:**

- Identify main template file(s): `_________________________`
- Identify included partials/macros: `_________________________`

**Checklist:**
| Standard | Current File(s) & Line(s) | Conforms? (Y/N) | Notes / Refactor Plan | Done |
|-----------------------------------------------|---------------------------|-----------------|----------------------------------------|------|
| **HTML Element IDs** | | | | `[ ]`|
| - Format: `{workflow_name}-{page_section}-{element_type}-{identifier}` (e.g., `single_search-results-table-main`) | | | | `[ ]`|
| - See: `CONVENTIONS_AND_PATTERNS_GUIDE.md` (UI: HTML Element IDs) | | | | `[ ]`|
| **Jinja2 Templating** | | | | `[ ]`|
| - Use of `{{ ... }}` for variables, `{% ... %}` for statements. | | | | `[ ]`|
| - Consistent block naming (`{% block content %}`) | | | | `[ ]`|
| **Other UI Standards from Guide:** | | | | `[ ]`|
| - (Add specific checks based on guide) | | | | `[ ]`|

---

## 2. JavaScript (Frontend Logic)

**Relevant Files:**

- Identify main JS file(s): `src/static/js/{workflow_name}.js` or similar: `_________________________`
- Identify any other relevant JS/AJAX call locations: `_________________________`

**Checklist:**
| Standard | Current File(s) & Line(s) | Conforms? (Y/N) | Notes / Refactor Plan | Done |
|-----------------------------------------------|---------------------------|-----------------|----------------------------------------|------|
| **File Naming & Location** | | | | `[ ]`|
| - `src/static/js/{workflow_name}.js` (e.g., `single_search.js`) | | | | `[ ]`|
| - See: `CONVENTIONS_AND_PATTERNS_GUIDE.md` (JS: File Naming & Scoping) | | | | `[ ]`|
| **Variable Naming** | | | | `[ ]`|
| - `const {workflowName}{ElementName} = ...` (e.g., `const singleSearchSubmitButton = ...`) | | | | `[ ]`|
| - See: `CONVENTIONS_AND_PATTERNS_GUIDE.md` (JS: Variable Naming) | | | | `[ ]`|
| **Function Naming** | | | | `[ ]`|
| - `function handle{WorkflowName}{Action}()` (e.g., `function handleSingleSearchSubmit()`) | | | | `[ ]`|
| - See: `CONVENTIONS_AND_PATTERNS_GUIDE.md` (JS: Function Naming) | | | | `[ ]`|
| **AJAX Calls** | | | | `[ ]`|
| - Consistent structure for requests/responses. | | | | `[ ]`|
| - Clear error handling. | | | | `[ ]`|
| **Other JS Standards from Guide:** | | | | `[ ]`|
| - (Add specific checks based on guide) | | | | `[ ]`|

---

## 3. Layer 1: Models & ENUMs (SQLAlchemy)

**Relevant Files:**

- Model file: `src/models/{source_table_name}.py` (e.g., `src/models/single_search_jobs.py`): `_________________________`

**Checklist:**
| Standard | Current File(s) & Line(s) | Conforms? (Y/N) | Notes / Refactor Plan | Done |
|-----------------------------------------------|---------------------------|-----------------|----------------------------------------|------|
| **File Naming & Location** | | | | `[ ]`|
| - `src/models/{source_table_name}.py` | | | | `[ ]`|
| - See: `CONVENTIONS_AND_PATTERNS_GUIDE.md` (Models: File Naming) | | | | `[ ]`|
| **Class Naming** | | | | `[ ]`|
| - `{SourceTableName}Table` (e.g., `SingleSearchJobsTable`) | | | | `[ ]`|
| - See: `CONVENTIONS_AND_PATTERNS_GUIDE.md` (Models: Class Naming) | | | | `[ ]`|
| **Status Enum Naming & Values (if applicable)**| | | | `[ ]`|
| - Enum Name: `{WorkflowName}Status` (e.g., `SingleSearchStatus`) | | | | `[ ]`|
| - Values: `QUEUED`, `PROCESSING`, `COMPLETED`, `FAILED` etc. | | | | `[ ]`|
| - Defined _within_ the model file. | | | | `[ ]`|
| - See: `CONVENTIONS_AND_PATTERNS_GUIDE.md` (Models: Status Enum) & (DB ENUM Types) | | | | `[ ]`|
| **Column Naming & Types** | | | | `[ ]`|
| - snake_case, clear, descriptive. | | | | `[ ]`|
| - Correct SQLAlchemy types used. | | | | `[ ]`|
| **Relationships & Foreign Keys** | | | | `[ ]`|
| - Correctly defined and named. | | | | `[ ]`|
| **`__tablename__` matches file/class concept**| | | | `[ ]`|
| **Other Model Standards from Guide:** | | | | `[ ]`|
| - (Add specific checks based on guide) | | | | `[ ]`|

---

## 4. Layer 1: Models & ENUMs (Database ENUM Types - if not in Model)

**Note:** Standard is to define ENUMs within their respective model files. This section is for auditing any deviations.

**Relevant Files:**

- Usually `src/models/enums.py` if legacy, or check model file from Section 3.

**Checklist:**
| Standard | Current File(s) & Line(s) | Conforms? (Y/N) | Notes / Refactor Plan | Done |
|-----------------------------------------------|---------------------------|-----------------|--------------------------------------------------------|------|
| **ENUM Co-location** | | | | `[ ]`|
| - ENUM types (`CurationStatus`, `ProcessingStatus`, workflow-specific statuses) should be defined in the Python model file that uses them (e.g., `src/models/{source_table_name}.py`). | | | Plan: Move ENUM definition to its associated model file. | `[ ]`|
| - See: `CONVENTIONS_AND_PATTERNS_GUIDE.md` (DB ENUM Types: Manual Creation) & (Models: Status Enum) | | | | `[ ]`|
| **Manual DB Creation** | | | | `[ ]`|
| - `CREATE TYPE ... AS ENUM (...)` is run manually in DB. | | | Confirm migration script or manual process. | `[ ]`|
| - SQLAlchemy `PgEnum(..., create_type=False)` | | | | `[ ]`|
| **Naming Convention for Type in DB** | | | | `[ ]`|
| - `"{workflow_name}_status_enum"` (e.g., `"single_search_status_enum"`) | | | | `[ ]`|
| - See: `CONVENTIONS_AND_PATTERNS_GUIDE.md` (DB ENUM Types: Naming) | | | | `[ ]`|

---

## 5. Layer 2: Schemas (Data Validation)

**Relevant Files:**

- Schema file: `src/schemas/{workflow_name}_schemas.py` (e.g., `src/schemas/single_search_schemas.py`): `_________________________`

**Checklist:**
| Standard | Current File(s) & Line(s) | Conforms? (Y/N) | Notes / Refactor Plan | Done |
|-----------------------------------------------|---------------------------|-----------------|----------------------------------------|------|
| **File Naming & Location** | | | | `[ ]`|
| - `src/schemas/{workflow_name}_schemas.py` | | | | `[ ]`|
| - See: `CONVENTIONS_AND_PATTERNS_GUIDE.md` (Schemas: File Naming) | | | | `[ ]`|
| **Class Naming** | | | | `[ ]`|
| - Request Body: `{WorkflowName}Request` | | | | `[ ]`|
| - Create: `{WorkflowName}Create` | | | | `[ ]`|
| - Update: `{WorkflowName}Update` | | | | `[ ]`|
| - Response: `{WorkflowName}Response` / `{WorkflowName}Job` / `{WorkflowName}Details` | | | | `[ ]`|
| - See: `CONVENTIONS_AND_PATTERNS_GUIDE.md` (Schemas: Model Naming) | | | | `[ ]`|
| **Field Definitions** | | | | `[ ]`|
| - Match model fields where applicable. | | | | `[ ]`|
| - Appropriate use of `Optional`, validators. | | | | `[ ]`|
| **`Config.orm_mode = True` (if applicable)** | | | | `[ ]`|
| **Other Schema Standards from Guide:** | | | | `[ ]`|
| - (Add specific checks based on guide) | | | | `[ ]`|

---

## 6. Layer 3: Routers (FastAPI)

**Relevant Files:**

- Router file: `src/routers/{workflow_name}_router.py` (e.g., `src/routers/single_search_router.py`): `_________________________`
- Registration in `src/main.py`: `_________________________`

**Checklist:**
| Standard | Current File(s) & Line(s) | Conforms? (Y/N) | Notes / Refactor Plan | Done |
|-----------------------------------------------|---------------------------|-----------------|----------------------------------------|------|
| **File Naming & Location** | | | | `[ ]`|
| - `src/routers/{workflow_name}_router.py` | | | | `[ ]`|
| - See: `CONVENTIONS_AND_PATTERNS_GUIDE.md` (Routers: File Naming) | | | | `[ ]`|
| **Router Variable Naming** | | | | `[ ]`|
| - `router = APIRouter(prefix="/{workflow_name_pluralized}", tags=["{WorkflowName}"])` (e.g., `/single_searches`, tag `SingleSearch`) | | | | `[ ]`|
| - See: `CONVENTIONS_AND_PATTERNS_GUIDE.md` (Routers: Router Variable) | | | | `[ ]`|
| **Endpoint Paths & HTTP Methods** | | | | `[ ]`|
| - e.g., `POST /` (create), `GET /{id}` (read), `GET /` (list) | | | | `[ ]`|
| - See: `CONVENTIONS_AND_PATTERNS_GUIDE.md` (Routers: Endpoint Paths) | | | | `[ ]`|
| **Function Naming** | | | | `[ ]`|
| - `async def create_{workflow_name}(...)` | | | | `[ ]`|
| - `async def get_{workflow_name}_status(...)` | | | | `[ ]`|
| - See: `CONVENTIONS_AND_PATTERNS_GUIDE.md` (Routers: Function Naming) | | | | `[ ]`|
| **Request/Response Schemas** | | | | `[ ]`|
| - Correct Pydantic schemas used from Section 5. | | | | `[ ]`|
| **Dependency Injection for DB Session** | | | | `[ ]`|
| - `db: Session = Depends(get_db)` | | | | `[ ]`|
| **Dual Status Update Pattern (if applicable)**| | | | `[ ]`|
| - API sets `curation_status` & `processing_status` to `QUEUED`. | | | | `[ ]`|
| - See: `Q&A_Key_Insights.md` (Dual-Status Updates) | | | | `[ ]`|
| **Registration in `main.py`** | | | | `[ ]`|
| - `app.include_router({workflow_name}_router.{router_variable_name})` | | | | `[ ]`|
| **Other Router Standards from Guide:** | | | | `[ ]`|
| - (Add specific checks based on guide) | | | | `[ ]`|

---

## 7. Layer 4: Services (Business Logic, Orchestration)

**Relevant Files:**

- Primary service file: `src/services/{workflow_name}_service.py` (e.g., `src/services/single_search_service.py`): `_________________________`
- Processing service (if separate): `src/services/{workflow_name}_processing_service.py`: `_________________________`
- Scheduler registration (if applicable): `src/services/scheduler_service.py` or `src/main.py`: `_________________________`

**Checklist:**
| Standard | Current File(s) & Line(s) | Conforms? (Y/N) | Notes / Refactor Plan | Done |
|-----------------------------------------------|---------------------------|-----------------|----------------------------------------|------|
| **File Naming & Location** | | | | `[ ]`|
| - Orchestration/API-called: `src/services/{workflow_name}_service.py` | | | | `[ ]`|
| - Background/Scheduler: `src/services/{workflow_name}_processing_service.py` (or combined) | | | | `[ ]`|
| - See: `CONVENTIONS_AND_PATTERNS_GUIDE.md` (Services: File Naming) | | | | `[ ]`|
| **Function Naming (Orchestration)** | | | | `[ ]`|
| - `def process_{workflow_name}_request(...)` | | | | `[ ]`|
| - `def get_{workflow_name}_details(...)` | | | | `[ ]`|
| - See: `CONVENTIONS_AND_PATTERNS_GUIDE.md` (Services: Orchestration Function Naming) | | | | `[ ]`|
| **Function Naming (Processing/Background)** | | | | `[ ]`|
| - `def execute_{workflow_name}_task(...)` | | | | `[ ]`|
| - `def poll_{workflow_name}_queue(...)` | | | | `[ ]`|
| - See: `CONVENTIONS_AND_PATTERNS_GUIDE.md` (Services: Processing Function Naming) | | | | `[ ]`|
| **DB Session Management (for background tasks)**| | | | `[ ]`|
| - Use `with SessionLocal() as db:` context manager. | | | | `[ ]`|
| - See: `Q&A_Key_Insights.md` (Scheduler Session Management) | | | | `[ ]`|
| **Error Handling & Logging** | | | | `[ ]`|
| - Robust error handling, clear logging. | | | | `[ ]`|
| **Separation of Concerns** | | | | `[ ]`|
| - API interaction logic vs. core processing. | | | | `[ ]`|
| **Other Service Standards from Guide:** | | | | `[ ]`|
| - (Add specific checks based on guide) | | | | `[ ]`|

---

## 8. Background Tasks / Schedulers (APScheduler)

**Relevant Files:**

- Scheduler definition/registration: `src/services/scheduler_service.py` or `src/main.py`: `_________________________`
- Actual task function (likely in a `_processing_service.py` file from Section 7): `_________________________`

**Checklist:**
| Standard | Current File(s) & Line(s) | Conforms? (Y/N) | Notes / Refactor Plan | Done |
|-----------------------------------------------|---------------------------|-----------------|----------------------------------------|------|
| **Scheduler Job Registration** | | | | `[ ]`|
| - Function name in registration: `schedule_{workflow_name}_tasks` (e.g. `schedule_single_search_tasks`) | | | | `[ ]`|
| - Called function: e.g., `poll_{workflow_name}_queue` | | | | `[ ]`|
| - See: `CONVENTIONS_AND_PATTERNS_GUIDE.md` (Services: Scheduler Registration) | | | | `[ ]`|
| **Configuration for Interval/Trigger** | | | | `[ ]`|
| - Interval/cron defined in `src/config.py` or `.env`. | | | | `[ ]`|
| - Code accesses via `settings` object. | | | | `[ ]`|
| - See: `CONVENTIONS_AND_PATTERNS_GUIDE.md` (Config / Env Vars) | | | | `[ ]`|
| **DB Session Management** | | | | `[ ]`|
| - As per Section 7: `with SessionLocal() as db:`. | | | | `[ ]`|
| **Logging & Status Updates** | | | | `[ ]`|
| - Clear logs for task execution, success, failure. | | | | `[ ]`|
| - Updates `processing_status` in DB correctly. | | | | `[ ]`|
| **Other Scheduler Standards from Guide:** | | | | `[ ]`|
| - (Add specific checks based on guide) | | | | `[ ]`|

---

## 9. Configuration / Environment Variables

**Relevant Files:**

- `src/config.py`
- `.env` file (or template `.env.example`)

**Checklist:**
| Standard | Relevant Setting(s) | Conforms? (Y/N) | Notes / Refactor Plan | Done |
|-----------------------------------------------|---------------------------|-----------------|----------------------------------------|------|
| **Naming Convention** | | | | `[ ]`|
| - `{WORKFLOW_NAME}_SETTING_NAME` (e.g., `SINGLE_SEARCH_API_KEY`) | | | | `[ ]`|
| - See: `CONVENTIONS_AND_PATTERNS_GUIDE.md` (Config / Env Vars) | | | | `[ ]`|
| **Centralized Access** | | | | `[ ]`|
| - All config loaded via `src/config.py` (Pydantic `BaseSettings`). | | | | `[ ]`|
| **Defaults & Documentation** | | | | `[ ]`|
| - Sensible defaults in `config.py` or comments in `.env.example`. | | | | `[ ]`|
| **Other Config Standards from Guide:** | | | | `[ ]`|
| - (Add specific checks based on guide) | | | | `[ ]`|

---

## 10. Documentation & Testing

**Relevant Files:**

- Workflow-specific documentation (e.g., in `Docs/`): `_________________________`
- Test files (e.g., `tests/test_{workflow_name}.py`): `_________________________`

**Checklist:**
| Standard | Relevant File(s)/Area | Conforms? (Y/N) | Notes / Refactor Plan | Done |
|-----------------------------------------------|---------------------------|-----------------|----------------------------------------|------|
| **Docstrings** | | | | `[ ]`|
| - Clear, concise docstrings for all public modules, classes, functions. | All relevant Python files | | | `[ ]`|
| **Workflow Documentation File** | | | | `[ ]`|
| - `Docs/Workflows/{WF#}-{WorkflowName}.md` follows template. | | | Review/Update/Create | `[ ]`|
| - See: `CONVENTIONS_AND_PATTERNS_GUIDE.md` (Documentation Files) | | | | `[ ]`|
| **Test File Naming & Location** | | | | `[ ]`|
| - `tests/routers/test_{workflow_name}_router.py` | | | | `[ ]`|
| - `tests/services/test_{workflow_name}_service.py` | | | | `[ ]`|
| - See: `CONVENTIONS_AND_PATTERNS_GUIDE.md` (Testing) | | | | `[ ]`|
| **Test Coverage** | | | | `[ ]`|
| - Key positive/negative paths, edge cases. | | | Outline missing tests | `[ ]`|
| **Other Doc/Test Standards from Guide:** | | | | `[ ]`|
| - (Add specific checks based on guide) | | | | `[ ]`|

---

## 11. Refactoring Summary & Completion

**Overall Status:** (Pending / In Progress / Completed)

**Key Refactoring Actions Taken:**

1.  `__________________________________________________________________`
2.  `__________________________________________________________________`
3.  `__________________________________________________________________`
    ...

**Remaining Issues / Technical Debt for this Workflow:**

- `__________________________________________________________________`
- `__________________________________________________________________`

**Final Review Checklist:**

- [ ] All sections above completed and checked.
- [ ] Code changes committed with clear messages.
- [ ] Workflow functionality tested post-refactor.
- [ ] Associated documentation (if any) updated.

**Date Completed:** `_________________________`

---
