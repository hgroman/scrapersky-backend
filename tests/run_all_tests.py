#!/usr/bin/env python3
"""
Batch Processor Test Suite Runner

This script runs all the batch processor tests in the correct sequence,
following the incremental testing methodology.

Usage:
    python run_all_tests.py [--verbose]
"""

import sys
import os
import argparse
import subprocess
import time
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f"logs/test_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    ]
)
logger = logging.getLogger("test_runner")

# Define the tests in order of dependency
TESTS = [
    {
        "name": "Database Connection",
        "script": "test_db_connection.py",
        "description": "Tests basic database connectivity with Supabase Supavisor"
    },
    {
        "name": "Batch Creation",
        "script": "test_batch_create.py",
        "description": "Tests the creation of batch records in the database"
    },
    {
        "name": "Batch Processing",
        "script": "test_batch_process.py",
        "description": "Tests the background task processing functionality"
    },
    {
        "name": "End-to-End Test",
        "script": "test_batch_e2e.py",
        "description": "Tests the complete batch processing workflow"
    }
]

def run_test(test, verbose=False):
    """Run a single test and return success status."""
    script_path = os.path.join(os.path.dirname(__file__), test["script"])

    logger.info(f"Running: {test['name']} - {test['description']}")
    logger.info(f"Executing: {script_path}")

    start_time = time.time()

    try:
        # Run the test script
        result = subprocess.run(
            [sys.executable, script_path],
            check=False,
            capture_output=True,
            text=True
        )

        # Calculate duration
        duration = time.time() - start_time

        # Process result
        if result.returncode == 0:
            logger.info(f"✅ {test['name']} PASSED (in {duration:.2f}s)")
            if verbose:
                logger.info(f"Output:\n{result.stdout}")
            return True
        else:
            logger.error(f"❌ {test['name']} FAILED (in {duration:.2f}s)")
            logger.error(f"Exit code: {result.returncode}")
            logger.error(f"Output:\n{result.stdout}")
            logger.error(f"Error output:\n{result.stderr}")
            return False

    except Exception as e:
        logger.error(f"❌ Error running {test['name']}: {str(e)}")
        return False

def run_all_tests(verbose=False):
    """Run all tests in sequence and report results."""
    logger.info("Starting batch processor test suite")
    logger.info(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Python: {sys.version}")
    logger.info(f"Working directory: {os.getcwd()}")
    logger.info(f"Verbose mode: {verbose}")
    logger.info("-" * 50)

    results = []
    start_time = time.time()

    # Run each test
    for test in TESTS:
        success = run_test(test, verbose)
        results.append({
            "name": test["name"],
            "success": success
        })

        # Break the sequence if a test fails
        if not success:
            logger.warning(f"Stopping test sequence due to failure in {test['name']}")
            break

        logger.info("-" * 50)

    # Calculate total duration
    total_duration = time.time() - start_time

    # Report summary
    passed = sum(1 for r in results if r["success"])
    total = len(results)

    logger.info("Test Suite Summary:")
    logger.info(f"Completed: {total} of {len(TESTS)} tests")
    logger.info(f"Passed: {passed}")
    logger.info(f"Failed: {total - passed}")
    logger.info(f"Total duration: {total_duration:.2f}s")

    # Print individual results
    logger.info("\nTest Results:")
    for result in results:
        status = "✅ PASSED" if result["success"] else "❌ FAILED"
        logger.info(f"{status} - {result['name']}")

    # Return overall success
    return passed == total

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run batch processor test suite")
    parser.add_argument("--verbose", action="store_true", help="Show verbose output")
    args = parser.parse_args()

    # Run all tests
    success = run_all_tests(verbose=args.verbose)

    # Exit with appropriate status code
    sys.exit(0 if success else 1)
