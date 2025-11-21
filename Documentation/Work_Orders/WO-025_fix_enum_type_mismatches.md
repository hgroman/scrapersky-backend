# Work Order: WO-025 - Fix Enum Type Mismatches (Fix Forward)

## 1. Context & Strategy
**Strategy:** FIX FORWARD (Database Migration)
The application code has been updated to use standardized snake_case Enum names (`place_status_enum`, `sitemap_curation_status_enum`). The database currently uses legacy names (`place_status`, `SitemapCurationStatusEnum`).
We will **migrate the database** to match the code.

## 2. Objectives
1.  Rename database Enum types to match the code expectations.
2.  Verify system stability after migration.

## 3. Instructions for Partner AI (Cascade)

### Step 1: Create Migration File
Create a new Supabase migration file (e.g., `20251120000003_fix_enum_names.sql`).

### Step 2: SQL Content
Write SQL to rename the types. **CRITICAL:** Use `IF EXISTS` to avoid errors if partial migrations occurred.

```sql
-- Fix Place Status Enum
-- Current DB: place_status
-- Target: place_status_enum
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_type WHERE typname = 'place_status') THEN
        ALTER TYPE place_status RENAME TO place_status_enum;
    END IF;
END
$$;

-- Fix Sitemap Curation Status Enum
-- Current DB: SitemapCurationStatusEnum (PascalCase)
-- Target: sitemap_curation_status_enum (snake_case)
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_type WHERE typname = 'SitemapCurationStatusEnum') THEN
        ALTER TYPE "SitemapCurationStatusEnum" RENAME TO sitemap_curation_status_enum;
    END IF;
END
$$;
```

### Step 3: Verification
1.  Run the migration.
2.  Restart the application.
3.  Verify `Places` workflow (search/staging) works.
4.  Verify `Domain` workflow (filtering) works.
