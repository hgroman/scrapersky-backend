# Runtime Import Tracing (`runtime_tracer.py`)

**Version:** 1.1 (Enhanced to track modules)
**Author:** [Assumed AI Assistance & Project Lead]
**Date:** 2025-04-30

## 1. Purpose and Goal

This utility provides runtime tracing capabilities specifically designed to track which Python files (`.py`) and corresponding modules within the `/app/src/` directory are loaded while the FastAPI application is running.

The primary goals are:

- **Debugging Dependency Issues:** Help diagnose `ModuleNotFoundError` or unexpected import behaviors by showing exactly what's being loaded.
- **Understanding Application Startup:** Visualize the sequence and scope of module loading during the application's initialization phase.
- **Aiding Code Audits (Project 41):** Provide data to help identify potentially unused code by comparing loaded files/modules against the full codebase.
- **Verifying Dynamic Imports:** Capture modules that might be loaded through mechanisms other than standard top-level imports.

## 2. How it Works

The tracer leverages Python's built-in tracing mechanisms:

- **`sys.settrace` / `threading.settrace`:** These functions are used to register a callback function (`trace_calls`) that gets executed at various points during code execution (like function calls, returns, line execution).
- **`trace_calls` Function:** This callback inspects the execution frame to find the filename being executed.
- **Filtering:** It specifically filters for events related to Python files (`.py`) located within the `/app/src/` directory (absolute path inside the container).
- **Tracking:**
  - **File Paths:** Unique absolute file paths (e.g., `/app/src/models/domain.py`) are added to a thread-safe set (`LOADED_SRC_FILES`).
  - **Module Names:** Corresponding module names (e.g., `src.models.domain`) are calculated from the file paths and added to a separate thread-safe set (`LOADED_MODULES`).
- **Thread Safety:** A `threading.Lock` (`_trace_lock`) is used to ensure safe concurrent access to the tracking sets from different threads.

## 3. Enabling/Disabling the Tracer

Tracing is controlled via an environment variable:

- **`ENABLE_IMPORT_TRACING`**:
  - Set to `true` (case-insensitive) to **enable** tracing.
  - Set to `false` or leave unset to **disable** tracing.

**Important Side Effect:** When `ENABLE_IMPORT_TRACING` is set to `true`, the `run_server.py` script **automatically disables Uvicorn's auto-reload feature**. This is necessary because auto-reloading interferes with the tracing mechanism.

## 4. Activation and Deactivation (Lifespan)

The tracer is integrated into the FastAPI application lifecycle using the `lifespan` context manager in `src/main.py`:

- **`start_tracing()`:** Called at the very beginning of the `lifespan` function, before the main application setup (like adding scheduler jobs) begins. This ensures tracing starts as early as possible.
- **`stop_tracing()`:** Called near the end of the `lifespan` function, _after_ the `yield` statement (where the application runs) but _before_ other shutdown tasks like closing the session manager or shutting down the scheduler.

## 5. Output and Logging

When tracing is **enabled** and the application **shuts down cleanly** (via the `lifespan` function completing), the following information is logged to the standard application output (e.g., Docker logs):

- Total count of unique `/app/src/*.py` files loaded.
- A list of each unique loaded file path, prefixed with `LOADED_SRC_FILE:`.
- Total count of unique `src.*` modules loaded.
- A list of each unique loaded module name, prefixed with `LOADED_MODULE:`.

Example Log Output:

```
...
INFO: Shutting down the ScraperSky API - Lifespan End
Stopping runtime file tracing...
INFO: Total unique /app/src/*.py files loaded: 55
INFO: LOADED_SRC_FILE: /app/src/config/logging_config.py
INFO: LOADED_SRC_FILE: /app/src/config/runtime_tracer.py
INFO: LOADED_SRC_FILE: /app/src/config/settings.py
... (many more files) ...
INFO: LOADED_SRC_FILE: /app/src/utils/validators.py
INFO: Total unique src.* modules loaded: 48
INFO: LOADED_MODULE: src.config.logging_config
INFO: LOADED_MODULE: src.config.runtime_tracer
INFO: LOADED_MODULE: src.config.settings
... (many more modules) ...
INFO: LOADED_MODULE: src.utils.validators
INFO: Shared APScheduler shutdown.
...
```

## 6. Accessing Data Programmatically

While the primary output is through logging at shutdown, the tracer utility also provides functions to access the collected data directly if needed:

- **`get_loaded_files() -> Set[str]`:** Returns a _copy_ of the set containing absolute paths of loaded `/app/src/*.py` files.
- **`get_loaded_modules() -> Set[str]`:** Returns a _copy_ of the set containing the names of loaded `src.*` modules.

These functions are available in `src.config.runtime_tracer`.

## 7. Code Location

- **Core Logic:** `src/config/runtime_tracer.py`
- **Activation/Logging:** `src/main.py` (within the `lifespan` function)
- **Enable/Disable Logic:** `run_server.py` (checks `ENABLE_IMPORT_TRACING` env var)

## 8. Limitations

- **Overhead:** Tracing adds some performance overhead. It should only be enabled for specific debugging or analysis sessions, not in production routinely.
- **Shutdown Requirement:** Logging only occurs if the application shuts down cleanly via the lifespan manager. Abrupt termination might prevent logs from being written.
- **Focus:** Only tracks `.py` files within `/app/src/`. Does not track standard library or third-party package imports unless they happen to reside within that specific path (which they shouldn't).
