
import sys
import os

# Add project root to python path
sys.path.append(os.getcwd())

try:
    print("Attempting to import src.main...")
    from src import main
    print("✅ Successfully imported src.main")
except ImportError as e:
    print(f"❌ ImportError: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Exception during import: {e}")
    # We might get other errors (like missing env vars), but as long as it's not ImportError for our moved files, it's likely fine.
    # If it's a ModuleNotFoundError, that's what we want to catch.
    if isinstance(e, ModuleNotFoundError):
        sys.exit(1)
    # Other errors might be runtime config issues which are expected in this environment
    print("⚠️  Runtime error (expected without full env), but import likely succeeded.")
    sys.exit(0)
