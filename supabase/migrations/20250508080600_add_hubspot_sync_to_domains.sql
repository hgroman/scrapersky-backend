-- Migration: Add hubspot_sync workflow status fields to domains table
-- Created with Supabase MCP: 2025-05-08
-- Following ScraperSky naming conventions

-- Start a transaction for entire migration
BEGIN;

-- Create enum types for hubspot_sync workflow (following ScraperSky conventions)
-- Note: These are shared with the contacts table migration so we only create them if they don't exist
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

-- Add hubspot_sync_status column to domains table
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema='public'
        AND table_name='domains'
        AND column_name='hubspot_sync_status'
    ) THEN
        RAISE NOTICE 'Adding hubspot_sync_status column to domains table';
        ALTER TABLE domains ADD COLUMN hubspot_sync_status hubotsyncstatus NOT NULL DEFAULT 'New';

        -- Add index for improved query performance
        CREATE INDEX idx_domains_hubspot_sync_status ON domains(hubspot_sync_status);

        -- Add documentation comment
        COMMENT ON COLUMN domains.hubspot_sync_status IS 'Current status of the domain in the hubspot_sync workflow';

        RAISE NOTICE 'hubspot_sync_status column added successfully to domains';
    ELSE
        RAISE NOTICE 'hubspot_sync_status column already exists in domains';
    END IF;
EXCEPTION
    WHEN others THEN
        RAISE NOTICE 'Error adding hubspot_sync_status column to domains: %', SQLERRM;
END
$$;

-- Add hubspot_processing_status column to domains table
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema='public'
        AND table_name='domains'
        AND column_name='hubspot_processing_status'
    ) THEN
        RAISE NOTICE 'Adding hubspot_processing_status column to domains table';
        ALTER TABLE domains ADD COLUMN hubspot_processing_status hubsyncprocessingstatus NULL;

        -- Add index for improved query performance
        CREATE INDEX idx_domains_hubspot_processing_status ON domains(hubspot_processing_status);

        -- Add documentation comment
        COMMENT ON COLUMN domains.hubspot_processing_status IS 'Current processing status for the domain in the HubSpot sync background workflow';

        RAISE NOTICE 'hubspot_processing_status column added successfully to domains';
    ELSE
        RAISE NOTICE 'hubspot_processing_status column already exists in domains';
    END IF;
EXCEPTION
    WHEN others THEN
        RAISE NOTICE 'Error adding hubspot_processing_status column to domains: %', SQLERRM;
END
$$;

-- Add hubspot_processing_error column to domains table
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema='public'
        AND table_name='domains'
        AND column_name='hubspot_processing_error'
    ) THEN
        RAISE NOTICE 'Adding hubspot_processing_error column to domains table';
        ALTER TABLE domains ADD COLUMN hubspot_processing_error TEXT NULL;

        -- Add documentation comment
        COMMENT ON COLUMN domains.hubspot_processing_error IS 'Error message if HubSpot sync processing failed for this domain';

        RAISE NOTICE 'hubspot_processing_error column added successfully to domains';
    ELSE
        RAISE NOTICE 'hubspot_processing_error column already exists in domains';
    END IF;
EXCEPTION
    WHEN others THEN
        RAISE NOTICE 'Error adding hubspot_processing_error column to domains: %', SQLERRM;
END
$$;

-- Complete the transaction
COMMIT;
