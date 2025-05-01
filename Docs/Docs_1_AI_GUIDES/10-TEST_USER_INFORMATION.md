# Test User Information Guide

## Available Test Users

We have confirmed real user accounts available for testing in the development environment:

### Primary Test User (Hank Groman - Last Apple)

```
Profile ID:         5905e9fe-6c61-4694-b09a-6602017b000a
Name:               Hank Groman
Email:              hankgroman@gmail.com
Active:             False
Role:               USER
Role ID:            2
Tenant ID:          550e8400-e29b-41d4-a716-446655440000
Tenant Name:        Last Apple
Tenant Description: Professional development tools for modern enterprises
```

### Secondary Test User (Personal Account)

```
Profile ID:         aa9c4524-7152-4ad6-abb1-b1008eef7625
Name:               Hank Groman
Email:              hgroman@gmail.com
Active:             True
Role:               USER
Role ID:            1
Tenant ID:          dd9ad211-e22f-4740-9c37-512223428ea8
Tenant Name:        HGroman@gmail
Tenant Description: Test Account. User Only. 1 Feature - LocalMiner
```

## Using These Accounts for Testing

These accounts can be used for various testing scenarios:

1. **Authentication Testing**:

   - Use the profile IDs and emails for login testing
   - Test password reset flows

2. **Multi-tenant Testing**:

   - Use different tenant IDs to test tenant isolation
   - Test functionality across different tenant contexts

3. **Role-Based Access Control Testing**:

   - Use the different role IDs to test permission checks
   - Test feature visibility based on role assignments

4. **Data Access Testing**:
   - Test endpoints that filter data by user profile
   - Verify tenant-specific data isolation

## Environment Variables for Testing

For testing flows that require authentication, you can use:

```bash
# Primary User (Last Apple)
export TEST_USER_ID=5905e9fe-6c61-4694-b09a-6602017b000a
export TEST_USER_EMAIL=hankgroman@gmail.com
export TEST_TENANT_ID=550e8400-e29b-41d4-a716-446655440000

# Secondary User (Personal)
export TEST_USER_ID_2=aa9c4524-7152-4ad6-abb1-b1008eef7625
export TEST_USER_EMAIL_2=hgroman@gmail.com
export TEST_TENANT_ID_2=dd9ad211-e22f-4740-9c37-512223428ea8
```

## Mocking User Context

For testing routes with authentication:

```python
@pytest.fixture
def authenticated_test_user():
    return {
        "user_id": "5905e9fe-6c61-4694-b09a-6602017b000a",
        "email": "hankgroman@gmail.com",
        "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
        "role": "USER",
        "role_id": 2
    }
```

## Development Testing Script

Quick script to verify user information programmatically:

```python
import os
from scripts.db.sb_connection import db

def verify_test_user():
    os.environ["ENVIRONMENT"] = "development"

    with db.get_cursor() as cursor:
        # Find the test user
        cursor.execute(
            "SELECT * FROM profiles WHERE id = %s",
            ('5905e9fe-6c61-4694-b09a-6602017b000a',)
        )
        user = cursor.fetchone()

        if user:
            print(f"Test user found: {user['name']} ({user['email']})")
            print(f"Tenant ID: {user['tenant_id']}")
            return True
        else:
            print("Test user not found!")
            return False

if __name__ == "__main__":
    verify_test_user()
```

**Note**: These are real user accounts in the development database. This information should NOT be used in production environments or included in public repositories.
