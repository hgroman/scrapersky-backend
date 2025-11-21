-- Migration: Cleanup Orphaned Sitemap Enum Types
-- Date: 2025-11-20
-- Related: Incident #003 - V2 Router Ghost Column
-- Commit: 314bca1

-- Purpose: Remove orphaned enum types that were causing confusion and errors
-- These types are not used by any columns and were left over from previous migrations

-- CRITICAL: Run this AFTER commit 314bca1 is deployed to production
-- CRITICAL: Verify no columns use these types before dropping

-- Verify current state (for logging)
DO $$
BEGIN
    RAISE NOTICE 'Current sitemap curation enum types:';
    RAISE NOTICE '%', (
        SELECT string_agg(typname, ', ')
        FROM pg_type
        WHERE typname ILIKE '%sitemap%curation%'
    );
END $$;

-- Drop orphaned enum types
-- CASCADE will drop any dependencies (there should be none)
DROP TYPE IF EXISTS sitemap_import_curation_status CASCADE;
DROP TYPE IF EXISTS sitemap_curation_status CASCADE;
DROP TYPE IF EXISTS sitemapimportcurationstatus CASCADE;
DROP TYPE IF EXISTS sitemapimportcurationstatusenum CASCADE;

-- Verify cleanup
DO $$
DECLARE
    remaining_types TEXT;
BEGIN
    SELECT string_agg(typname, ', ')
    INTO remaining_types
    FROM pg_type
    WHERE typname ILIKE '%sitemap%curation%';
    
    RAISE NOTICE 'Remaining sitemap curation enum types: %', remaining_types;
    
    -- Should only have sitemap_curation_status_enum
    IF remaining_types != 'sitemap_curation_status_enum' THEN
        RAISE WARNING 'Unexpected enum types remain: %', remaining_types;
    ELSE
        RAISE NOTICE 'Cleanup successful - only sitemap_curation_status_enum remains';
    END IF;
END $$;

-- Verify the column is still using the correct type
DO $$
DECLARE
    column_type TEXT;
BEGIN
    SELECT udt_name
    INTO column_type
    FROM information_schema.columns
    WHERE table_name = 'sitemap_files'
    AND column_name = 'deep_scrape_curation_status';
    
    RAISE NOTICE 'Column deep_scrape_curation_status uses type: %', column_type;
    
    IF column_type != 'sitemap_curation_status_enum' THEN
        RAISE EXCEPTION 'Column type mismatch! Expected sitemap_curation_status_enum, got %', column_type;
    END IF;
END $$;

-- Log completion
DO $$
BEGIN
    RAISE NOTICE 'Migration 20251120_cleanup_orphaned_sitemap_enums completed successfully';
    RAISE NOTICE 'Incident #003 database cleanup complete';
END $$;
