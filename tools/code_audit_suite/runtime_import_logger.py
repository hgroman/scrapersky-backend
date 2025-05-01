import builtins
import os
import sys
import threading
from datetime import datetime

_original_import = builtins.__import__
_log_file = None
_logged_modules = set()
_lock = threading.Lock()
_initialized = False


def setup_runtime_logger(log_file="reports/runtime_imports.log"):
    """Overrides __import__ to log modules as they load."""
    global _log_file, _initialized
    if _initialized:
        print("Runtime logger already initialized.")
        return

    abs_log_file = os.path.abspath(log_file)
    _log_file = abs_log_file

    # Ensure the directory exists
    log_dir = os.path.dirname(abs_log_file)
    os.makedirs(log_dir, exist_ok=True)

    # Clear the log file at the start
    with open(_log_file, "w", encoding="utf-8") as f:
        f.write(f"# Runtime Import Log - Started at {datetime.now()}\n")

    print(f"Setting up runtime import logger. Logging to: {_log_file}")
    builtins.__import__ = _logged_import
    _initialized = True


def _logged_import(name, globals=None, locals=None, fromlist=(), level=0):
    """The custom import function that logs module imports."""
    # Call the original import function first
    module = _original_import(name, globals, locals, fromlist, level)

    # Log the import if it hasn't been logged yet and the logger is setup
    if _log_file and name and name not in _logged_modules:
        # Check if the imported module has a file path and if it's within the project (optional)
        # This helps filter out built-in modules or site-packages if desired
        try:
            module_path = getattr(module, "__file__", None)
            # Optionally, filter to only log modules within your project directory
            # project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            # if module_path and module_path.startswith(project_root):
            #     pass # Log this module
            # else:
            #     return module # Don't log non-project modules

        except Exception:
            # Some modules might raise errors when accessing __file__
            module_path = None

        # Use a lock for thread safety when writing to the set and file
        with _lock:
            if name not in _logged_modules:
                _logged_modules.add(name)
                try:
                    with open(_log_file, "a", encoding="utf-8") as f:
                        timestamp = datetime.now().isoformat()
                        f.write(f"{timestamp} | {name} | Path: {module_path}\n")
                except Exception as e:
                    # Avoid crashing the application if logging fails
                    print(
                        f"[Runtime Import Logger Error] Failed to write to log: {e}",
                        file=sys.stderr,
                    )

    return module


# Example Usage (e.g., in tests/conftest.py or manage.py):
#
# If using pytest:
# import pytest
# from tools.runtime_import_logger import setup_runtime_logger
#
# @pytest.fixture(scope='session', autouse=True)
# def import_logger(request):
#     """Initializes the runtime import logger for the test session."""
#     # You might want to make the log file path configurable or place it in tmp_path
#     log_path = "reports/runtime_imports.log"
#     print(f"\nInitializing import logger for test session. Log file: {log_path}")
#     setup_runtime_logger(log_file=log_path)
#     # No need to yield or teardown, the hook replaces __import__ globally
#
# If running a script or server:
# import os
# from tools.runtime_import_logger import setup_runtime_logger
#
# if __name__ == "__main__":
#     # Set up logging before importing most application modules
#     log_path = "reports/runtime_imports.log"
#     setup_runtime_logger(log_file=log_path)
#
#     # Now import and run your application
#     # from my_app import main
#     # main()
#     print("Application finished. Runtime imports logged.")
