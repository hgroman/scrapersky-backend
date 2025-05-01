# 07-10 Schema Migrations Needed for Sitemap Service

## Schema Issues Identified

Based on the debug output from running the sitemap flow, several schema-related issues need to be resolved before the sitemap service can function correctly:

1. **Missing `url_count` Column**: The `sitemap_files` table is missing the `url_count` column that the code is trying to use.
2. **Type Mismatch in Job ID**: There's a type casting issue when comparing `job_id` (string) with UUID in the database queries.

## Required Migrations

### 1. Add `url_count` Column to `sitemap_files` Table

```sql
ALTER TABLE sitemap_files
ADD COLUMN url_count INTEGER DEFAULT 0;

-- Add a comment to explain the column
COMMENT ON COLUMN sitemap_files.url_count IS 'Number of URLs found in this sitemap file';
```

### 2. Fix Job ID Type in `jobs` Table

The error message indicates a type mismatch when updating job status:

```
operator does not exist: character varying = uuid
```

This suggests that the `job_id` column in the `jobs` table is defined as UUID, but the code is trying to use a string. There are two approaches to fix this:

#### Option A: Change Database Column Type (Preferred)

```sql
-- Change job_id column type from UUID to VARCHAR
ALTER TABLE jobs
ALTER COLUMN job_id TYPE VARCHAR;
```

#### Option B: Cast String to UUID in Code

Alternatively, we can modify the background service to cast the job_id to UUID before database operations.

## Implementation Plan

1. **Execute Schema Migrations**:

   - Create a migration script to add the missing column
   - Apply the type change for job_id

2. **Update Model Definitions**:

   - Ensure SQLAlchemy model definitions match the updated schema
   - Update type annotations in the code

3. **Verification**:
   - Re-run the debug script after schema changes
   - Verify that the sitemap scan completes successfully

## Impact Assessment

These schema changes are necessary but may impact existing functionality:

1. **Adding `url_count` Column**: Low impact - adds a new column with default value
2. **Changing `job_id` Type**: Medium impact - requires careful testing of job-related functionality

## Rollback Plan

If issues occur after implementation:

```sql
-- Rollback url_count column addition
ALTER TABLE sitemap_files
DROP COLUMN url_count;

-- Rollback job_id type change (if Option A was chosen)
ALTER TABLE jobs
ALTER COLUMN job_id TYPE UUID USING job_id::uuid;
```
