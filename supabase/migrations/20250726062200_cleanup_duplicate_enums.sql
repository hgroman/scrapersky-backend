-- Cleanup duplicate enum types that were causing conflicts
-- The database columns use 'page_curation_status' and 'page_processing_status' (with underscores)
-- But there were also 'pagecurationstatus' and 'pageprocessingstatus' (without underscores) created

-- First check if the enum types without underscores are still in use
-- If not, drop them to avoid confusion

-- Drop the unused enum types (without underscores) if they exist
DO $$ BEGIN
    IF EXISTS (SELECT 1 FROM pg_type WHERE typname = 'pagecurationstatus') THEN
        -- Check if this type is actually being used by any columns
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE udt_name = 'pagecurationstatus'
        ) THEN
            DROP TYPE pagecurationstatus;
        END IF;
    END IF;
END $$;

DO $$ BEGIN
    IF EXISTS (SELECT 1 FROM pg_type WHERE typname = 'pageprocessingstatus') THEN
        -- Check if this type is actually being used by any columns
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE udt_name = 'pageprocessingstatus'
        ) THEN
            DROP TYPE pageprocessingstatus;
        END IF;
    END IF;
END $$;
