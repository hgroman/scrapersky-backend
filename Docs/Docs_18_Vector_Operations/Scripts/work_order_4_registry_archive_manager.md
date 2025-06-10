# Work Order: Registry Archive Manager Script

**Date:** 2025-06-08  
**Author:** Cascade AI  
**Status:** Proposed  
**Priority:** Medium  

## Purpose

Create a new script (`4-registry-archive-manager.py`) to identify and manage documents in the registry that no longer exist at their specified file paths. This script will allow users to review missing files and mark them as "archived" in the document registry without manually running SQL commands.

## Background

The document registry system currently has three primary scripts:
1. `1-registry-directory-manager.py` - Manages approved directories
2. `2-registry-document-scanner.py` - Scans and updates the registry
3. `3-registry-update-flag-manager.py` - Manages the `needs_update` flag

As the document registry evolves over time, some documents may be moved, renamed, or deleted from the filesystem while still having entries in the registry. Currently, there is no convenient way to identify these missing files or update their status in the registry. This script will fill that gap by providing a dedicated tool for managing archived documents.

## Requirements

The script should:

1. Scan the document registry for files that no longer exist at their specified paths
2. Present a list of these files for review
3. Allow the user to mark specific files as "archived" in the registry
4. Update the document registry with an "archived" status
5. Provide a non-interactive mode to just list missing files without updating
6. Follow the same command-line interface pattern as the existing scripts

## Implementation Details

### File Location
```
/Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/Docs/Docs_19_File-2-Vector-Registry-System/4-registry-archive-manager.py
```

### Command-Line Interface

The script should support the following commands:

```bash
# Scan for missing files and present them for review in an interactive mode
python 4-registry-archive-manager.py --scan

# Non-interactive mode to just list missing files without updating
python 4-registry-archive-manager.py --list-missing

# Mark specific files as archived (after reviewing)
python 4-registry-archive-manager.py --mark-archived <file_id>

# Mark specific files as archived by path
python 4-registry-archive-manager.py --mark-archived-by-path /path/to/file.md

# List all currently archived documents
python 4-registry-archive-manager.py --list-archived
```

### Database Schema Changes

The script will need to work with an enhanced `embedding_status` field in the document registry that includes an "archived" status. If this status doesn't exist, the script should be able to handle it appropriately.

```sql
-- Check if we need to update the embedding_status type
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'embedding_status_enum' AND typelem <> 0 AND typlen = -1 AND typcategory = 'E' AND typtype = 'e' AND typisdefined = true) THEN
        CREATE TYPE embedding_status_enum AS ENUM ('pending', 'completed', 'failed', 'archived');
        ALTER TABLE document_registry ALTER COLUMN embedding_status TYPE embedding_status_enum USING embedding_status::embedding_status_enum;
    ELSE
        -- Check if 'archived' value exists in the enum
        IF NOT EXISTS (SELECT 1 FROM pg_enum WHERE enumtypid = (SELECT oid FROM pg_type WHERE typname = 'embedding_status_enum') AND enumlabel = 'archived') THEN
            ALTER TYPE embedding_status_enum ADD VALUE 'archived';
        END IF;
    END IF;
END
$$;
```

### Database Interaction

The script should:

1. Connect to the database using the same connection method as the existing scripts
2. Query the document registry for all entries
3. Check if each file exists at its specified path
4. Allow updating the `embedding_status` field to "archived" for missing files
5. Handle errors gracefully and provide clear feedback

### Dependencies

- Python 3.x
- asyncpg
- dotenv (for loading environment variables)
- argparse (for command-line argument parsing)
- os.path (for file existence checking)

## Implementation Plan

1. Create the script with basic structure and command-line argument parsing
2. Implement database connection and query functions
3. Implement file existence checking
4. Create interactive mode for reviewing and marking files
5. Implement non-interactive commands
6. Add error handling and logging
7. Test with various scenarios
8. Update documentation to include the new script

## Risks and Mitigations

**Risk**: The `embedding_status` field may not support an "archived" status.
**Mitigation**: The script should check the current enum values and add "archived" if needed, with appropriate permissions.

**Risk**: Files might be temporarily unavailable due to network issues or permissions.
**Mitigation**: Add a confirmation step before marking files as archived and provide clear warnings about potential false positives.

**Risk**: Large numbers of missing files could make interactive review cumbersome.
**Mitigation**: Add pagination to the interactive mode and provide batch operations for efficiency.

## Testing Plan

1. Test with files that exist and don't exist
2. Test with various file paths (absolute, relative)
3. Test interactive and non-interactive modes
4. Verify database updates are correctly applied
5. Test integration with the existing document registry workflow

## Documentation Updates

After implementation, update:
1. `0-registry_librarian_persona.md` to include the new script's capabilities
2. Add examples to the script's help text
3. Update any relevant workflow documentation

## Approval

This work order requires approval before implementation.

- [ ] Approved by: ________________
- [ ] Date: ________________
