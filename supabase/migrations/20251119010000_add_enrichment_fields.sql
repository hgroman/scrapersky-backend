-- WO-021: Add n8n enrichment return data fields to contacts table
-- This migration adds fields to store enriched contact data received from n8n workflows
-- Created: 2025-11-19

-- ============================================================================
-- Enrichment Status Tracking Fields
-- ============================================================================

ALTER TABLE contacts
ADD COLUMN IF NOT EXISTS enrichment_status VARCHAR(20),
ADD COLUMN IF NOT EXISTS enrichment_started_at TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS enrichment_completed_at TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS enrichment_error TEXT,
ADD COLUMN IF NOT EXISTS last_enrichment_id VARCHAR(255);

-- ============================================================================
-- Enriched Data Fields (JSON/JSONB for flexible schema)
-- ============================================================================

ALTER TABLE contacts
ADD COLUMN IF NOT EXISTS enriched_phone VARCHAR(50),
ADD COLUMN IF NOT EXISTS enriched_address JSONB,
ADD COLUMN IF NOT EXISTS enriched_social_profiles JSONB,
ADD COLUMN IF NOT EXISTS enriched_company JSONB,
ADD COLUMN IF NOT EXISTS enriched_additional_emails JSONB,
ADD COLUMN IF NOT EXISTS enrichment_confidence_score INTEGER,
ADD COLUMN IF NOT EXISTS enrichment_sources JSONB;

-- ============================================================================
-- Enrichment Metadata Fields
-- ============================================================================

ALTER TABLE contacts
ADD COLUMN IF NOT EXISTS enrichment_duration_seconds FLOAT,
ADD COLUMN IF NOT EXISTS enrichment_api_calls INTEGER,
ADD COLUMN IF NOT EXISTS enrichment_cost_estimate FLOAT;

-- ============================================================================
-- Indexes for Performance
-- ============================================================================

-- Index for filtering by enrichment status
CREATE INDEX IF NOT EXISTS idx_contacts_enrichment_status
ON contacts(enrichment_status);

-- Index for idempotency checks
CREATE INDEX IF NOT EXISTS idx_contacts_last_enrichment_id
ON contacts(last_enrichment_id);

-- ============================================================================
-- Constraints
-- ============================================================================

-- Ensure enrichment_status is valid
ALTER TABLE contacts
ADD CONSTRAINT chk_enrichment_status
CHECK (enrichment_status IN ('pending', 'complete', 'partial', 'failed') OR enrichment_status IS NULL);

-- Ensure confidence_score is between 0 and 100
ALTER TABLE contacts
ADD CONSTRAINT chk_enrichment_confidence_score
CHECK (enrichment_confidence_score >= 0 AND enrichment_confidence_score <= 100 OR enrichment_confidence_score IS NULL);

-- ============================================================================
-- Comments for Documentation
-- ============================================================================

COMMENT ON COLUMN contacts.enrichment_status IS 'Current status of contact enrichment: pending, complete, partial, failed';
COMMENT ON COLUMN contacts.enrichment_started_at IS 'Timestamp when enrichment process started';
COMMENT ON COLUMN contacts.enrichment_completed_at IS 'Timestamp when enrichment process completed';
COMMENT ON COLUMN contacts.enrichment_error IS 'Error message if enrichment failed';
COMMENT ON COLUMN contacts.last_enrichment_id IS 'Unique ID of last enrichment run (for idempotency)';

COMMENT ON COLUMN contacts.enriched_phone IS 'Phone number discovered during enrichment';
COMMENT ON COLUMN contacts.enriched_address IS 'Address data (street, city, state, zip, country) as JSON';
COMMENT ON COLUMN contacts.enriched_social_profiles IS 'Social media profiles (linkedin, twitter, facebook, etc.) as JSON';
COMMENT ON COLUMN contacts.enriched_company IS 'Company information (name, website, industry, size) as JSON';
COMMENT ON COLUMN contacts.enriched_additional_emails IS 'Additional email addresses discovered as JSON array';
COMMENT ON COLUMN contacts.enrichment_confidence_score IS 'Quality score of enrichment data (0-100)';
COMMENT ON COLUMN contacts.enrichment_sources IS 'List of data sources used for enrichment as JSON array';

COMMENT ON COLUMN contacts.enrichment_duration_seconds IS 'Time taken to complete enrichment in seconds';
COMMENT ON COLUMN contacts.enrichment_api_calls IS 'Number of API calls made during enrichment';
COMMENT ON COLUMN contacts.enrichment_cost_estimate IS 'Estimated cost of enrichment in USD';
