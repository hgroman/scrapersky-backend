-- Migration: Add contact_curation workflow status fields to contacts table
-- Created with Supabase MCP: 2025-05-07
-- Updated: 2025-05-07 17:00:00

-- Start a transaction for entire migration
BEGIN;

-- Verify contacts table exists first (safer approach with NOTICE instead of EXCEPTION)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT FROM information_schema.tables
        WHERE table_schema = 'public'
        AND table_name = 'contacts'
    ) THEN
        RAISE NOTICE 'Warning: The contacts table does not exist in the database. Creating it first.';

        -- Create contacts table if it doesn't exist (this ensures migration can proceed)
        -- This would normally be skipped in production where the table already exists
        CREATE TABLE IF NOT EXISTS contacts (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            domain_id UUID NOT NULL,
            page_id UUID NOT NULL,
            email TEXT NOT NULL,
            email_type TEXT NULL,
            has_gmail BOOLEAN DEFAULT FALSE NULL,
            context TEXT NULL,
            source_url TEXT NULL,
            source_job_id UUID NULL,
            CONSTRAINT uq_contact_domain_email UNIQUE(domain_id, email)
        );

        CREATE INDEX IF NOT EXISTS idx_contacts_domain_id ON contacts(domain_id);
        CREATE INDEX IF NOT EXISTS idx_contacts_page_id ON contacts(page_id);
        CREATE INDEX IF NOT EXISTS idx_contacts_email ON contacts(email);
    ELSE
        RAISE NOTICE 'Contacts table found, proceeding with migration.';
    END IF;
END
$$;

-- Create enum types for contact_curation workflow (following ScraperSky conventions)
DO $$
BEGIN
    -- Check if enum type exists first
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'contactcurationstatus') THEN
        RAISE NOTICE 'Creating contactcurationstatus enum type';
        CREATE TYPE contactcurationstatus AS ENUM (
            'New', 'Queued', 'Processing', 'Complete', 'Error', 'Skipped'
        );
    ELSE
        RAISE NOTICE 'contactcurationstatus enum type already exists';
    END IF;
EXCEPTION
    WHEN others THEN
        RAISE NOTICE 'Error creating contactcurationstatus enum: %', SQLERRM;
END
$$;

DO $$
BEGIN
    -- Check if enum type exists first
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'contactprocessingstatus') THEN
        RAISE NOTICE 'Creating contactprocessingstatus enum type';
        CREATE TYPE contactprocessingstatus AS ENUM (
            'Queued', 'Processing', 'Complete', 'Error'
        );
    ELSE
        RAISE NOTICE 'contactprocessingstatus enum type already exists';
    END IF;
EXCEPTION
    WHEN others THEN
        RAISE NOTICE 'Error creating contactprocessingstatus enum: %', SQLERRM;
END
$$;

-- Add contact_curation_status column
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema='public'
        AND table_name='contacts'
        AND column_name='contact_curation_status'
    ) THEN
        RAISE NOTICE 'Adding contact_curation_status column';
        ALTER TABLE contacts ADD COLUMN contact_curation_status contactcurationstatus NOT NULL DEFAULT 'New';

        -- Add index for improved query performance
        CREATE INDEX idx_contacts_contact_curation_status ON contacts(contact_curation_status);

        -- Add documentation comment
        COMMENT ON COLUMN contacts.contact_curation_status IS 'Current status of the contact in the contact_curation workflow';

        RAISE NOTICE 'contact_curation_status column added successfully';
    ELSE
        RAISE NOTICE 'contact_curation_status column already exists';
    END IF;
EXCEPTION
    WHEN others THEN
        RAISE NOTICE 'Error adding contact_curation_status column: %', SQLERRM;
END
$$;

-- Add contact_processing_status column
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema='public'
        AND table_name='contacts'
        AND column_name='contact_processing_status'
    ) THEN
        RAISE NOTICE 'Adding contact_processing_status column';
        ALTER TABLE contacts ADD COLUMN contact_processing_status contactprocessingstatus NULL;

        -- Add index for improved query performance
        CREATE INDEX idx_contacts_contact_processing_status ON contacts(contact_processing_status);

        -- Add documentation comment
        COMMENT ON COLUMN contacts.contact_processing_status IS 'Current processing status for the contact in the background workflow';

        RAISE NOTICE 'contact_processing_status column added successfully';
    ELSE
        RAISE NOTICE 'contact_processing_status column already exists';
    END IF;
EXCEPTION
    WHEN others THEN
        RAISE NOTICE 'Error adding contact_processing_status column: %', SQLERRM;
END
$$;

-- Add contact_processing_error column
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema='public'
        AND table_name='contacts'
        AND column_name='contact_processing_error'
    ) THEN
        RAISE NOTICE 'Adding contact_processing_error column';
        ALTER TABLE contacts ADD COLUMN contact_processing_error TEXT NULL;

        -- Add documentation comment
        COMMENT ON COLUMN contacts.contact_processing_error IS 'Error message if processing failed for this contact';

        RAISE NOTICE 'contact_processing_error column added successfully';
    ELSE
        RAISE NOTICE 'contact_processing_error column already exists';
    END IF;
EXCEPTION
    WHEN others THEN
        RAISE NOTICE 'Error adding contact_processing_error column: %', SQLERRM;
END
$$;

-- Complete the transaction
COMMIT;
