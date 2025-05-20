# ScraperSky File Audit System (Simple Supabase Implementation)

## Basic File Tracking Table

We'll create a single, straightforward Supabase table to track all files in the system:

```
file_audit
- id (auto-generated)
- file_number (unique sequential number)
- file_path (complete path from project root)
- file_name (extracted from path)
- layer (which architectural layer: Layer 1-7)
- status ('NOVEL', 'SHARED', 'SYSTEM')
- workflows (array of workflow IDs: WF1, WF2, etc.)
- audit_status ('NOT_STARTED', 'IN_PROGRESS', 'COMPLETED')
- audit_date
- audited_by
- technical_debt (description of any issues)
- jira_tickets (array of related tickets)
- notes
```

## Simple Instructions to Populate the Table

1. Get all Python files from the source code
2. For each file:
   - Assign a unique number
   - Determine which layer it belongs to
   - Check if it's used in multiple workflows to determine if it's SHARED or NOVEL
   - Add it to the table with audit_status = 'NOT_STARTED'

## Basic Queries

1. **Files needing audit**: Show all files where audit_status = 'NOT_STARTED'
2. **Files by layer**: Group files by layer and count them
3. **Files by workflow**: For a specific workflow, show all associated files
4. **Technical debt**: Show files with non-empty technical_debt field

That's it - a simple spreadsheet-like table to track our files and audit progress.
