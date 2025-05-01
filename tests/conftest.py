# tests/conftest.py

import uuid  # Added for generating fixture IDs

import pytest

# Add the project root to the Python path to allow importing tools
# project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# sys.path.insert(0, project_root)

# Now import the setup function
# try:
#     from tools.runtime_import_logger import setup_runtime_logger
# except ImportError as e:
#     print(f"Error importing runtime_import_logger: {e}")
#     # Define a dummy function if import fails to avoid crashing pytest setup
#     def setup_runtime_logger(log_file=None):
#         print(f"Dummy setup_runtime_logger called (import failed). Log file requested: {log_file}")

# @pytest.fixture(scope='session', autouse=True)
# def import_logger(request):
#     """Initializes the runtime import logger for the test session."""
#     # Define the log path relative to the project root
#     log_path = os.path.join(project_root, "reports/runtime_imports.log")
#     print(f"\nInitializing import logger for test session. Log file: {log_path}")
#     try:
#         setup_runtime_logger(log_file=log_path)
#         print("Runtime import logger setup successfully.")
#     except Exception as e:
#         print(f"Error setting up runtime import logger in conftest: {e}")
#     # No need to yield or teardown, the hook replaces __import__ globally


# Fixtures for tests
@pytest.fixture(scope="session")
def business_type():
    """Provides a default business type for tests."""
    return "restaurant"


@pytest.fixture(
    scope="function"
)  # Use function scope if tests might modify/expect unique IDs
def job_id():
    """Provides a unique job ID string for tests."""
    return str(uuid.uuid4())


@pytest.fixture(scope="function")  # Use function scope for uniqueness
def batch_id():
    """Provides a unique batch ID string for tests."""
    return str(uuid.uuid4())


@pytest.fixture(scope="session")  # Session scope is fine for a static domain
def domain():
    """Provides a default domain string for tests."""
    return "example.com"


# You can add other session-wide fixtures here if needed
