import sys
import os
from datetime import datetime
import inspect

# Define the log file path relative to the project root (for context)
LOG_FILE_PATH = 'reports/runtime_imports.log'

# Ensure the reports directory exists
# This still needs to be done at the module level or in main.py before first import
os.makedirs('reports', exist_ok=True)

# <<< Removed all logging module setup >>>

class RuntimeImportHook:
    """
    A custom import hook (finder) that logs import attempts via print().
    It only logs and then returns None to let the standard import mechanism proceed.
    """
    def find_spec(self, fullname, path, target=None):
        try:
            # Get the current frame, which *might* be None
            current_frame = inspect.currentframe()
            caller_frame = None
            if current_frame:
                # Get the frame of the caller (one level up) if current_frame exists
                caller_frame = current_frame.f_back

            if caller_frame:
                caller_filename = caller_frame.f_code.co_filename
                lineno = caller_frame.f_lineno

                # Avoid logging imports triggered internally by this module or standard libraries if desired
                # Example: Exclude self and logging
                if caller_filename and __file__ not in caller_filename and 'logging/__init__.py' not in caller_filename:
                     timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                     print(f'{timestamp} - RUNTIME_IMPORT: {fullname} - FROM: {caller_filename}:{lineno}', flush=True)
            # else:
                 # Fallback print (usually safe to keep commented unless debugging the hook itself)
                 # timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                 # print(f'{timestamp} - RUNTIME_IMPORT: {fullname} - FROM: <unknown_caller>', flush=True)

        except Exception as e:
            # Print any error during the hook process itself
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
            print(f'{timestamp} - ERROR: Exception in import hook for {fullname}: {e}', flush=True)

        # Always return None to let the standard import mechanism continue
        return None

# --- Activation ---
# Create an instance of the hook
_runtime_hook = RuntimeImportHook()

# Insert the hook at the beginning of the meta_path
# This ensures it sees import attempts before standard finders
sys.meta_path.insert(0, _runtime_hook)

# Print activation confirmation to standard out
timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
print(f'{timestamp} - INFO: Runtime import print hook activated.', flush=True)
