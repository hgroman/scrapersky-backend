-- Migration: Add DeBounce email validation fields to contacts table
-- Work Order: WO-017 Phase 1
-- Created: 2025-11-19
-- Purpose: Enable email validation quality gate before CRM sync

-- Start a transaction for entire migration
BEGIN;

-- Create enum type for debounce_validation_status
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'debounce_validation_status') THEN
        RAISE NOTICE 'Creating debounce_validation_status enum type';
        CREATE TYPE debounce_validation_status AS ENUM (
            'New', 'Selected', 'Queued', 'Processing', 'Complete', 'Error', 'Skipped'
        );
    ELSE
        RAISE NOTICE 'debounce_validation_status enum type already exists';
    END IF;
EXCEPTION
    WHEN others THEN
        RAISE NOTICE 'Error creating debounce_validation_status enum: %', SQLERRM;
END
$$;

-- Create enum type for debounce_processing_status
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'debounce_processing_status') THEN
        RAISE NOTICE 'Creating debounce_processing_status enum type';
        CREATE TYPE debounce_processing_status AS ENUM (
            'Queued', 'Processing', 'Complete', 'Error'
        );
    ELSE
        RAISE NOTICE 'debounce_processing_status enum type already exists';
    END IF;
EXCEPTION
    WHEN others THEN
        RAISE NOTICE 'Error creating debounce_processing_status enum: %', SQLERRM;
END
$$;

-- Add debounce_validation_status column
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema='public'
        AND table_name='contacts'
        AND column_name='debounce_validation_status'
    ) THEN
        RAISE NOTICE 'Adding debounce_validation_status column';
        ALTER TABLE contacts ADD COLUMN debounce_validation_status debounce_validation_status NULL;

        -- Add index for improved query performance
        CREATE INDEX idx_contacts_debounce_validation_status ON contacts(debounce_validation_status);

        -- Add documentation comment
        COMMENT ON COLUMN contacts.debounce_validation_status IS 'Current validation status of the contact email in DeBounce workflow';

        RAISE NOTICE 'debounce_validation_status column added successfully';
    ELSE
        RAISE NOTICE 'debounce_validation_status column already exists';
    END IF;
EXCEPTION
    WHEN others THEN
        RAISE NOTICE 'Error adding debounce_validation_status column: %', SQLERRM;
END
$$;

-- Add debounce_processing_status column
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema='public'
        AND table_name='contacts'
        AND column_name='debounce_processing_status'
    ) THEN
        RAISE NOTICE 'Adding debounce_processing_status column';
        ALTER TABLE contacts ADD COLUMN debounce_processing_status debounce_processing_status NULL;

        -- Add index for improved query performance
        CREATE INDEX idx_contacts_debounce_processing_status ON contacts(debounce_processing_status);

        -- Add documentation comment
        COMMENT ON COLUMN contacts.debounce_processing_status IS 'Current processing status for the contact in DeBounce validation background workflow';

        RAISE NOTICE 'debounce_processing_status column added successfully';
    ELSE
        RAISE NOTICE 'debounce_processing_status column already exists';
    END IF;
EXCEPTION
    WHEN others THEN
        RAISE NOTICE 'Error adding debounce_processing_status column: %', SQLERRM;
END
$$;

-- Add debounce_result column
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema='public'
        AND table_name='contacts'
        AND column_name='debounce_result'
    ) THEN
        RAISE NOTICE 'Adding debounce_result column';
        ALTER TABLE contacts ADD COLUMN debounce_result VARCHAR NULL;

        -- Add documentation comment
        COMMENT ON COLUMN contacts.debounce_result IS 'DeBounce validation result: valid, invalid, catch-all, unknown, or disposable';

        RAISE NOTICE 'debounce_result column added successfully';
    ELSE
        RAISE NOTICE 'debounce_result column already exists';
    END IF;
EXCEPTION
    WHEN others THEN
        RAISE NOTICE 'Error adding debounce_result column: %', SQLERRM;
END
$$;

-- Add debounce_score column
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema='public'
        AND table_name='contacts'
        AND column_name='debounce_score'
    ) THEN
        RAISE NOTICE 'Adding debounce_score column';
        ALTER TABLE contacts ADD COLUMN debounce_score INTEGER NULL;

        -- Add documentation comment
        COMMENT ON COLUMN contacts.debounce_score IS 'DeBounce validation confidence score (0-100)';

        RAISE NOTICE 'debounce_score column added successfully';
    ELSE
        RAISE NOTICE 'debounce_score column already exists';
    END IF;
EXCEPTION
    WHEN others THEN
        RAISE NOTICE 'Error adding debounce_score column: %', SQLERRM;
END
$$;

-- Add debounce_reason column
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema='public'
        AND table_name='contacts'
        AND column_name='debounce_reason'
    ) THEN
        RAISE NOTICE 'Adding debounce_reason column';
        ALTER TABLE contacts ADD COLUMN debounce_reason VARCHAR(500) NULL;

        -- Add documentation comment
        COMMENT ON COLUMN contacts.debounce_reason IS 'Explanation if email validation failed';

        RAISE NOTICE 'debounce_reason column added successfully';
    ELSE
        RAISE NOTICE 'debounce_reason column already exists';
    END IF;
EXCEPTION
    WHEN others THEN
        RAISE NOTICE 'Error adding debounce_reason column: %', SQLERRM;
END
$$;

-- Add debounce_suggestion column
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema='public'
        AND table_name='contacts'
        AND column_name='debounce_suggestion'
    ) THEN
        RAISE NOTICE 'Adding debounce_suggestion column';
        ALTER TABLE contacts ADD COLUMN debounce_suggestion VARCHAR NULL;

        -- Add documentation comment
        COMMENT ON COLUMN contacts.debounce_suggestion IS 'DeBounce suggested correction (did you mean)';

        RAISE NOTICE 'debounce_suggestion column added successfully';
    ELSE
        RAISE NOTICE 'debounce_suggestion column already exists';
    END IF;
EXCEPTION
    WHEN others THEN
        RAISE NOTICE 'Error adding debounce_suggestion column: %', SQLERRM;
END
$$;

-- Add debounce_processing_error column
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema='public'
        AND table_name='contacts'
        AND column_name='debounce_processing_error'
    ) THEN
        RAISE NOTICE 'Adding debounce_processing_error column';
        ALTER TABLE contacts ADD COLUMN debounce_processing_error TEXT NULL;

        -- Add documentation comment
        COMMENT ON COLUMN contacts.debounce_processing_error IS 'Error message if DeBounce validation processing failed';

        RAISE NOTICE 'debounce_processing_error column added successfully';
    ELSE
        RAISE NOTICE 'debounce_processing_error column already exists';
    END IF;
EXCEPTION
    WHEN others THEN
        RAISE NOTICE 'Error adding debounce_processing_error column: %', SQLERRM;
END
$$;

-- Add debounce_validated_at column
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema='public'
        AND table_name='contacts'
        AND column_name='debounce_validated_at'
    ) THEN
        RAISE NOTICE 'Adding debounce_validated_at column';
        ALTER TABLE contacts ADD COLUMN debounce_validated_at TIMESTAMP WITH TIME ZONE NULL;

        -- Add documentation comment
        COMMENT ON COLUMN contacts.debounce_validated_at IS 'Timestamp when email was successfully validated by DeBounce';

        RAISE NOTICE 'debounce_validated_at column added successfully';
    ELSE
        RAISE NOTICE 'debounce_validated_at column already exists';
    END IF;
EXCEPTION
    WHEN others THEN
        RAISE NOTICE 'Error adding debounce_validated_at column: %', SQLERRM;
END
$$;

-- Complete the transaction
COMMIT;
