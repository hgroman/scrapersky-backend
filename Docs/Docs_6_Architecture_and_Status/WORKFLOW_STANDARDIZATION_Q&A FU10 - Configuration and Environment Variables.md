# Follow-up Questions for Section 10: Configuration & Environment Variables

**Based on answers in:** `Docs/Docs_6_Architecture_and_Status/WORKFLOW_STANDARDIZATION_Round_1_Answers.md` (Section 10)

---

**Regarding Answer Q10.1 (New Environment Variables):**
The answer states: "New environment variables are typically added to `.env.example` and `config.py`... Documentation is crucial... There isn't a strict naming prefix like `{WORKFLOW_NAME}_` but variables should be descriptive (e.g., `PAGE_CURATION_BATCH_SIZE`)."

- **Follow-up Question 10.1.1 (Naming Prefix Reconsideration for Clarity):**
  - Given the goal of maximum clarity and preventing naming collisions for workflow-specific settings (e.g., batch sizes, specific API keys for a workflow), would it be beneficial to **now establish a stricter convention** for new workflow-specific environment variables, such as `SCS_{WORKFLOW_NAME_UPPERCASE}_SETTING_NAME` (e.g., `SCS_PAGE_CURATION_BATCH_SIZE`)? `SCS_` for ScraperSky.
  - If not a strict prefix, what definitive guidelines can be provided to ensure names are "descriptive enough" to avoid ambiguity when multiple workflows might have similar-sounding settings (e.g., batch size for `page_curation` vs. batch size for `sitemap_import`)?
  - Where in `config.py` (or `src/core/config.py`) are these variables loaded and transformed into Pydantic `BaseSettings`? Can you point to an existing workflow-specific setting there and its corresponding `.env.example` entry?

**ANSWER:**

Examining the codebase reveals an established pattern for workflow-specific environment variables that could benefit from more explicit standardization.

1. **Naming Convention Assessment**:

   Currently, workflow-specific settings for scheduler-related parameters follow a pattern of `{WORKFLOW_NAME}_SCHEDULER_{PARAMETER}`. Examples from `src/config/settings.py`:

   ```python
   # Domain Scheduler settings
   DOMAIN_SCHEDULER_INTERVAL_MINUTES: int = 1
   DOMAIN_SCHEDULER_BATCH_SIZE: int = 10
   DOMAIN_SCHEDULER_MAX_INSTANCES: int = 1

   # Sitemap Import Scheduler settings
   SITEMAP_IMPORT_SCHEDULER_INTERVAL_MINUTES: int = 1
   SITEMAP_IMPORT_SCHEDULER_BATCH_SIZE: int = 20
   SITEMAP_IMPORT_SCHEDULER_MAX_INSTANCES: int = 1
   ```

   This pattern provides decent clarity but lacks a unified namespace prefix.

2. **Recommendation for Stricter Convention**:

   Adopting a stricter convention like `SCS_{WORKFLOW_NAME}_{SETTING_NAME}` would indeed be beneficial for several reasons:

   - It creates a clear namespace for all ScraperSky environment variables
   - It prevents potential collisions with third-party libraries or future integrations
   - It makes it immediately obvious which variables belong to our application

   While an immediate global refactoring might be disruptive, establishing this convention for all new workflows would improve clarity going forward.

3. **Definitive Naming Guidelines**:

   If retaining the current pattern, these guidelines should be followed:

   - For scheduler settings: `{WORKFLOW_NAME}_SCHEDULER_{PARAMETER}`
   - For workflow-specific API keys: `{WORKFLOW_NAME}_API_KEY`
   - For other workflow-specific settings: `{WORKFLOW_NAME}_{SETTING_PURPOSE}_{PARAMETER}`
   - Always use UPPERCASE for the entire variable name
   - Use underscores to separate words
   - Include the workflow name as the prefix to prevent ambiguity

4. **Configuration Loading**:

   The environment variables are loaded in `src/config/settings.py` using Pydantic's `BaseSettings` class:

   ```python
   class Settings(BaseSettings):
       # ...

       # Domain Scheduler settings
       DOMAIN_SCHEDULER_INTERVAL_MINUTES: int = 1
       DOMAIN_SCHEDULER_BATCH_SIZE: int = 10
       DOMAIN_SCHEDULER_MAX_INSTANCES: int = 1

       # ...

       model_config = SettingsConfigDict(
           env_file=".env", case_sensitive=False, extra="allow"
       )
   ```

   The corresponding `.env.example` entries are:

   ```
   # Domain Scheduler Configuration
   DOMAIN_SCHEDULER_INTERVAL_MINUTES=1
   DOMAIN_SCHEDULER_BATCH_SIZE=10
   DOMAIN_SCHEDULER_MAX_INSTANCES=1
   ```

   The settings are then accessed throughout the application by importing the `settings` instance (not the class) from `src/config/settings.py`:

   ```python
   from ..config.settings import settings

   batch_size = settings.DOMAIN_SCHEDULER_BATCH_SIZE
   ```

Based on the existing patterns and best practices, implementing a `SCS_` prefix would improve clarity and maintainability, particularly as the number of workflows grows.

---

**Regarding Answer Q10.2 (Workflow-Specific Config in `main.py` / `app_setup.py`):**
The answer states: "Workflow-specific setup (like Sentry tags or specialized logging) is typically done in `main.py` or a dedicated `app_setup.py`... the current `main.py` has examples."

- **Follow-up Question 10.2.1 (Centralized vs. Decentralized Setup):**
  - Is there a preferred location between `main.py` and a potential `src/core/app_setup.py` for workflow-specific initializations that need to happen at application startup (beyond just router inclusion)?
  - For a new workflow, if it requires, for example, setting a unique Sentry tag based on `workflow_name`, or initializing a specific client/resource it uses, what's the precise recommended way to integrate this into the app's startup sequence?
  - Can you cite an example from `main.py` where a _workflow-specific_ (not general like DB, Sentry globally) setup is performed?

**ANSWER:**

Examining the codebase reveals a clear pattern for workflow-specific initializations and their integration into the application startup sequence.

1. **Preferred Location for Workflow-Specific Initializations**:

   The codebase consistently uses the FastAPI `lifespan` context manager in `main.py` as the centralized location for initializing all application components, including workflow-specific elements. There is no separate `src/core/app_setup.py` file; instead, each workflow module provides its own setup function that gets called from the lifespan event.

   The pattern is:

   a. Define a setup function in the workflow's scheduler file (e.g., `setup_workflow_scheduler()` in `src/services/workflow_scheduler.py`)
   b. Import and call this setup function in the `lifespan` function in `main.py`

   This approach strikes a balance between centralization (all setup functions are called from one place) and decentralization (each workflow defines its own setup logic).

2. **Recommended Integration of Workflow-Specific Initializations**:

   For a new workflow requiring specific initialization:

   ```python
   # 1. In src/services/new_workflow_scheduler.py
   def setup_new_workflow_scheduler():
       """Setup function for the new workflow's scheduler and resources."""
       # Initialize any workflow-specific resources
       client = initialize_special_client()

       # Set up scheduler job with the shared scheduler instance
       try:
           scheduler.add_job(
               process_pending_new_workflow_items,
               trigger=IntervalTrigger(minutes=settings.NEW_WORKFLOW_SCHEDULER_INTERVAL_MINUTES),
               id="process_new_workflow",
               name="Process New Workflow",
               replace_existing=True,
               max_instances=settings.NEW_WORKFLOW_SCHEDULER_MAX_INSTANCES,
           )
           logger.info("Added New Workflow scheduler job to shared scheduler")
       except Exception as e:
           logger.error(f"Failed to setup New Workflow scheduler job: {e}", exc_info=True)

   # 2. In src/main.py - Import the setup function
   from .services.new_workflow_scheduler import setup_new_workflow_scheduler

   # 3. Then add to the lifespan context manager in main.py
   @asynccontextmanager
   async def lifespan(app: FastAPI):
       # ... existing code ...

       # Add the new workflow setup
       try:
           setup_new_workflow_scheduler()
       except Exception as e:
           logger.error(f"Failed to setup New Workflow scheduler job: {e}", exc_info=True)

       # ... rest of function ...
   ```

3. **Examples of Workflow-Specific Setup in `main.py`**:

   The clearest examples of workflow-specific initialization in `main.py` are the scheduler setup calls in the `lifespan` function:

   ```python
   @asynccontextmanager
   async def lifespan(app: FastAPI):
       # ... existing code ...

       # Add jobs from each module to the shared scheduler
       logger.info("Adding jobs to the shared scheduler...")
       try:
           setup_domain_scheduler()
       except Exception as e:
           logger.error(f"Failed to setup Domain scheduler job: {e}", exc_info=True)

       try:
           setup_sitemap_scheduler()
       except Exception as e:
           logger.error(f"Failed to setup Sitemap scheduler job: {e}", exc_info=True)

       try:
           setup_domain_sitemap_submission_scheduler()
       except Exception as e:
           logger.error(
               f"Failed to setup Domain Sitemap Submission scheduler job: {e}",
               exc_info=True,
           )

       # Setup for the renamed Sitemap Import scheduler
       try:
           setup_sitemap_import_scheduler()
       except Exception as e:
           logger.error(
               f"Failed to setup Sitemap Import scheduler job: {e}", exc_info=True
           )

       # ... rest of function ...
   ```

   Each call is workflow-specific, initializing the scheduler jobs for that particular workflow. This pattern provides clear separation of concerns while maintaining centralized startup control.

The established approach in the codebase has several advantages:

1. It keeps workflow-specific setup logic in the workflow's own files
2. It centralizes the actual initialization calls in a single place (`main.py`)
3. It provides consistent error handling for each setup step
4. It makes it easy to temporarily disable specific workflows by commenting out their setup calls

This hybrid approach is recommended for all new workflows requiring specific initialization.

---
