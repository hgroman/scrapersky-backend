-- Create the hubotsyncstatus enum type if it doesn't exist
DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'hubotsyncstatus') THEN
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

-- Create the hubsyncprocessingstatus enum type if it doesn't exist
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
