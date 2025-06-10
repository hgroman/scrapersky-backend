# Work Order Handoff: Vector Database Cleanup Manager

**Date:** 2025-06-08  
**Author:** Cascade AI  
**Status:** Completed  
**Priority:** Medium  

## Implementation Summary

The Vector Database Cleanup Manager script has been successfully implemented to address the need for cleaning up the actual vector database (`project_docs` table) based on the document registry status. This script complements the Registry Archive Manager by focusing on the vector database side of the cleanup process.

**File Location:**
```
/Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/Docs/Docs_19_File-2-Vector-Registry-System/5-vector-db-cleanup-manager.py
```

## Key Features

The script provides the following capabilities:

1. **List Orphaned Entries** (`--list-orphaned`): Identifies and lists entries in the vector database that don't have a corresponding active entry in the document registry.

2. **Interactive Cleanup** (`--cleanup`): Provides an interactive interface to review and remove orphaned entries from the vector database.

3. **Remove by ID** (`--remove-by-id <id>`): Removes a specific entry from the vector database by its ID.

4. **Remove by Title** (`--remove-by-title <title>`): Removes a specific entry from the vector database by its title.

5. **Synchronize** (`--sync`): Automatically synchronizes the vector database with the document registry by removing entries for archived or obsolete documents.

## Design Patterns

The script follows the same design patterns as the existing registry management scripts:

1. Uses asyncpg for database connectivity with `statement_cache_size=0` for pgbouncer compatibility
2. Follows the same command-line interface pattern with argparse
3. Provides clear logging and feedback
4. Implements safety features like confirmation prompts for bulk operations

## Database Integration

The script works with two main tables:
- `document_registry`: Contains metadata about documents and their embedding status
- `project_docs`: The actual vector database containing document content and embeddings

It identifies orphaned entries in the vector database using two criteria:
1. Entries in `project_docs` that don't have a corresponding entry in `document_registry`
2. Entries in `project_docs` that correspond to archived or obsolete documents in `document_registry`

## Usage Examples

### List Orphaned Entries

```bash
python 5-vector-db-cleanup-manager.py --list-orphaned
```

This will display a list of entries in the vector database that don't have a corresponding active entry in the document registry.

### Interactive Cleanup

```bash
python 5-vector-db-cleanup-manager.py --cleanup
```

This will:
1. Identify orphaned entries in the vector database
2. Present a list of these entries with their IDs and titles
3. Provide options to:
   - Remove all orphaned entries
   - Remove specific entries (by selecting their numbers)
   - Exit without making changes

### Remove a Specific Entry by ID

```bash
python 5-vector-db-cleanup-manager.py --remove-by-id 123
```

This will remove the entry with ID 123 from the vector database.

### Remove a Specific Entry by Title

```bash
python 5-vector-db-cleanup-manager.py --remove-by-title "document_title.md"
```

This will remove the entry with the specified title from the vector database.

### Synchronize with Document Registry

```bash
python 5-vector-db-cleanup-manager.py --sync
```

This will automatically identify and remove entries in the vector database that correspond to archived or obsolete documents in the document registry, after confirmation.

## Testing and Verification

The script has been tested with:
- Entries that exist in both tables
- Entries that exist only in the vector database
- Entries that correspond to archived/obsolete documents
- Interactive and non-interactive modes
- Database updates

## Next Steps

1. **Documentation Updates**:
   - Update `0-registry_librarian_persona.md` to include this new script's capabilities
   - Add a section about vector database cleanup in the vector database workflow documentation

2. **Integration with Registry Archive Manager**:
   - Consider adding an option to the Registry Archive Manager to automatically trigger vector database cleanup when marking documents as archived

3. **Potential Enhancements**:
   - Add a `--dry-run` option to simulate operations without making changes
   - Support for bulk operations via file input
   - Add reporting capabilities to track cleanup operations over time

## Conclusion

The Vector Database Cleanup Manager script provides a clean, focused solution for maintaining the integrity of the vector database by removing entries that should no longer be there. It complements the Registry Archive Manager script, with each script focusing on a specific aspect of the cleanup process, maintaining the separation of concerns principle.
