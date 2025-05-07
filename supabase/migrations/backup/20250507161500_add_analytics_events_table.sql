-- Migration: Add analytics_events table for tracking user interactions
-- Created with Supabase MCP: 2025-05-07

-- Create analytics events table for tracking user interactions with the system
CREATE TABLE IF NOT EXISTS analytics_events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL,
  user_id UUID NOT NULL,
  event_type TEXT NOT NULL,
  event_data JSONB NOT NULL DEFAULT '{}',
  page_url TEXT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

  -- Add indexes for common query patterns
  CONSTRAINT fk_tenant_id FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE
);

-- Add comment to document table purpose
COMMENT ON TABLE analytics_events IS 'Tracks user interactions with the system for analytics purposes';

-- Create index for tenant_id and user_id since we'll frequently filter by these
CREATE INDEX idx_analytics_events_tenant_user ON analytics_events(tenant_id, user_id);

-- Create index for event_type lookups
CREATE INDEX idx_analytics_events_event_type ON analytics_events(event_type);

-- Enable Row Level Security for tenant isolation
ALTER TABLE analytics_events ENABLE ROW LEVEL SECURITY;

-- Create policy to restrict access by tenant_id
CREATE POLICY tenant_isolation_policy ON analytics_events
  USING (tenant_id = auth.jwt() ->> 'tenant_id');
