-- Create enum for JIRA issue types
CREATE TYPE jira_issue_type AS ENUM (
    'Task',
    'Bug',
    'Epic',
    'Story',
    'Sub-task'
);

-- Create enum for JIRA status
CREATE TYPE jira_status AS ENUM (
    'To Do',
    'In Progress',
    'Done',
    'Blocked',
    'Review'
);

-- Create JIRA sync table
CREATE TABLE jira_sync (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    jira_key TEXT NOT NULL UNIQUE,
    issue_type jira_issue_type NOT NULL,
    summary TEXT NOT NULL,
    description TEXT,
    status jira_status NOT NULL,
    assignee TEXT,
    reporter TEXT,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    due_date TIMESTAMPTZ,
    priority TEXT,
    labels TEXT[],
    components TEXT[],
    epic_link TEXT,
    parent_issue TEXT,
    local_notes TEXT,
    local_metadata JSONB,
    last_synced_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at_utc TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at_utc TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create indexes
CREATE INDEX idx_jira_sync_jira_key ON jira_sync(jira_key);
CREATE INDEX idx_jira_sync_status ON jira_sync(status);
CREATE INDEX idx_jira_sync_assignee ON jira_sync(assignee);
CREATE INDEX idx_jira_sync_epic_link ON jira_sync(epic_link);

-- Add RLS policies
ALTER TABLE jira_sync ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Enable read access for authenticated users" ON jira_sync
    FOR SELECT
    TO authenticated
    USING (true);

CREATE POLICY "Enable insert for service role" ON jira_sync
    FOR INSERT
    TO service_role
    WITH CHECK (true);

CREATE POLICY "Enable update for service role" ON jira_sync
    FOR UPDATE
    TO service_role
    USING (true);

-- Create function to update updated_at_utc
CREATE OR REPLACE FUNCTION update_updated_at_utc()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at_utc = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger for updated_at_utc
CREATE TRIGGER update_jira_sync_updated_at_utc
    BEFORE UPDATE ON jira_sync
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_utc();
