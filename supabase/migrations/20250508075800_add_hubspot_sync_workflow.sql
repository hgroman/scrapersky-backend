-- Migration: Add hubspot_sync workflow status fields to contacts table
-- Created with Supabase MCP: 2025-05-08
-- Following ScraperSky naming conventions

-- Start a transaction for entire migration
BEGIN;

-- Create enum types for hubspot_sync workflow (following ScraperSky conventions)
DO $$
BEGIN
    -- Check if enum type exists first
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'hubotsyncstatus') THEN
        RAISE NOTICE 'Creating hubotsyncstatus enum type';
        CREATE TYPE hubotsyncstatus AS ENUM (
            'New', 'Queued', 'Processing', 'Complete', 'Error', 'Skipped'
        );
    ELSE
        RAISE NOTICE 'hubotsyncstatus enum type already exists';
    END IF;
EXCEPTION
    WHEN others THEN
        RAISE NOTICE 'Error creating hubotsyncstatus enum: %', SQLERRM;
END
$$;

DO $$
BEGIN
    -- Check if enum type exists first
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'hubsyncprocessingstatus') THEN
        RAISE NOTICE 'Creating hubsyncprocessingstatus enum type';
        CREATE TYPE hubsyncprocessingstatus AS ENUM (
            'Queued', 'Processing', 'Complete', 'Error'
        );
    ELSE
        RAISE NOTICE 'hubsyncprocessingstatus enum type already exists';
    END IF;
EXCEPTION
    WHEN others THEN
        RAISE NOTICE 'Error creating hubsyncprocessingstatus enum: %', SQLERRM;
END
$$;

-- Add hubspot_sync_status column
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema='public'
        AND table_name='contacts'
        AND column_name='hubspot_sync_status'
    ) THEN
        RAISE NOTICE 'Adding hubspot_sync_status column';
        ALTER TABLE contacts ADD COLUMN hubspot_sync_status hubotsyncstatus NOT NULL DEFAULT 'New';

        -- Add index for improved query performance
        CREATE INDEX idx_contacts_hubspot_sync_status ON contacts(hubspot_sync_status);

        -- Add documentation comment
        COMMENT ON COLUMN contacts.hubspot_sync_status IS 'Current status of the contact in the hubspot_sync workflow';

        RAISE NOTICE 'hubspot_sync_status column added successfully';
    ELSE
        RAISE NOTICE 'hubspot_sync_status column already exists';
    END IF;
EXCEPTION
    WHEN others THEN
        RAISE NOTICE 'Error adding hubspot_sync_status column: %', SQLERRM;
END
$$;

-- Add hubspot_processing_status column
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema='public'
        AND table_name='contacts'
        AND column_name='hubspot_processing_status'
    ) THEN
        RAISE NOTICE 'Adding hubspot_processing_status column';
        ALTER TABLE contacts ADD COLUMN hubspot_processing_status hubsyncprocessingstatus NULL;

        -- Add index for improved query performance
        CREATE INDEX idx_contacts_hubspot_processing_status ON contacts(hubspot_processing_status);

        -- Add documentation comment
        COMMENT ON COLUMN contacts.hubspot_processing_status IS 'Current processing status for the contact in the HubSpot sync background workflow';

        RAISE NOTICE 'hubspot_processing_status column added successfully';
    ELSE
        RAISE NOTICE 'hubspot_processing_status column already exists';
    END IF;
EXCEPTION
    WHEN others THEN
        RAISE NOTICE 'Error adding hubspot_processing_status column: %', SQLERRM;
END
$$;

-- Add hubspot_processing_error column
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema='public'
        AND table_name='contacts'
        AND column_name='hubspot_processing_error'
    ) THEN
        RAISE NOTICE 'Adding hubspot_processing_error column';
        ALTER TABLE contacts ADD COLUMN hubspot_processing_error TEXT NULL;

        -- Add documentation comment
        COMMENT ON COLUMN contacts.hubspot_processing_error IS 'Error message if HubSpot sync processing failed for this contact';

        RAISE NOTICE 'hubspot_processing_error column added successfully';
    ELSE
        RAISE NOTICE 'hubspot_processing_error column already exists';
    END IF;
EXCEPTION
    WHEN others THEN
        RAISE NOTICE 'Error adding hubspot_processing_error column: %', SQLERRM;
END
$$;

-- Complete the transaction
COMMIT;
