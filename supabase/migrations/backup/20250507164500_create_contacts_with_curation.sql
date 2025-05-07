-- Migration: Create contacts table with contact_curation workflow fields
-- Created with Supabase MCP: 2025-05-07

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

-- Create contacts table if it doesn't exist
CREATE TABLE IF NOT EXISTS contacts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    page_id UUID NULL,
    name TEXT NULL,
    email TEXT NULL,
    phone TEXT NULL,
    title TEXT NULL,
    company TEXT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Contact curation workflow fields
    contact_curation_status contactcurationstatus NOT NULL DEFAULT 'New',
    contact_processing_status contactprocessingstatus NULL,
    contact_processing_error TEXT NULL,

    -- Add constraint to link to pages table if it exists
    CONSTRAINT fk_page_id FOREIGN KEY(page_id) REFERENCES pages(id) ON DELETE SET NULL
);

-- Add indexes for improved query performance
CREATE INDEX IF NOT EXISTS idx_contacts_tenant_id ON contacts(tenant_id);
CREATE INDEX IF NOT EXISTS idx_contacts_page_id ON contacts(page_id);
CREATE INDEX IF NOT EXISTS idx_contacts_contact_curation_status ON contacts(contact_curation_status);
CREATE INDEX IF NOT EXISTS idx_contacts_contact_processing_status ON contacts(contact_processing_status);

-- Add comments for documentation
COMMENT ON TABLE contacts IS 'Stores contact information extracted from pages';
COMMENT ON COLUMN contacts.contact_curation_status IS 'Current status of the contact in the contact_curation workflow';
COMMENT ON COLUMN contacts.contact_processing_status IS 'Current processing status for the contact in the background workflow';
COMMENT ON COLUMN contacts.contact_processing_error IS 'Error message if processing failed for this contact';
