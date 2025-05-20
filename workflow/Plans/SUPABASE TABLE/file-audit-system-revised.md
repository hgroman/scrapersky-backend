# ScraperSky File Audit Database (Supabase Implementation)

## Direct Implementation Plan

We already have a complete inventory of files in "ScraperSky Files by Layer and Workflow.md" with all necessary classifications. We'll simply transfer this existing data into a Supabase table.

## Basic Database Table

```
file_audit
- id (auto-generated)
- file_number (sequential number)
- file_path (as documented in existing mappings)
- file_name (extracted from path)
- layer (Layer 1-7, already identified in mappings)
- status ('NOVEL', 'SHARED', 'SYSTEM' - already identified in mappings)
- workflows (array of workflow IDs that use this file - already identified in mappings)
- technical_debt (from "Technical Issues by Workflow" section)
- jira_tickets (already linked in existing documentation)
- compliance_status ('COMPLIANT', 'NON_COMPLIANT', 'PARTIALLY_COMPLIANT')
- audit_completed (boolean)
```

## Implementation Steps

1. Tell MCP to create the above table in Supabase

2. Tell MCP to directly extract the file data from "ScraperSky Files by Layer and Workflow.md" and insert it into the table:
   - Parse the documented files from each layer and workflow
   - Extract status ([NOVEL]/[SHARED]) from the mapping
   - Extract layer based on the section headers
   - Extract workflows based on the column headers
   - Extract technical debt and Jira tickets from the "Technical Issues by Workflow" section
   - Set audit_completed to false initially

3. Tell MCP to add these basic queries:
   - Show files by layer
   - Show files by workflow
   - Show files with technical debt by severity
   - Show files that need audit

That's it. No complicated process - just transfer the existing data we already have into a queryable database.
