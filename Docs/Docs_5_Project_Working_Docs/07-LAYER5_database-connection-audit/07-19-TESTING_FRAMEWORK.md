# Testing Framework

This document outlines the testing framework for the ScraperSky Backend based on our successful implementation of the sitemap testing script.

## Core Testing Principles

1. **Use real user credentials** - All tests should use documented test users
2. **Test complete flows** - Test from API request to database storage
3. **Verify database results** - Check that data is correctly stored
4. **Handle error cases** - Test both successful and error paths
5. **Clean up after tests** - Leave the system in a clean state when possible

## Test User Information

All tests should use the documented test users. See [10-TEST_USER_INFORMATION.md](/AI_GUIDES/10-TEST_USER_INFORMATION.md) for details.

Primary test user:

- ID: `5905e9fe-6c61-4694-b09a-6602017b000a`
- Email: `hankgroman@gmail.com`
- Tenant ID: `550e8400-e29b-41d4-a716-446655440000`

## Test Script Template

Based on our successful sitemap test script, here's a template for creating test scripts for other services:

```python
#!/usr/bin/env python3
"""
Service Testing Script with Real User Authentication

This script uses a real user account to test the [SERVICE] functionality.
It simulates the complete flow from authentication to processing and result retrieval.
"""

import asyncio
import os
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

# Set environment to development
os.environ["ENVIRONMENT"] = "development"

# Import after path setup
from scripts.db.sb_connection import db
from src.models.[MODEL] import [MODEL_CLASS]
from src.services.[SERVICE].[SERVICE_MODULE] import [SERVICE_FUNCTION]

# Test user information
TEST_USER_ID = "5905e9fe-6c61-4694-b09a-6602017b000a"
TEST_USER_EMAIL = "hankgroman@gmail.com"
TEST_TENANT_ID = "550e8400-e29b-41d4-a716-446655440000"

# Safe dictionary access function
def safe_get(obj: Union[Dict[str, Any], Tuple[Any, ...], None], key: str, default: Any = "N/A") -> Any:
    """Safely get a value from a dictionary or tuple-based record"""
    if obj is None:
        return default
    if isinstance(obj, dict):
        return obj.get(key, default)
    # If it's something else, return default
    return default

async def setup_test_environment():
    """Setup any necessary test prerequisites"""
    print("\n=== Setting Up Test Environment ===")

    # Verify test user exists in profiles
    try:
        with db.get_cursor() as cursor:
            cursor.execute("SELECT * FROM profiles WHERE id = %s", (TEST_USER_ID,))
            user = cursor.fetchone()

            if not user:
                print(f"ERROR: Test user with ID {TEST_USER_ID} not found!")
                return False

            # Handle dictionary result type
            name = safe_get(user, 'name')
            email = safe_get(user, 'email')
            tenant_id = safe_get(user, 'tenant_id')

            print(f"Test user confirmed in profiles table")
            print(f"Name: {name}")
            print(f"Email: {email}")
            print(f"Tenant ID: {tenant_id}")

        return True
    except Exception as e:
        print(f"ERROR setting up test environment: {str(e)}")
        return False

async def test_service_function(parameter: str):
    """Test the specific service functionality"""
    print(f"\n=== Testing [SERVICE] Function ===")

    # Generate a unique job ID for this test if needed
    job_id = str(uuid.uuid4())

    print(f"Test parameters:")
    print(f"- Parameter: {parameter}")
    print(f"- Job ID: {job_id}")
    print(f"- User ID: {TEST_USER_ID}")

    try:
        # Process using the service function
        args = {
            "parameter": parameter,
            "job_id": job_id,
            "user_id": TEST_USER_ID
        }

        print(f"\nInitiating service call...")

        # Call the service function
        result = await [SERVICE_FUNCTION](args)

        print(f"Service processing completed for job {job_id}")

        # Check results in database
        try:
            with db.get_cursor() as cursor:
                cursor.execute(
                    "SELECT COUNT(*) as count FROM [TABLE] WHERE job_id = %s",
                    (job_id,)
                )
                result = cursor.fetchone()

                # Handle result safely
                count = 0
                if isinstance(result, dict):
                    count = result.get('count', 0)
                elif result and isinstance(result, (list, tuple)) and len(result) > 0:
                    count = result[0]

                print(f"\nFound {count} records for job {job_id}")

                if count > 0:
                    # Output sample data
                    pass
        except Exception as db_error:
            print(f"Error checking database records: {str(db_error)}")
            return False

        return True
    except Exception as e:
        print(f"ERROR during testing: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return False

async def main():
    """Main test function"""
    print("=== [SERVICE] Testing with Real User ===")
    print(f"Starting test at: {datetime.now()}")

    # Get parameter from command line if provided
    test_parameter = "default_parameter"
    if len(sys.argv) > 1:
        test_parameter = sys.argv[1]
        print(f"Using parameter from command line: {test_parameter}")

    # Setup test environment
    success = await setup_test_environment()
    if not success:
        print("Failed to set up test environment. Aborting tests.")
        return

    # Run the service test
    await test_service_function(test_parameter)

    print(f"\nTest completed at: {datetime.now()}")

if __name__ == "__main__":
    # Run the async test
    asyncio.run(main())
```

## Test Coverage Requirements

For each service, tests should cover:

1. **Happy Path** - Normal successful operation
2. **Input Validation** - Handling of invalid inputs
3. **Error Handling** - Proper handling of errors
4. **Edge Cases** - Empty results, large results, etc.
5. **Database Verification** - Confirm data is correctly stored

## Testing Services with Background Tasks

For services that use background tasks:

1. **Task Triggering** - Confirm task is properly queued
2. **Task Execution** - Verify task executes correctly
3. **Task Completion** - Check task completes and updates status
4. **Result Verification** - Verify results are correctly stored

## Testing Database Operations

For database operations:

1. **Connection Pooling** - Confirm proper connection pooling
2. **Transaction Management** - Verify transactions are properly managed
3. **Error Handling** - Check error handling in database operations
4. **Type Conversion** - Ensure proper type conversion (especially UUIDs)

## Testing API Endpoints

When testing API endpoints:

1. **Authentication** - Verify proper authentication
2. **Parameter Validation** - Check validation of request parameters
3. **Response Format** - Verify response format
4. **Error Responses** - Check error responses for proper status codes and messages

## Test Environment

All tests should run in the development environment:

```python
os.environ["ENVIRONMENT"] = "development"
```

This ensures:

- SSL certificate verification is disabled
- Database connection uses development settings
- No modification of production data

## Test Automation

As more tests are created, we should automate running them:

1. Create a test runner script to run all tests
2. Add CI/CD integration to run tests on code changes
3. Report test results for review

## Conclusion

Following this testing framework will ensure consistent, reliable testing across all services in the ScraperSky Backend. The sitemap testing script has provided a solid foundation for this approach.
