-- Create all enum types used in the application
-- Each enum is wrapped in its own DO block for better error handling

-- ContactEmailTypeEnum
DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'contact_email_type_enum') THEN
        CREATE TYPE contact_email_type_enum AS ENUM (
            'SERVICE',
            'CORPORATE',
            'FREE',
            'UNKNOWN'
        );
    END IF;
END $$;

-- ContactCurationStatus
DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'contactcurationstatus') THEN
        CREATE TYPE contactcurationstatus AS ENUM (
            'New',
            'Queued',
            'Processing',
            'Complete',
            'Error',
            'Skipped'
        );
    END IF;
END $$;

-- ContactProcessingStatus
DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'contactprocessingstatus') THEN
        CREATE TYPE contactprocessingstatus AS ENUM (
            'Queued',
            'Processing',
            'Complete',
            'Error'
        );
    END IF;
END $$;

-- HubSpotSyncStatus
DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'hubotsyncstatus') THEN
        DROP TYPE IF EXISTS hubotsyncstatus; -- Drop the typo'd version if it exists
        CREATE TYPE hubotsyncstatus AS ENUM (
            'New',
            'Queued',
            'Processing',
            'Complete',
            'Error',
            'Skipped'
        );
    END IF;
END $$;

-- HubSpotProcessingStatus
DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'hubsyncprocessingstatus') THEN
        CREATE TYPE hubsyncprocessingstatus AS ENUM (
            'Queued',
            'Processing',
            'Complete',
            'Error'
        );
    END IF;
END $$;

-- PageCurationStatus
DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'pagecurationstatus') THEN
        CREATE TYPE pagecurationstatus AS ENUM (
            'New',
            'Queued',
            'Processing',
            'Complete',
            'Error',
            'Skipped'
        );
    END IF;
END $$;

-- PageProcessingStatus
DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'pageprocessingstatus') THEN
        CREATE TYPE pageprocessingstatus AS ENUM (
            'Queued',
            'Processing',
            'Complete',
            'Error'
        );
    END IF;
END $$;

-- PlaceStatusEnum
DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'place_status_enum') THEN
        CREATE TYPE place_status_enum AS ENUM (
            'New',
            'Selected',
            'Maybe',
            'Not a Fit',
            'Archived'
        );
    END IF;
END $$;

-- GcpApiDeepScanStatusEnum
DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'gcp_api_deep_scan_status_enum') THEN
        CREATE TYPE gcp_api_deep_scan_status_enum AS ENUM (
            'Pending',
            'Running',
            'Complete',
            'Failed'
        );
    END IF;
END $$;

-- SitemapCurationStatusEnum
DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'sitemapcurationstatusenum') THEN
        CREATE TYPE sitemapcurationstatusenum AS ENUM (
            'New',
            'Selected',
            'Maybe',
            'Not a Fit',
            'Archived',
            'Completed'
        );
    END IF;
END $$;

-- SitemapFileStatusEnum
DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'sitemapfilestatusenum') THEN
        CREATE TYPE sitemapfilestatusenum AS ENUM (
            'New',
            'Processing',
            'Complete',
            'Error'
        );
    END IF;
END $$;

-- SitemapImportCurationStatusEnum
DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'sitemapimportcurationstatusenum') THEN
        CREATE TYPE sitemapimportcurationstatusenum AS ENUM (
            'New',
            'Queued',
            'Processing',
            'Complete',
            'Error',
            'Skipped'
        );
    END IF;
END $$;

-- SitemapImportProcessStatusEnum
DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'sitemapimportprocessstatusenum') THEN
        CREATE TYPE sitemapimportprocessstatusenum AS ENUM (
            'Queued',
            'Processing',
            'Complete',
            'Error'
        );
    END IF;
END $$;

-- DomainExtractionStatusEnum
DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'domainextractionstatusenum') THEN
        CREATE TYPE domainextractionstatusenum AS ENUM (
            'pending',
            'queued',
            'processing',
            'submitted',
            'failed'
        );
    END IF;
END $$;
