-- WO-024: Fix local_businesses.domain_extraction_status column type
-- 
-- Problem: Column uses old enum type "domain_extraction_status" (PascalCase values)
-- Solution: Change to use renamed enum type "domain_extraction_status_enum" (snake_case)
--
-- This aligns with WO-022 which renamed the enum type but didn't update the column reference

ALTER TABLE local_businesses
ALTER COLUMN domain_extraction_status
TYPE domain_extraction_status_enum
USING domain_extraction_status::text::domain_extraction_status_enum;
