-- Create a test table to validate MCP migration workflow
CREATE TABLE IF NOT EXISTS mcp_test_table (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL,
  name TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Add comment for documentation
COMMENT ON TABLE mcp_test_table IS 'Test table created to validate MCP migration workflow';
