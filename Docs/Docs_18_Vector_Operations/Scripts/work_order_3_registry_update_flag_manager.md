# Work Order: Registry Update Flag Manager Script

**Date:** 2025-06-08  
**Author:** Cascade AI  
**Status:** Proposed  
**Priority:** Medium  

## Purpose

Create a new script (`3-registry-update-flag-manager.py`) to manage the `needs_update` flag in the document registry. This script will allow users to easily mark documents for re-vectorization without manually running SQL commands.

## Background

The document registry system currently has two primary scripts:
1. `1-registry-directory-manager.py` - Manages approved directories
2. `2-registry-document-scanner.py` - Scans and updates the registry

With the addition of the `needs_update` field to the document registry schema (as planned in Work Order Part Two), we need a convenient way to mark documents as needing re-vectorization. This is particularly important when document content has changed but the filename remains the same, as the scanner won't automatically detect these changes.

## Requirements

The script should:

1. Allow marking individual documents as needing updates by title or path
2. Allow marking all documents in a specific directory as needing updates
3. Allow marking all documents matching a pattern as needing updates
4. Provide a way to view documents currently marked for updates
5. Provide a way to clear the update flag for specific documents
6. Follow the same command-line interface pattern as the existing scripts

## Implementation Details

### File Location
```
/Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/Docs/Docs_19_File-2-Vector-Registry-System/3-registry-update-flag-manager.py
```

### Command-Line Interface

The script should support the following commands:

```bash
# Mark a specific document for update
python 3-registry-update-flag-manager.py --mark-for-update /path/to/document.md

# Mark all documents in a directory for update
python 3-registry-update-flag-manager.py --mark-directory-for-update /path/to/directory

# Mark documents matching a pattern for update
python 3-registry-update-flag-manager.py --mark-pattern-for-update "pattern*"

# List documents currently marked for update
python 3-registry-update-flag-manager.py --list-updates

# Clear update flag for a specific document
python 3-registry-update-flag-manager.py --clear-update /path/to/document.md

# Clear update flag for all documents
python 3-registry-update-flag-manager.py --clear-all-updates
```

### Database Interaction

The script should:

1. Connect to the database using the same connection method as the existing scripts
2. Update the `needs_update` field in the `document_registry` table
3. Handle errors gracefully and provide clear feedback

### Dependencies

- Python 3.x
- asyncpg
- dotenv (for loading environment variables)
- argparse (for command-line argument parsing)

## Implementation Plan

1. Create the script with basic structure and command-line argument parsing
2. Implement database connection and query functions
3. Implement each command functionality
4. Add error handling and logging
5. Test with various scenarios
6. Update documentation to include the new script

## Risks and Mitigations

**Risk**: The `needs_update` column may not exist if Work Order Part Two hasn't been implemented.
**Mitigation**: The script should check for the column's existence and create it if missing (with appropriate permissions).

**Risk**: Marking many documents for update could overwhelm the vectorization process.
**Mitigation**: Add a confirmation prompt when marking more than 10 documents at once.

## Testing Plan

1. Test each command with valid inputs
2. Test error handling with invalid inputs
3. Verify database updates are correctly applied
4. Test integration with the existing document registry workflow

## Documentation Updates

After implementation, update:
1. `0-registry_librarian_persona.md` to include the new script's capabilities
2. Add examples to the script's help text
3. Update any relevant workflow documentation

## Approval

This work order requires approval before implementation.

- [ ] Approved by: ________________
- [ ] Date: ________________
