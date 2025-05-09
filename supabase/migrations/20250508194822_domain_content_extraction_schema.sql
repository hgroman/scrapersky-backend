-- Domain Content Extraction Schema Migration
-- Adds required tables and enums for the Domain Content Extraction service

-- Create content extraction status enum
DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'content_extraction_status_enum') THEN
        CREATE TYPE content_extraction_status_enum AS ENUM (
            'QUEUED_FOR_CONTENT_EXTRACTION',
            'PROCESSING_CONTENT_EXTRACTION',
            'CONTENT_EXTRACTION_COMPLETE',
            'CONTENT_EXTRACTION_ERROR'
        );
    END IF;
END $$;

-- Add new columns to domains table
ALTER TABLE domains
ADD COLUMN IF NOT EXISTS content_extraction_status content_extraction_status_enum DEFAULT 'QUEUED_FOR_CONTENT_EXTRACTION',
ADD COLUMN IF NOT EXISTS content_extraction_error TEXT,
ADD COLUMN IF NOT EXISTS last_crawled TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS metadata JSONB;

-- Create contacts table
CREATE TABLE IF NOT EXISTS contacts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    domain_id UUID NOT NULL REFERENCES domains(id) ON DELETE CASCADE,
    email TEXT NOT NULL,
    type TEXT NOT NULL DEFAULT 'general',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_domain_email UNIQUE(domain_id, email)
);

-- Create social_media table
CREATE TABLE IF NOT EXISTS social_media (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    domain_id UUID NOT NULL REFERENCES domains(id) ON DELETE CASCADE,
    platform TEXT NOT NULL,
    handle TEXT,
    url TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_domain_platform_url UNIQUE(domain_id, platform, url)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_contacts_domain_id ON contacts(domain_id);
CREATE INDEX IF NOT EXISTS idx_contacts_email ON contacts(email);
CREATE INDEX IF NOT EXISTS idx_social_media_domain_id ON social_media(domain_id);
CREATE INDEX IF NOT EXISTS idx_social_media_platform ON social_media(platform);
CREATE INDEX IF NOT EXISTS idx_domains_content_extraction_status ON domains(content_extraction_status);

-- Add comments for documentation
COMMENT ON TABLE contacts IS 'Stores contact information extracted from domain websites';
COMMENT ON TABLE social_media IS 'Stores social media links extracted from domain websites';
COMMENT ON COLUMN domains.content_extraction_status IS 'Tracks the status of content extraction for this domain';
COMMENT ON COLUMN domains.content_extraction_error IS 'Stores any error message from content extraction';
COMMENT ON COLUMN domains.last_crawled IS 'When the domain was last crawled for content';
COMMENT ON COLUMN domains.metadata IS 'Additional metadata extracted from the domain';
