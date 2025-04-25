import os
import sys
import threading
from typing import Set

# Global set to store loaded file paths from /app/src
LOADED_SRC_FILES: Set[str] = set()
_trace_lock = threading.Lock()

# Flag to control tracing
is_tracing_enabled = False

def trace_calls(frame, event, arg):
    """Trace function to be registered with sys.settrace."""
    if event == 'call':
        code = frame.f_code
        filename = code.co_filename
        # Check if the file is within /app/src and is a .py file
        try:
            abs_filename = os.path.abspath(filename)
            if abs_filename.startswith('/app/src/') and abs_filename.endswith('.py'):
                # Add to set (thread-safe)
                with _trace_lock:
                    LOADED_SRC_FILES.add(abs_filename)
        except Exception:
            # Ignore errors during path resolution/checking
            pass
    return trace_calls  # Return itself to continue tracing

def start_tracing():
    """Enable tracing."""
    global is_tracing_enabled
    if not is_tracing_enabled:
        print("Starting runtime file tracing...")
        sys.settrace(trace_calls)
        is_tracing_enabled = True
        # Enable tracing in all threads created from this point
        threading.settrace(trace_calls)

def stop_tracing():
    """Disable tracing."""
    global is_tracing_enabled
    if is_tracing_enabled:
        print("Stopping runtime file tracing...")
        sys.settrace(None)
        threading.settrace(None)  # Disable for threads as well
        is_tracing_enabled = False

def get_loaded_files() -> Set[str]:
    """Return the set of loaded files."""
    with _trace_lock:
        # Return a copy
        return set(LOADED_SRC_FILES)
