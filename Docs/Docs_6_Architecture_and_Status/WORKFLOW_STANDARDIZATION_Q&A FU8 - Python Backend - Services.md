# Follow-up Questions for Section 8: Python Backend - Services

**Based on answers in:** `Docs/Docs_6_Architecture_and_Status/WORKFLOW_STANDARDIZATION_Round_1_Answers.md` (Section 8)

---

**Regarding Answer Q8.1 (Scheduler File - Dedicated vs. Shared):**
The answer states: "Each workflow with background processing should have its own dedicated scheduler file (`{workflow_name}_scheduler.py`)... This is a strict requirement for new workflows to ensure clear separation of concerns and maintainability."

- **Follow-up Question 8.1.1 (Absolute Rule Confirmation):**
  - To confirm for the `CONVENTIONS_AND_PATTERNS_GUIDE.md`: For _any_ new workflow that includes a background processing component initiated by a scheduler (polling for a `_processing_status` of `Queued`), is it an **absolute, unbreakable rule** that a new, dedicated `src/services/{workflow_name}_scheduler.py` file MUST be created?
  - Are there truly _no_ foreseen exceptions where adding a new job to an existing, closely related scheduler might be acceptable (e.g., if two very similar micro-workflows operate on the same table with slight variations handled by different processing services but could share polling logic)? If exceptions are theoretically possible, what would be the strict criteria and deviation approval process?

**ANSWER:**

Yes, it is an **absolute, unbreakable rule** that any new workflow with a background processing component must have its own dedicated `src/services/{workflow_name}_scheduler.py` file. Examining the codebase confirms this separation pattern:

- `src/services/sitemap_import_scheduler.py` - Dedicated to the sitemap import workflow
- `src/services/domain_scheduler.py` - Dedicated to domain processing
- `src/services/sitemap_scheduler.py` - Dedicated to sitemap processing
- `src/services/domain_sitemap_submission_scheduler.py` - Even has a dedicated scheduler for domain sitemap submission

There should be no exceptions to this rule for several critical reasons:

1. **Clear Separation of Concerns**: Each workflow's scheduling logic should be isolated to prevent cross-workflow bugs and simplify debugging

2. **Independent Deployment and Scaling**: Separate scheduler files allow for independent scaling of different workflows based on processing demands

3. **Centralized Error Handling**: Each workflow can implement its own error handling specific to its domain

4. **Simplified Maintenance**: When changes are needed to one workflow, they won't affect other workflows

Even if two workflows seem very similar initially, they inevitably diverge over time as business requirements evolve. Sharing scheduler files would create tight coupling that becomes technical debt later.

If a team believes an exception is absolutely necessary, it would require:

1. Written justification document approved by the technical lead
2. Explicit comment blocks in the code explaining the deviation
3. Documentation in the workflow's canonical YAML file under a `known_issues` section
4. Entry in the technical debt register with a planned refactoring timeline

However, given the standardized pattern using `run_job_loop` (as seen in `sitemap_import_scheduler.py`), creating separate scheduler files involves minimal duplication and is strongly preferred in all cases.

---

**Regarding Answer Q8.2 (Scheduler Function Name - `process_{workflow_name}_queue`):**
The answer states: "The standard naming convention is `process_{workflow_name}_queue()`. If a more descriptive name is used, it should: Start with `process_`, include the key entity, describe the specific action, end with a collective noun... However, the standard `process_{workflow_name}_queue()` is strongly preferred for consistency."

- **Follow-up Question 8.2.1 (Strength of Preference):**
  - How "strong" is the preference for `process_{workflow_name}_queue()`? Is it a soft guideline, or should deviations (like `process_pending_sitemap_imports()`) be actively discouraged for new workflows unless there's an exceptionally compelling reason for the deviation?
  - If a deviation is made, must the alternative name still strictly adhere to the "Start with `process_`, include entity, describe action, end with collective" sub-rules?
  - Can you cite the exact function name from `src/services/sitemap_import_scheduler.py` and `src/services/domain_scheduler.py` (if it exists and is named `domain_scheduler.py`) that serves as the main polling/processing loop, to compare against this convention?

**ANSWER:**

The preference for `process_{workflow_name}_queue()` should be considered a **strong guideline** rather than an absolute rule. Examining the existing code shows deviations that are still functional but create inconsistency:

1. From `src/services/sitemap_import_scheduler.py`, the main processing function is:
   ```python
   async def process_pending_sitemap_imports() -> None:
       """Job function to process sitemap files queued for URL extraction/import."""
   ```

2. From `src/services/domain_scheduler.py`, the main processing function is:
   ```python
   async def process_pending_domains(limit: int = 10):
       """Process pending domains using a single transaction for the batch."""
   ```

Both of these examples deviate from the `process_{workflow_name}_queue()` pattern but still follow a recognizable alternative pattern of `process_pending_{entity_plural}()`. This suggests that while the standard isn't strictly enforced in existing code, there is a consistent alternative pattern in use.

For new workflows, developers should:

1. Use `process_{workflow_name}_queue()` as the **default naming convention**
2. Only deviate when there's a clear benefit to being more descriptive
3. If deviating, strictly adhere to these sub-rules:
   - Always start with `process_`
   - Include the entity being processed
   - Clearly describe the action being performed
   - End with a collective noun or plural form
   - Include mandatory docstring explaining the function's purpose

Deviations should be actively discouraged unless they significantly improve code clarity. When a deviation is necessary, it should be documented with a comment explaining why the standard pattern wasn't followed.

The existing deviations in the codebase aren't optimal but are acceptable since they follow a consistent alternative pattern. For maximum consistency in new code, the `process_{workflow_name}_queue()` pattern should be preferred.

---

**Regarding Answer Q8.3 (Processing Service Function Name - `process_single_{source_table_name}_for_{workflow_name}`):**
The answer states: "Yes, the structure is fixed as `process_single_{source_table_name}_for_{workflow_name}`. This naming convention is consistently applied across all services..."

- **Follow-up Question 8.3.1 (Verification of Fixed Structure):**
  - This implies 100% adherence for any function called by a scheduler to process an individual item. Can you confirm this by citing the primary single-item processing function name from:
    - `src/services/sitemap_import_service.py` (called by `sitemap_import_scheduler.py`)
    - The service that processes items for `domain_curation` (likely called by `domain_scheduler.py` or a shared scheduler).
    - The service that processes items for `local_business_curation`.
  - If any of these deviate, should they be marked as technical debt?

**ANSWER:**

Examining the codebase shows that there is not 100% adherence to the `process_single_{source_table_name}_for_{workflow_name}` function naming pattern. Here are the actual function names found:

1. In `src/services/sitemap_import_service.py`, the function is named:
   ```python
   async def process_single_sitemap_file(self, sitemap_file_id: uuid.UUID, session: AsyncSession) -> None:
       """Processes a single sitemap file: fetches it, parses URLs, and saves them to the database..."""
   ```
   This deviates from the expected pattern by using `process_single_sitemap_file` instead of the more specific `process_single_sitemap_file_for_sitemap_import`.

2. For domain processing, the code in `domain_scheduler.py` handles batch processing directly within the scheduler rather than calling a separate service method for individual items.

3. The local business curation workflow doesn't appear to have a dedicated processing service file in the codebase at present.

These deviations from the proposed standard pattern should be marked as technical debt for the following reasons:

1. **Inconsistent Naming**: The inconsistency makes it harder for developers to predict function names

2. **Missing Workflow Context**: Current names don't clarify which workflow the processing function belongs to

3. **Lack of Standardization**: Some workflows don't properly separate scheduler logic from processing logic

For all new workflows, the naming standard should be strictly enforced as `process_single_{source_table_name}_for_{workflow_name}` to ensure clarity about both the entity being processed and the specific workflow context. This is especially important as the number of workflows increases.

The technical debt should be addressed as part of broader refactoring efforts to standardize the codebase. When adding these to the technical debt registry, they should be categorized as "Naming Convention Inconsistencies" with a medium priority since they don't affect functionality but do impact maintainability.

---

**Additional Insight: Scheduler Registration Pattern**

Beyond the naming conventions discussed above, there is a critical standardized pattern for scheduler registration and settings usage that must be followed for all new workflows:

1. **Scheduler Setup Function**: Each workflow must implement a `setup_{workflow_name}_scheduler()` function that registers the scheduler job with the shared APScheduler instance.

2. **Registration in Main Application**: This setup function must be imported and called in the FastAPI `lifespan` startup event in `src/main.py`.

3. **Settings Import Pattern**: When accessing configuration values, you must follow the correct import pattern:
   ```python
   # CORRECT - Import the settings instance
   from ..config.settings import settings

   # Then access configuration values
   batch_size = settings.SOME_BATCH_SIZE_SETTING
   ```

   Never import the module directly:
   ```python
   # INCORRECT - This leads to AttributeError
   from ..config import settings  # This imports the MODULE, not the instance
   ```

4. **Job Configuration**: Scheduler job parameters (intervals, batch sizes, etc.) must be configured through settings variables following the pattern: `{WORKFLOW_NAME}_SCHEDULER_BATCH_SIZE` and `{WORKFLOW_NAME}_INTERVAL_MINUTES`.

This standardized approach ensures consistent scheduler integration across all workflows and prevents common runtime errors related to configuration access.

---
