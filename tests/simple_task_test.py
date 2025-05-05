"""
Simple Task Test

This is a minimal implementation of a background task handler that can be used
to verify FastAPI background task execution. It has minimal dependencies and
does not attempt to interact with the database.
"""

import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

# Setup basic logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("simple_task_test")

# Create markers directory if it doesn't exist
MARKERS_DIR = Path("/tmp/scraper_sky_task_markers")
MARKERS_DIR.mkdir(exist_ok=True, parents=True)


async def simple_test_task(test_id: str, additional_data: Optional[str] = None) -> None:
    """
    A minimal background task that only creates marker files.
    This function should be called as a FastAPI background task
    to verify task execution.

    Args:
        test_id: Test identifier
        additional_data: Any additional data to include in marker
    """
    # Create timestamp for unique marker filename
    timestamp = datetime.utcnow().isoformat().replace(":", "-")

    # Create a marker file with timestamp
    marker_path = MARKERS_DIR / f"simple_task_test_{test_id}_{timestamp}.txt"

    # First log message - should appear if task starts executing
    print(f"🔍 SIMPLE_TASK_STARTED: Test task {test_id} started at {timestamp}")
    logger.info(f"Simple test task {test_id} started at {timestamp}")

    try:
        # Write to marker file
        with open(marker_path, "w") as f:
            f.write(f"Task started at {timestamp}\n")
            f.write(f"test_id: {test_id}\n")
            if additional_data:
                f.write(f"additional_data: {additional_data}\n")

        # Second log message - should appear if file creation succeeds
        print(f"✅ SIMPLE_TASK_MARKER_CREATED: Created marker file for test {test_id}")
        logger.info(f"Created marker file: {marker_path}")

        # Add a small delay to simulate processing
        time.sleep(1)

        # Write completion marker
        with open(marker_path, "a") as f:
            f.write(f"Task completed at {datetime.utcnow().isoformat()}\n")

        # Final log message - should appear if task completes
        print(f"✅ SIMPLE_TASK_COMPLETED: Test task {test_id} completed")
        logger.info(f"Simple test task {test_id} completed")

    except Exception as e:
        # Error logging - should appear if an error occurs
        error_msg = f"Error in simple test task: {str(e)}"
        print(f"❌ SIMPLE_TASK_ERROR: {error_msg}")
        logger.error(error_msg)

        # Try to write error to marker file
        try:
            with open(marker_path, "a") as f:
                f.write(f"ERROR: {error_msg}\n")
        except:
            pass


def verify_simple_task_execution(test_id: str) -> bool:
    """
    Utility function to check if a simple test task has executed
    by looking for marker files.

    Args:
        test_id: Test identifier to look for

    Returns:
        Boolean indicating if marker files were found
    """
    # Look for marker files matching the test ID
    markers = list(MARKERS_DIR.glob(f"simple_task_test_{test_id}_*.txt"))

    logger.info(f"Found {len(markers)} marker files for test ID {test_id}")
    for marker in markers:
        logger.info(f"  {marker.name}")
        try:
            logger.info(f"  Contents: {marker.read_text()}")
        except Exception as e:
            logger.error(f"  Error reading marker: {e}")

    return len(markers) > 0
