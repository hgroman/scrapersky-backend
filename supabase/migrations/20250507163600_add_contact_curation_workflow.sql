-- Migration: Add contact_curation workflow status fields to contacts table (v2)
-- Created with Supabase MCP: 2025-05-07
-- Updated: 2025-05-07 16:47:00

-- First try to connect to the existing database and verify the contacts table exists
DO $$
DECLARE
    contacts_exists boolean;
BEGIN
    SELECT EXISTS (
        SELECT FROM information_schema.tables
        WHERE table_schema = 'public'
        AND table_name = 'contacts'
    ) INTO contacts_exists;

    IF NOT contacts_exists THEN
        RAISE EXCEPTION 'The contacts table does not exist in the database';
    END IF;
END
$$;

-- Create enum types for contact_curation workflow (following ScraperSky conventions)
DO $$
BEGIN
    -- Standard workflow status enums following ScraperSky naming conventions
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'contactcurationstatus') THEN
        CREATE TYPE contactcurationstatus AS ENUM (
            'New', 'Queued', 'Processing', 'Complete', 'Error', 'Skipped'
        );
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'contactprocessingstatus') THEN
        CREATE TYPE contactprocessingstatus AS ENUM (
            'Queued', 'Processing', 'Complete', 'Error'
        );
    END IF;
END
$$;

-- Add status tracking columns to contacts table (following ScraperSky naming conventions)
DO $$
BEGIN
    -- Add contact_curation_status column
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_schema='public' AND table_name='contacts'
                   AND column_name='contact_curation_status') THEN
        ALTER TABLE contacts ADD COLUMN contact_curation_status contactcurationstatus NOT NULL DEFAULT 'New';

        -- Add index for improved query performance
        EXECUTE 'CREATE INDEX IF NOT EXISTS idx_contacts_contact_curation_status ON contacts(contact_curation_status)';

        -- Add documentation comment
        COMMENT ON COLUMN contacts.contact_curation_status IS 'Current status of the contact in the contact_curation workflow';
    END IF;

    -- Add contact_processing_status column
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_schema='public' AND table_name='contacts'
                   AND column_name='contact_processing_status') THEN
        ALTER TABLE contacts ADD COLUMN contact_processing_status contactprocessingstatus NULL;

        -- Add index for improved query performance
        EXECUTE 'CREATE INDEX IF NOT EXISTS idx_contacts_contact_processing_status ON contacts(contact_processing_status)';

        -- Add documentation comment
        COMMENT ON COLUMN contacts.contact_processing_status IS 'Current processing status for the contact in the background workflow';
    END IF;

    -- Add contact_processing_error column
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_schema='public' AND table_name='contacts'
                   AND column_name='contact_processing_error') THEN
        ALTER TABLE contacts ADD COLUMN contact_processing_error TEXT NULL;

        -- Add documentation comment
        COMMENT ON COLUMN contacts.contact_processing_error IS 'Error message if processing failed for this contact';
    END IF;
END
$$;
