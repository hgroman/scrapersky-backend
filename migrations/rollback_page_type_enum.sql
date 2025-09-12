-- Rollback Script: Remove PageTypeEnum and revert to TEXT field
-- Work Order: WORK_ORDER_PAGE_TYPE_ENUM_IMPLEMENTATION.md
-- Date: 2025-09-12
-- Purpose: Emergency rollback if PageTypeEnum migration causes issues

-- WARNING: Only run this if the enum migration causes critical issues

BEGIN;

-- Step 1: Drop the index
DROP INDEX IF EXISTS idx_pages_page_type;

-- Step 2: Convert enum column back to TEXT
ALTER TABLE pages 
ALTER COLUMN page_type TYPE TEXT 
USING page_type::TEXT;

-- Step 3: Drop the enum type
DROP TYPE IF EXISTS page_type_enum;

-- Step 4: Verify rollback succeeded
SELECT 
    page_type, 
    COUNT(*) as count,
    pg_typeof(page_type) as data_type
FROM pages 
WHERE page_type IS NOT NULL
GROUP BY page_type 
ORDER BY count DESC;

-- Display rollback completion message
SELECT 'PageTypeEnum rollback completed - column reverted to TEXT' as status;

COMMIT;