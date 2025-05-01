# Development User UUID Standardization Guide

## Critical Issue: Non-Standard UUIDs in Development User Functions

A critical issue was discovered in the sitemap scanning functionality where API calls would fail with a foreign key constraint violation, but test scripts would work correctly. The root cause was that development user functions were using non-standard ID formats.

```
IntegrityError: insert or update on table "sitemap_files" violates foreign key constraint "sitemap_files_created_by_fkey"
DETAIL: Key (created_by)=(00000000-0000-0000-0000-000000000000) is not present in table "users".
```

## The Problem

Multiple router modules defined development user functions that returned user IDs as string literals instead of proper UUID formats:

```python
# INCORRECT IMPLEMENTATION
async def get_development_user():
    return {
        "id": "dev-admin-id",       # String literal that's not a valid UUID
        "user_id": "dev-admin-id",  # String literal that's not a valid UUID
        # ...
    }
```

When these IDs were passed to database operations, foreign key constraints would fail because:

1. The UUID columns in the database expected proper UUID formats
2. The string literals used didn't match any existing user IDs

## The Solution

### Frontend Authentication: Use Hank Groman's Test User UUID

All development user functions should use Hank Groman's test user UUID directly:

```python
# CORRECT IMPLEMENTATION
async def get_development_user():
    return {
        "id": "5905e9fe-6c61-4694-b09a-6602017b000a",      # Hank Groman's test user UUID
        "user_id": "5905e9fe-6c61-4694-b09a-6602017b000a", # Hank Groman's test user UUID
        "email": "hankgroman@gmail.com",
        # Other user properties
    }
```

### Background Process User UUID Fallback

For background processing services that handle user IDs from various sources, implement a fallback to ensure invalid UUIDs are replaced with a valid one:

```python
# In background processing functions
if not user_id or user_id == "00000000-0000-0000-0000-000000000000":
    # Use the test user ID that we know exists in the database
    user_id = "5905e9fe-6c61-4694-b09a-6602017b000a"  # Hank Groman test user
```

## Test User Information

The test user ID to be used throughout the system belongs to Hank Groman:

```
Profile ID:         5905e9fe-6c61-4694-b09a-6602017b000a
Name:               Hank Groman
Email:              hankgroman@gmail.com
Tenant ID:          550e8400-e29b-41d4-a716-446655440000
Tenant Name:        Last Apple
```

This user account exists in the development database and should be used in all development user functions and as a fallback for operations that require a valid database user.

## Affected Files

This issue was found in multiple files:

### Frontend Authentication

- `src/routers/modernized_sitemap.py`
- `src/routers/modernized_page_scraper.py`
- `src/routers/batch_page_scraper.py`

### Background Processing

- `src/services/sitemap/processing_service.py`

## How to Verify UUID Format Issues

Testing with real user IDs will work (as in the test script), while API calls with development users may fail. The error message will typically include a foreign key constraint violation mentioning the `created_by` field.

## Testing Scripts vs Direct API Calls

- **Test scripts**: Used Hank Groman's real UUID: `5905e9fe-6c61-4694-b09a-6602017b000a`
- **Direct API calls**: Should use the same real UUID, not zero UUID or string literals
- **Background processes**: Should use the same real UUID when invalid IDs are encountered

## Prevention and Best Practices

1. **Always use Hank Groman's test user UUID** for development user functions and as fallback for invalid IDs
2. **Never use zero UUID** (`00000000-0000-0000-0000-000000000000`) for operations that need database validation
3. **Never use string literals** for IDs that will be used in database operations
4. **Implement fallback logic** in background processes to handle potentially invalid UUIDs

## Implementation Guidance

For development user functions:

```python
async def get_development_user():
    return {
        "id": "5905e9fe-6c61-4694-b09a-6602017b000a",
        "user_id": "5905e9fe-6c61-4694-b09a-6602017b000a",
        "email": "hankgroman@gmail.com",
        "tenant_id": DEFAULT_TENANT_ID,
        # Other user properties
    }
```

For background processes:

```python
# At the beginning of background task functions
if not user_id or user_id == "00000000-0000-0000-0000-000000000000":
    # Use the test user ID that we know exists in the database
    user_id = "5905e9fe-6c61-4694-b09a-6602017b000a"  # Hank Groman test user
    logger.info(f"Using test user ID for invalid UUID: {user_id}")
```

## Related Guides

- [10-TEST_USER_INFORMATION.md](./10-TEST_USER_INFORMATION.md) - For test user details
- [11-AUTHENTICATION_BOUNDARY.md](./11-AUTHENTICATION_BOUNDARY.md) - For JWT handling standards
- [16-UUID_STANDARDIZATION_GUIDE.md](./16-UUID_STANDARDIZATION_GUIDE.md) - For UUID format standards
- [17-CORE_ARCHITECTURAL_PRINCIPLES.md](./17-CORE_ARCHITECTURAL_PRINCIPLES.md) - Core principles
