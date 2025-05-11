# Guide: Scheduler Registration and Settings Import Patterns

**Document ID:** 28
**Date:** 2024-07-27
**Status:** Active

## Purpose

This guide documents the standard patterns used in this project for:

1.  Registering background jobs with the shared APScheduler instance.
2.  Correctly importing and using the application's Pydantic configuration settings (`settings` object).

Following these patterns is crucial for preventing common runtime errors, particularly `AttributeError` related to configuration access.

## 1. Shared Scheduler Registration Pattern

The application utilizes a single, shared `APScheduler` instance, typically defined in `src/scheduler_instance.py`. Background jobs are added to this scheduler during application startup using the following pattern:

1.  **Scheduler Instance:** A central `scheduler` object is created (`src/scheduler_instance.py`).
2.  **Job Logic Module:** Each distinct background task (e.g., domain processing, sitemap import) has its own service module (e.g., `src/services/domain_scheduler.py`).
3.  **Setup Function:** This service module contains a dedicated setup function (e.g., `setup_domain_scheduler()`).
4.  **Startup Call:** The main application entry point (`src/main.py`) imports and calls these `setup_*_scheduler()` functions within the FastAPI `lifespan` startup event.
5.  **`add_job` Call:** The `setup_*_scheduler()` function calls `scheduler.add_job()` on the shared instance, passing the job function, trigger details, and configuration parameters (often sourced from the `settings` object).
6.  **Start/Stop:** `src/main.py` manages the overall `scheduler.start()` and `scheduler.shutdown()`.

**Reference:** See `Docs/Docs_5_Project_Working_Docs/21-19-and-20-Work-Order-Supplemental/21.1-Supplemental.md` for a detailed dependency tree and flowchart of this process.

## 2. Settings Import Pattern (CRITICAL)

The application configuration is managed by a Pydantic `Settings` class within `src/config/settings.py`. At the bottom of this file, an **instance** of this class is created:

```python
# src/config/settings.py
class Settings(BaseSettings):
    # ... field definitions ...
    MY_SETTING: str = "default"
    # ... other settings ...

# CRITICAL: Instance creation at the end of the file
settings = Settings()
```

**Correct Import:**

To access configuration values in other modules (like scheduler setup functions, services, routers), you **MUST** import the `settings` **instance**, not the entire module or the `Settings` class.

```python
# Correct way (using relative import from a sibling 'services' directory):
from ..config.settings import settings

# Accessing a setting:
interval = settings.MY_SETTING
print(interval) # Output: 'default' (or value from environment)
```

**Incorrect Import (Leads to AttributeError):**

Importing the module directly will lead to errors when trying to access configuration attributes.

```python
# INCORRECT way:
from ..config import settings # This imports the MODULE object

# Attempting to access a setting:
try:
    interval = settings.MY_SETTING # This will FAIL
except AttributeError as e:
    print(f"Error: {e}")
    # Output: Error: module 'src.config.settings' has no attribute 'MY_SETTING'

# Why it fails:
# The 'settings' variable here refers to the module itself.
# The module contains the 'Settings' class and the 'settings' instance,
# but the attributes (like MY_SETTING) exist *on the instance*, not the module.
print(type(settings))       # Output: <class 'module'>
print(dir(settings))        # Output includes 'Settings' (class) and 'settings' (instance)
# print(settings.settings.MY_SETTING) # This *might* work but is confusing and non-standard
```

**Debugging Tip:**

If you encounter an `AttributeError: module 'src.config.settings' has no attribute '...'`, immediately check the import statement in the failing file. Ensure you are using `from ...config.settings import settings` to import the instance.

---

## See Also

- `21-SCHEDULED_TASKS_APSCHEDULER_PATTERN.md`: General APScheduler patterns and examples.
- `24-SHARED_SCHEDULER_INTEGRATION_GUIDE.md`: Detailed guide on integrating with the shared scheduler instance.
- `Docs/Docs_5_Project_Working_Docs/21-19-and-20-Work-Order-Supplemental/21.1-Supplemental.md`: Debugging session notes and architecture diagrams related to the shared scheduler.

---
