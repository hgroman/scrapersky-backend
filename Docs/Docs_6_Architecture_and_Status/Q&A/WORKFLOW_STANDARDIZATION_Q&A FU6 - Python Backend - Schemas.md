# Follow-up Questions for Section 6: Python Backend - Schemas (Pydantic)

**Based on answers in:** `Docs/Docs_6_Architecture_and_Status/WORKFLOW_STANDARDIZATION_Round_1_Answers.md` (Section 6)

---

**Regarding Answer Q6.1 (Schema File Location - `{workflow_name}.py` OR `source_table_name.py`):**
The answer states: "Use `{source_table}.py` when: Schemas are used across multiple workflows, primarily relate to the entity rather than a specific workflow action, define core CRUD operations. Use `{workflow_name}.py` when: Schemas are specific to a single workflow's actions, define operation-specific data structures not related to general entity CRUD, the workflow has multiple specialized request/response models. The most common practice appears to be using `{source_table}.py` for standard entity schemas and `{workflow_name}.py` for specialized workflow-specific schemas."

- **Follow-up Question 6.1.1 (Primary Choice and Override Condition):**
  - To make this more prescriptive for an MVP approach: Should the **default/primary** convention be to place new Pydantic schemas (Layer 2: Schemas) (especially for batch status updates like `PageBatchCurationUpdateRequest`) in a workflow-specific file, i.e., `src/schemas/{workflow_name}.py` (Layer 2: Schemas)?
  - And then, only if the schema is genuinely generic and intended for reuse by _other distinct workflows_ or for general CRUD on the entity, would it then be placed in `src/schemas/{source_table_name}.py` (Layer 2: Schemas)?
  - Could you cite an example from `src/schemas/` (Layer 2: Schemas) of a `{workflow_name}.py` file containing primarily workflow-action-specific schemas (Layer 2: Schemas) (e.g., our target `src/schemas/page_curation.py` (Layer 2: Schemas)) and an example of a `{source_table_name}.py` file that contains more generic, reusable entity schemas (Layer 2: Schemas)?

**ANSWER:**

Yes, the **default/primary** convention should be to place new Pydantic schemas (Layer 2: Schemas) for workflow-specific operations (such as batch status updates) in a workflow-specific file with the pattern `src/schemas/{workflow_name}.py` (Layer 2: Schemas). This approach aligns with the clear separation of concerns and emphasizes the workflow-specific nature of these operations.

Only schemas (Layer 2: Schemas) that are genuinely generic and intended for reuse by other distinct workflows or for general CRUD operations on the entity should be placed in `src/schemas/{source_table_name}.py` (Layer 2: Schemas). This makes the distinction clearer and helps prevent overloading the entity schema files with workflow-specific logic.

Examples from the codebase:

1. **Workflow-specific schema file (Layer 2: Schemas)** (`{workflow_name}.py`):

   - `src/schemas/page_curation.py` (Layer 2: Schemas) is an excellent example of a workflow-specific schema file (Layer 2: Schemas) that contains precisely the schemas (Layer 2: Schemas) needed for that workflow:

   ```python
   # From src/schemas/page_curation.py (Layer 2: Schemas)
   class PageCurationUpdateRequest(BaseModel):
       page_ids: List[UUID] = Field(..., min_length=1, description="List of one or more Page UUIDs to update.")
       curation_status: PageCurationStatus = Field(..., description="The target curation status to apply to the selected pages.") # (Layer 1: Models & ENUMs)

   class PageCurationUpdateResponse(BaseModel):
       message: str = Field(..., description="A summary message indicating the result of the operation.")
       updated_count: int = Field(..., description="The number of pages successfully updated.")
   ```

   This file focuses exclusively on the page curation workflow operations, with no generic CRUD schemas (Layer 2: Schemas).

2. **Entity-based schema file (Layer 2: Schemas)** (`{source_table_name}.py`):

   - `src/schemas/sitemap_file.py` (Layer 2: Schemas) follows the entity-based pattern with general CRUD schemas (Layer 2: Schemas):

   ```python
   # From src/schemas/sitemap_file.py (Layer 2: Schemas)
   # Base Schema: Fields common to Create and Read
   class SitemapFileBase(BaseModel):
       domain_id: uuid.UUID
       url: str = Field(..., alias="sitemap_url", examples=["https://example.com/sitemap.xml"])
       # ...

   # Schema for Creating a new SitemapFile
   class SitemapFileCreate(SitemapFileBase):
       pass  # Inherits all needed fields from Base for creation

   # Schema for Updating an existing SitemapFile
   class SitemapFileUpdate(BaseModel):
       # ...

   # Schema for Reading/Returning a SitemapFile
   class SitemapFileRead(SitemapFileBase):
       # ...
   ```

   This file includes the general CRUD operations (`Create`, `Update`, `Read`) that could be used by multiple workflows operating on sitemap files.

Notably, even in the entity-based schema file, when a workflow-specific operation like batch updates is needed, it still follows naming conventions that refer to the specific workflow purpose (e.g., `SitemapFileBatchUpdate`).

---

**Regarding Answer Q6.2 (Request/Response Model Naming):**
The answer states: "The standard naming convention is `{WorkflowNameTitleCase}BatchStatusUpdateRequest`. 'Batch' should always be included for batch operations. 'Curation' should be included when it refers specifically to the curation status." It also implies flexibility with `{SourceTableTitleCase}` as an alternative prefix.

- **Follow-up Question 6.2.1 (Model Naming Prefix - Clarification):**

  - The answer to Q4.1 (Python Enum Naming) strongly preferred `{WorkflowNameTitleCase}` for Enums to clearly associate with the workflow. For Pydantic request/response models (Layer 2: Schemas) related to a _specific workflow action_ (like a batch curation status update for `page_curation`), should the naming convention **mandate** using the `{WorkflowNameTitleCase}` prefix (e.g., `PageCurationBatchStatusUpdateRequest`) for utmost clarity and consistency with the Enum naming decision?
  - When would using `{SourceTableTitleCase}` (e.g., `PageBatchStatusUpdateRequest`) be appropriate for a workflow-specific action schema? Is it only if the `{workflow_name}` is nearly identical to the `{source_table_name}` (e.g., a hypothetical `page_publish` workflow operating on `page` table)?

**ANSWER:**

Yes, the naming convention should **mandate** using the `{WorkflowNameTitleCase}` prefix for Pydantic request/response models (Layer 2: Schemas) related to specific workflow actions. This ensures clarity and consistency with the Enum naming convention and makes the purpose of the schema immediately obvious.

Examining the existing codebase confirms this approach:

1. The workflow-specific schema (Layer 2: Schemas) in `src/schemas/page_curation.py` (Layer 2: Schemas) follows this pattern:

   ```python
   class PageCurationUpdateRequest(BaseModel):
       page_ids: List[UUID] = Field(..., min_length=1, description="List of one or more Page UUIDs to update.")
       curation_status: PageCurationStatus = Field(..., description="The target curation status to apply to the selected pages.")

   class PageCurationUpdateResponse(BaseModel):
       message: str = Field(..., description="A summary message indicating the result of the operation.")
       updated_count: int = Field(..., description="The number of pages successfully updated.")
   ```

   This clearly associates these schemas (Layer 2: Schemas) with the `page_curation` workflow rather than generic page operations.

Using `{SourceTableTitleCase}` would only be appropriate in two specific cases:

1. When the schema (Layer 2: Schemas) is for generic CRUD operations on the entity, placed in a `{source_table_name}.py` (Layer 2: Schemas) file
2. When the workflow name is nearly identical to the source table name, making the distinction redundant

However, even in the second case, it's better to err on the side of clarity by explicitly including the workflow name. The example in `src/schemas/sitemap_file.py` (Layer 2: Schemas) shows a hybrid approach with `SitemapFileBatchUpdate`, which is less clear than if it had been named `SitemapImportBatchUpdate` to directly tie it to the workflow.

For consistency with enum naming and to avoid confusion, the rule should be to always prefer the workflow name in the schema name for workflow-specific operations, regardless of similarity to the source table name.

- **Follow-up Question 6.2.2 (Suffixes "Request" and "Response"):**
  - Is it a strict rule that request models always end with "Request" (e.g., `...UpdateRequest`, `...CreateRequest`) and response models always end with "Response" (e.g., `...UpdateResponse`, `...GetResponse`)?
  - Can you point to a specific request model (e.g., for a batch update) and its corresponding response model in `src/schemas/` (Layer 2: Schemas) that clearly demonstrates this `...Request` / `...Response` suffix pattern along with the preferred `{WorkflowNameTitleCase}BatchStatus...` structure?

**ANSWER:**

Yes, it is a strict rule that request models always end with "Request" and response models always end with "Response". This clear naming convention is essential for maintaining consistency and readability throughout the codebase.

Examining the existing schemas (Layer 2: Schemas) in the codebase, we can see consistent adherence to this pattern:

1. In `src/schemas/page_curation.py` (Layer 2: Schemas), the request/response pair follows this pattern precisely:

   ```python
   class PageCurationUpdateRequest(BaseModel):
       page_ids: List[UUID] = Field(..., min_length=1, description="List of one or more Page UUIDs to update.")
       curation_status: PageCurationStatus = Field(..., description="The target curation status to apply to the selected pages.")

   class PageCurationUpdateResponse(BaseModel):
       message: str = Field(..., description="A summary message indicating the result of the operation.")
       updated_count: int = Field(..., description="The number of pages successfully updated.")
   ```

   This demonstrates the proper `{WorkflowNameTitleCase}...Request` and `{WorkflowNameTitleCase}...Response` pattern.

While the example above doesn't specifically include "BatchStatus" in the name (it uses "Update" instead), it still follows the core pattern of workflow-specific naming with Request/Response suffixes. The batch update operations in the codebase should follow a similar pattern with more specific naming like `PageCurationBatchStatusUpdateRequest` and `PageCurationBatchStatusUpdateResponse`.

The only exception to this pattern appears to be in `src/schemas/sitemap_file.py` (Layer 2: Schemas), where we find:

```python
class SitemapFileBatchUpdate(BaseModel):
    sitemap_file_ids: List[uuid.UUID]
    deep_scrape_curation_status: SitemapImportCurationStatusEnum
```

This class doesn't follow the "Request" suffix convention and should be considered technical debt. It would be more consistently named as `SitemapImportBatchUpdateRequest` to clearly identify it as both workflow-specific and a request model.

For standardization, all new schema (Layer 2: Schemas) classes should strictly follow:

- Request models: `{WorkflowNameTitleCase}[BatchStatus]UpdateRequest`
- Response models: `{WorkflowNameTitleCase}[BatchStatus]UpdateResponse`

---
