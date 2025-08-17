# WORK ORDER: Test MCP Database Access for Librarian Agent

**Date Created**: 2025-08-14  
**Priority**: HIGH  
**Requestor**: System Administrator  
**Assignee**: Next Available AI Agent  
**Location**: `/personas_layers/WORK_ORDER_Test_MCP_Database_Access.md`

## Executive Summary

The librarian agent has been configured with MCP database tool access (`mcp__supabase-mcp-server__execute_sql`) but reports the tool is unavailable. We need to verify whether agents can successfully inherit and use MCP tools from the parent Claude instance.

## Background

During Test Sentinel v1.3 → v1.5 version correction, we discovered the librarian agent lacked database access. We added the MCP tool to its configuration:

```yaml
tools: Read, Write, Edit, Bash, Grep, Glob, mcp__supabase-mcp-server__execute_sql
```

However, when tested, the agent reports: "The mcp__supabase-mcp-server__execute_sql tool you mentioned is not available in my current tool set."

## Scope of Work

### 1. Test Direct MCP Tool Access
Execute the following SQL query using the MCP tool to verify it works in the parent context:

```sql
SELECT 
    id, 
    title, 
    embedding_status, 
    last_embedded_at
FROM document_registry 
WHERE title LIKE '%test_sentinel%' 
ORDER BY id DESC 
LIMIT 5;
```

**Tool Parameters**:
- Tool: `mcp__supabase-mcp-server__execute_sql`
- Project ID: `ddfldwzhdhhzhxywqnyz`

### 2. Test Librarian Agent MCP Access
Invoke the librarian agent and request it to:
1. Execute the same SQL query above
2. Report whether the MCP tool is available
3. List all tools it has access to

### 3. Test Tool Inheritance Strategies

#### Strategy A: Explicit Tool List (Current)
Test with current configuration where tools are explicitly listed.

#### Strategy B: Inherit All Tools
1. Create a temporary test agent without explicit tools:
```yaml
---
name: test-db-agent
description: Test agent for verifying MCP database tool inheritance
color: blue
# No tools specified - should inherit all
---

I am a test agent for database access verification.
```

2. Test if this agent can access `mcp__supabase-mcp-server__execute_sql`

#### Strategy C: Minimal Tool Set
Test with only the MCP tool specified:
```yaml
tools: mcp__supabase-mcp-server__execute_sql
```

### 4. Document Findings

Create a report documenting:
- Which configuration allows MCP tool access
- Whether agents can use MCP tools at all
- Recommended configuration for the librarian agent
- Any limitations discovered

## Expected Deliverables

1. **Test Results Matrix**:
   | Configuration | MCP Tool Available | Can Execute SQL | Notes |
   |--------------|-------------------|-----------------|-------|
   | Explicit list with MCP | Yes/No | Yes/No | ... |
   | Inherit all (no tools line) | Yes/No | Yes/No | ... |
   | Only MCP tool | Yes/No | Yes/No | ... |

2. **Recommended Configuration**: Final YAML frontmatter for librarian agent

3. **Documentation Update**: If needed, update `/Docs/Docs_29_Sub-Agents-Journal/` with findings

## Success Criteria

- [ ] Determine if agents can use MCP tools
- [ ] Find optimal configuration for database access
- [ ] Update librarian agent with working configuration
- [ ] Verify Test Sentinel v1.5 status via agent SQL query

## Test Data for Verification

The following should be confirmed via direct SQL:
- Test Sentinel v1.5 (ID: 427) - Status: active
- Test Sentinel v1.3 (ID: 426) - Status: archived
- Both in `document_registry` table

## Notes

- The parent Claude instance HAS access to the MCP tool (verified)
- Python scripts work as fallback but direct SQL would be preferred
- This affects all agents needing database access, not just librarian

## Resources

- Librarian agent: `.claude/agents/librarian.md`
- Source personas requiring database:
  - `Docs/Docs_18_Vector_Operations/knowledge_librarian_persona_v2.md`
  - `Docs/Docs_19_File-2-Vector-Registry-System/0-registry_librarian_persona.md`
- MCP Documentation: Check Anthropic's MCP tool inheritance rules

---

**EXECUTE THIS WORK ORDER IMMEDIATELY** to resolve database access for the librarian agent and establish best practices for MCP tool configuration in Claude Code agents.