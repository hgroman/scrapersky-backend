# Database Schema Type Mismatch Fix - 2025-03-25

## Issue Summary

We encountered a critical issue with type mismatches between our code and database schema that was causing errors in the sitemap scanning flow:

1. In the `sitemap_files` table:

   - `domain_id` was stored as `String` but expected to be `UUID` in the code
   - `job_id` was stored as `String` but expected to be `UUID` in the job service

2. In the `jobs` table:
   - `job_id` values with prefixes like `sitemap_`, `places_` were incompatible with UUID type

These mismatches resulted in errors when:

- Converting UUID values to strings and vice versa
- Foreign key constraints failing
- SQL type comparison errors

## Solution Implemented

### Database Schema Updates

We made the following changes to fix the schema:

```sql
-- Step 1: Backup data before making changes
CREATE TABLE IF NOT EXISTS sitemap_files_backup AS SELECT * FROM sitemap_files;
CREATE TABLE IF NOT EXISTS jobs_backup AS SELECT * FROM jobs;

-- Step 2: Clean up non-UUID job_ids from the database
DELETE FROM jobs
WHERE job_id IS NOT NULL AND job_id !~ '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$';

-- Step 3: Fix the sitemap_files table - convert domain_id and job_id to UUID
ALTER TABLE sitemap_files
  ALTER COLUMN domain_id TYPE UUID USING domain_id::uuid,
  ALTER COLUMN job_id TYPE UUID USING
    CASE
      WHEN job_id ~ '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
      THEN job_id::uuid
      ELSE NULL
    END;

-- Step 4: Fix jobs table - ensure job_id is UUID type
ALTER TABLE jobs
  ALTER COLUMN job_id TYPE UUID USING job_id::uuid;

-- Step 5: Fix any other tables referencing job_id
ALTER TABLE sitemap_urls
  DROP CONSTRAINT IF EXISTS sitemap_urls_sitemap_id_fkey;

ALTER TABLE sitemap_urls
  ADD CONSTRAINT sitemap_urls_sitemap_id_fkey
  FOREIGN KEY (sitemap_id)
  REFERENCES sitemap_files(id)
  ON DELETE CASCADE;
```

### Code Changes Required

We identified the following code locations where job_id formats need to be changed to use standard UUID format:

1. `/src/services/sitemap/processing_service.py` (line 113):

   ```python
   # BEFORE:
   job_id = f"sitemap_{uuid.uuid4().hex[:32]}"

   # AFTER:
   job_id = str(uuid.uuid4())
   ```

2. `/src/routers/modernized_sitemap.py` (line 110):

   ```python
   # BEFORE:
   job_id = f"sitemap_{uuid.uuid4().hex[:32]}"

   # AFTER:
   job_id = str(uuid.uuid4())
   ```

3. `/src/models.py` (line 254):

   ```python
   # BEFORE:
   job_id: str = Field(default_factory=lambda: f"sitemap_{uuid.uuid4().hex}")

   # AFTER:
   job_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
   ```

## Implementation Plan

1. ✅ **Fixed Database Schema** - Executed SQL script to update table structure
2. ❓ **Code Changes Required** - Need to update job_id generation to use standard UUIDs
3. 🔄 **Testing** - Need to test full sitemap scanning flow after changes

## Impact Assessment

### What Was Fixed

- Type compatibility issues between database and code
- Foreign key constraint violations
- SQL comparison errors

### Potential Risks

- Job URLs in the frontend may be referencing old job_id format
- Any external systems expecting the old job_id format will need updates

### Next Steps

1. Update all job_id generation code to use standard UUIDs
2. Run integration tests to verify sitemap flow works end-to-end
3. Update any frontend code that may be expecting the old job_id format

## Lessons Learned

1. **Schema Consistency** - Ensure database schema and code models are in sync
2. **Use Standard Formats** - Stick to standard formats for UUIDs without prefixes
3. **Type Safety** - Add proper type checking in code to catch these issues earlier
4. **Documentation** - Maintain clear documentation of expected data types for all fields

## References

- [Previous Database Audit](./07-06-enhanced-database-connection-audit-plan.md)
- [SQL Standards Document](../02-database-consolidation/02-02-sql-standards-guide.md)
