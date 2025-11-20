-- Fix local_businesses.status column type
-- It was incorrectly using sitemap_import_curation_status (or similar)
-- It should use place_status_enum which matches the PlaceStatusEnum values

ALTER TABLE local_businesses
ALTER COLUMN status TYPE place_status_enum
USING status::text::place_status_enum;
