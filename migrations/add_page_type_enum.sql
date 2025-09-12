-- Database Migration: Add PageTypeEnum to replace TEXT page_type field
-- Work Order: WORK_ORDER_PAGE_TYPE_ENUM_IMPLEMENTATION.md
-- Date: 2025-09-12
-- Purpose: Convert page_type from TEXT to proper enum following codebase patterns

-- CRITICAL: Run pre-migration validation first to ensure all existing values are compatible

BEGIN;

-- Step 1: Create the PostgreSQL enum type
CREATE TYPE page_type_enum AS ENUM (
    'contact_root',
    'career_contact', 
    'about_root',
    'services_root',
    'menu_root',
    'pricing_root',
    'team_root',
    'legal_root',
    'wp_prospect',
    'unknown'
);

-- Step 2: Convert the existing column to use the enum
-- This is safe because all current values (contact_root, unknown) are included in enum
ALTER TABLE pages 
ALTER COLUMN page_type TYPE page_type_enum 
USING page_type::page_type_enum;

-- Step 3: Add index for performance (pages table will grow significantly)
CREATE INDEX IF NOT EXISTS idx_pages_page_type 
ON pages(page_type) 
WHERE page_type IS NOT NULL;

-- Step 4: Verify the migration succeeded
SELECT 
    page_type, 
    COUNT(*) as count,
    ROUND((COUNT(*) * 100.0 / SUM(COUNT(*)) OVER()), 1) as percentage
FROM pages 
WHERE page_type IS NOT NULL
GROUP BY page_type 
ORDER BY count DESC;

-- Display migration completion message
SELECT 'PageTypeEnum migration completed successfully' as status;

COMMIT;