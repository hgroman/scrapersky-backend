-- Add n8n Contact Enrichment Fields (WO-021)
-- This migration adds columns to support contact enrichment via n8n workflows

ALTER TABLE contacts
ADD COLUMN IF NOT EXISTS enrichment_status VARCHAR(20),
ADD COLUMN IF NOT EXISTS enrichment_started_at TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS enrichment_completed_at TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS enrichment_error TEXT,
ADD COLUMN IF NOT EXISTS last_enrichment_id VARCHAR(255),
ADD COLUMN IF NOT EXISTS enriched_phone VARCHAR(50),
ADD COLUMN IF NOT EXISTS enriched_address JSONB,
ADD COLUMN IF NOT EXISTS enriched_social_profiles JSONB,
ADD COLUMN IF NOT EXISTS enriched_company JSONB,
ADD COLUMN IF NOT EXISTS enriched_additional_emails JSONB,
ADD COLUMN IF NOT EXISTS enrichment_confidence_score INTEGER,
ADD COLUMN IF NOT EXISTS enrichment_sources JSONB,
ADD COLUMN IF NOT EXISTS enrichment_duration_seconds FLOAT,
ADD COLUMN IF NOT EXISTS enrichment_api_calls INTEGER,
ADD COLUMN IF NOT EXISTS enrichment_cost_estimate FLOAT;

-- Add comment for documentation
COMMENT ON COLUMN contacts.enrichment_status IS 'Status of enrichment process: pending/complete/partial/failed';
COMMENT ON COLUMN contacts.enrichment_confidence_score IS 'Quality score 0-100 for enriched data';
