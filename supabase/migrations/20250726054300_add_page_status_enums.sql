-- Create the pagecurationstatus enum type if it doesn't exist
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

-- Create the pageprocessingstatus enum type if it doesn't exist
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
