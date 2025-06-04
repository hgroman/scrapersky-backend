# ScraperSky Naming & Structural Conventions Guide - Layer 3: Routers

**Date:** 2025-05-11
**Version:** 1.0

## Related Documentation

- **[1.0-ARCH-TRUTH-Definitive_Reference.md](./1.0-ARCH-TRUTH-Definitive_Reference.md)** - Definitive architectural reference
- **[2.0-ARCH-TRUTH-Implementation_Strategy.md](./2.0-ARCH-TRUTH-Implementation_Strategy.md)** - Implementation strategy for architectural alignment
- **[3.0-ARCH-TRUTH-Layer_Classification_Analysis.md](./3.0-ARCH-TRUTH-Layer_Classification_Analysis.md)** - Comprehensive analysis of layer classification
- **[Q&A_Key_Insights.md](./Q&A_Key_Insights.md)** - Clarifications on implementation standards

**Objective:** This document details the naming and structural conventions for Layer 3 components (FastAPI Routers) within the ScraperSky backend project. Adherence to these conventions is crucial for maintaining consistency, readability, and maintainability across the codebase.

---

## 4. Layer 3: Routers

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

## Transaction Management (Critical for Compliance)

Transaction ownership is a core architectural principle. Routers are responsible for defining transaction boundaries, ensuring atomicity of operations that span multiple service calls or database interactions.

- **Router Transaction Ownership:** Routers **MUST** own transaction boundaries using `async with session.begin():`. This ensures that a series of database operations are treated as a single, atomic unit.
- **Session Dependency Injection:** Routers receive database sessions via dependency injection, typically `session: AsyncSession = Depends(get_async_session)`. Services **MUST NOT** create their own sessions.
- **Compliant Router Pattern Example:**
  ```python
  @router.put("/status")
  async def update_page_status_batch(
      request: PageCurationUpdateRequest,
      session: AsyncSession = Depends(get_async_session)
  ):
      async with session.begin():
          # Call service with session
          await service_function(session, data)
  ```
- **Compliance Impact:** This adherence to transaction boundary ownership in Layer 3 (Routers) is why it currently boasts an **82% compliance rate**. In contrast, Layer 4 (Services) is only 11% compliant because services often incorrectly create their own sessions or transactions, violating this fundamental rule.
