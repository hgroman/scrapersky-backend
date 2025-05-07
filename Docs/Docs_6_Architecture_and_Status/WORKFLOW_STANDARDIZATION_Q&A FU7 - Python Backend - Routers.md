# Follow-up Questions for Section 7: Python Backend - Routers

**Based on answers in:** `Docs/Docs_6_Architecture_and_Status/WORKFLOW_STANDARDIZATION_Round_1_Answers.md` (Section 7)

---

**Regarding Answer Q7.1 (Router File Location - `{workflow_name}.py` OR `source_table_plural_name}.py`):**
The answer states criteria similar to schemas: Use `{source_table_plural_name}.py` for multiple operations on a single entity or when the entity is central; use `{workflow_name}.py` for workflow-specific operations, workflows spanning multiple entities, or specialized processes. Examples given: `pages.py` vs. `sitemap_import.py`.

- **Follow-up Question 7.1.1 (Primary Choice and Override Condition):**
  - For an MVP/default approach: If a new router is primarily for handling the batch status update endpoint for a specific workflow (e.g., the `/api/v3/pages/page_curation/status` endpoint for `page_curation`), should the **default/primary** convention be to create a workflow-specific router file, i.e., `src/routers/{workflow_name}.py`?
  - When would it be preferable to add this workflow-specific endpoint to an existing `src/routers/{source_table_plural_name}.py` file? Is it only if that file already exists and the new endpoint is a minor addition, or are there other overriding conditions?
  - Can you cite from `src/routers/` an example of a `{workflow_name}.py` file that primarily serves one workflow's endpoints, and an example of a `{source_table_plural_name}.py` file that handles more general CRUD or multiple workflow interactions for that entity?

**ANSWER:**

Yes, the **default/primary** convention for a new router primarily handling workflow-specific operations (like batch status updates) should be to create a workflow-specific router file following the pattern `src/routers/{workflow_name}.py`. This approach maintains clear separation of concerns and makes the codebase more maintainable as workflows evolve independently.

It would be preferable to add workflow-specific endpoints to an existing `src/routers/{source_table_plural_name}.py` file only when:

1. The file already exists and is actively maintained
2. The new endpoint is a minor addition that doesn't significantly change the router's focus
3. The workflow is tightly coupled to the entity and doesn't involve complex inter-entity interactions
4. The router file would otherwise be very small (containing just 1-2 endpoints)

Examples from the codebase:

1. **Workflow-specific router** (`{workflow_name}.py`):
   `src/routers/page_curation.py` is a perfect example of a workflow-specific router that exclusively handles endpoints related to the page curation workflow:

   ```python
   # src/routers/page_curation.py
   @router.put("/pages/curation-status", response_model=PageCurationUpdateResponse)
   async def update_page_curation_status_batch(
       request: PageCurationUpdateRequest,
       session: AsyncSession = Depends(get_session_dependency),
       # current_user: UserInToken = Depends(get_current_user) # Add if auth is needed
   ):
       """Updates the page_curation_status for a batch of pages.
       If the target curation status is 'Queued', this endpoint will also set the
       page_processing_status to 'Queued' and clear any previous processing errors."""
       # Implementation details...
   ```

   This file is dedicated to the page curation workflow and contains only the endpoints necessary for that specific workflow.

2. **Entity-based router** (`{source_table_plural_name}.py`):
   `src/routers/sitemap_files.py` follows the entity-based pattern, containing general CRUD operations for sitemap files as well as workflow-specific operations:

   ```python
   # src/routers/sitemap_files.py - General entity CRUD operation
   @router.post(
       "/",
       response_model=SitemapFileRead,
       status_code=status.HTTP_201_CREATED,
       summary="Create Sitemap File",
   )
   async def create_sitemap_file(
       sitemap_data: SitemapFileCreate,
       session: AsyncSession = Depends(get_db_session),
       current_user: Dict[str, Any] = Depends(get_current_user),
   ):
       # Implementation details...
   ```

   ```python
   # src/routers/sitemap_files.py - Workflow-specific operation
   @router.put(
       "/status",
       response_model=Dict[str, int],
       summary="Batch Update Sitemap File Curation Status",
   )
   async def update_sitemap_files_status_batch(
       update_request: SitemapFileBatchUpdate,
       session: AsyncSession = Depends(get_db_session),
       current_user: Dict[str, Any] = Depends(get_current_user),
   ):
       # Implementation details...
   ```

   This file handles both general CRUD operations for sitemap files and workflow-specific operations, showing how an entity-based router can incorporate multiple types of endpoints.

---

**Regarding Answer Q7.2 (Endpoint Path - Specific Action part: `/{workflow_name}/status` or `/status`):**
The answer states: "Include `/{workflow_name}` in the path when: The router is named after the source table (`{source_table_plural_name}.py`), Multiple workflows operate on the same entity. Omit `/{workflow_name}` when: The router is already named after the workflow (`{workflow_name}.py`), All endpoints in the router are specific to that workflow."

- **Follow-up Question 7.2.1 (Clarifying the Rule for Endpoint Definition):**
  - This implies a clear rule:
    - If router filename is `src/routers/{source_table_plural_name}.py`, the endpoint decorator should be `@router.put("/{workflow_name}/status", ...)`
    - If router filename is `src/routers/{workflow_name}.py`, the endpoint decorator should be `@router.put("/status", ...)`
  - Is this interpretation correct and intended as the strict standard for new workflows?
  - Could you provide one code example for each of these two cases from `src/routers/` (e.g., `pages.py` vs. `sitemap_import.py` if they fit) showing the router filename and the corresponding `@router.put(...)` path definition for a status update endpoint?

**ANSWER:**

Yes, this interpretation is correct and should be treated as the strict standard for new workflows. The rule ensures consistent endpoint paths based on router file organization:

1. If the router is entity-focused (`{source_table_plural_name}.py`), include the workflow name in the path to distinguish between different workflows operating on the same entity.
2. If the router is workflow-specific (`{workflow_name}.py`), omit the workflow name from the path since all endpoints in the file are already scoped to that workflow.

Examples from the codebase:

1. **Workflow-specific router** (`page_curation.py`):
   In a workflow-specific router file like `src/routers/page_curation.py`, the status update endpoint omits the workflow name from the path:

   ```python
   # src/routers/page_curation.py
   @router.put("/pages/curation-status", response_model=PageCurationUpdateResponse)
   async def update_page_curation_status_batch(...):
       # Implementation details...
   ```

   This example is somewhat atypical as it includes "pages" in the path despite being in a workflow-specific router. A more standardized version would be `@router.put("/status", ...)` for full compliance with the convention.

2. **Entity-based router** (`sitemap_files.py`):
   In an entity-focused router file like `src/routers/sitemap_files.py`, the status update endpoint uses a simpler `/status` path:

   ```python
   # src/routers/sitemap_files.py
   @router.put(
       "/status",
       response_model=Dict[str, int],
       summary="Batch Update Sitemap File Curation Status",
   )
   async def update_sitemap_files_status_batch(...):
       # Implementation details...
   ```

   Interestingly, this example doesn't include the workflow name in the path as would be strictly expected for an entity-based router (`/sitemap-import/status`). This represents a deviation from the ideal pattern.

These examples highlight some inconsistencies in the current implementation. For new workflows, the standard should be strictly enforced:

- `src/routers/{workflow_name}.py` → `@router.put("/status", ...)`
- `src/routers/{source_table_plural_name}.py` → `@router.put("/{workflow_name}/status", ...)`

---

**Regarding Answer Q7.3 (Endpoint Function Naming - `update_{source_table_name}_{workflow_name}_status_batch`):**
The answer mentions omitting `_{source_table_name}_` if the router is entity-specific or if the workflow name already incorporates the entity.

- **Follow-up Question 7.3.1 (Default Naming and Conditions for Shortening):**
  - Should the full `update_{source_table_name}_{workflow_name}_status_batch` be considered the **default, most explicit naming convention**?
  - What are the precise, objective conditions under which the `_{source_table_name}_` part can/should be omitted? Is it _only_ if the router filename is `{source_table_plural_name}.py`?
  - What are the precise, objective conditions under which the `_{workflow_name}_` part could be considered for omission (if ever, for a workflow-specific status update)?
  - Can you show an example from `src/routers/` of an endpoint function name that uses the full pattern, and one where `_{source_table_name}_` was omitted due to the router's entity-specific nature? For instance, in `src/routers/pages.py` (if it exists and has such an endpoint), would a function be `update_page_curation_status_batch` (omitting `_page_` as it's in `pages.py`)?

**ANSWER:**

Yes, the full `update_{source_table_name}_{workflow_name}_status_batch` should be considered the **default, most explicit naming convention** for endpoint functions. This comprehensive naming approach provides maximum clarity about what the function does, which entity it affects, and which workflow it belongs to.

The precise, objective conditions for omitting parts of this pattern are:

1. **Omit `_{source_table_name}_` when:**
   - The router filename is `{source_table_plural_name}.py` (entity-based router)
   - All endpoints in the file operate on the same entity type
   - The entity name would be redundant given the router's context

2. **Omit `_{workflow_name}_` when:**
   - The router filename is `{workflow_name}.py` (workflow-specific router)
   - All endpoints in the file belong to the same workflow
   - The workflow name would be redundant given the router's context

Examples from the codebase:

1. **With part of the full pattern omitted** (workflow-specific router):
   In `src/routers/page_curation.py`, we see the endpoint function name omits the source table name since it's a workflow-specific router:

   ```python
   # src/routers/page_curation.py
   async def update_page_curation_status_batch(
       request: PageCurationUpdateRequest,
       session: AsyncSession = Depends(get_session_dependency),
   ):
       # Implementation...
   ```

   This function is named `update_page_curation_status_batch` which includes both the source table name (`page`) and workflow name (`curation`). A strict adherence to the shortening rule would have resulted in `update_curation_status_batch` since it's in a workflow-specific router.

2. **With part of the full pattern omitted** (entity-based router):
   In `src/routers/sitemap_files.py`, the function name follows the entity-based pattern by focusing on the entity type:

   ```python
   # src/routers/sitemap_files.py
   async def update_sitemap_files_status_batch(
       update_request: SitemapFileBatchUpdate,
       session: AsyncSession = Depends(get_db_session),
       current_user: Dict[str, Any] = Depends(get_current_user),
   ):
       # Implementation...
   ```

   This function is named `update_sitemap_files_status_batch`, which includes the entity name (`sitemap_files`) but omits the specific workflow name. According to our convention, in an entity-based router, the function name should include the workflow name: `update_sitemap_files_import_status_batch`.

The examples from the codebase show some inconsistencies with the ideal pattern. For new workflows, the rule should be:

- In `{workflow_name}.py`: Use `update_{workflow_name}_status_batch` (omit entity name)
- In `{source_table_plural_name}.py`: Use `update_{source_table_name}_{workflow_name}_status_batch` (include both)

These rules ensure function names are contextually appropriate and non-redundant while maintaining sufficient clarity about their purpose.

---
