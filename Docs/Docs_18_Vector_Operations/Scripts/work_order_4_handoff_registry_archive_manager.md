# Work Order Handoff: Registry Archive Manager

**Date:** 2025-06-08  
**Author:** Cascade AI  
**Status:** Completed  
**Priority:** Medium  

## Implementation Summary

The Registry Archive Manager script has been successfully implemented as requested. This script provides a focused tool for identifying and managing documents in the registry that no longer exist at their specified file paths.

**File Location:**
```
/Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/Docs/Docs_19_File-2-Vector-Registry-System/4-registry-archive-manager.py
```

## Key Features

The script provides the following capabilities:

1. **Scan for Missing Files** (`--scan`): Interactive mode that scans for files in the registry that no longer exist at their specified paths and allows the user to mark them as archived.

2. **List Missing Files** (`--list-missing`): Non-interactive mode that simply lists files that no longer exist without making any changes.

3. **Mark Files as Archived** (`--mark-archived <id>`): Marks a specific file as archived by its ID.

4. **Mark Files as Archived by Path** (`--mark-archived-by-path <path>`): Marks a specific file as archived by its file path.

5. **List Archived Files** (`--list-archived`): Lists all files currently marked as archived or obsolete.

## Design Patterns

The script follows the same design patterns as the existing registry management scripts:

1. Uses asyncpg for database connectivity with `statement_cache_size=0` for pgbouncer compatibility
2. Follows the same command-line interface pattern with argparse
3. Provides clear logging and feedback
4. Implements safety features like confirmation prompts for bulk operations

## Database Integration

The script works with the existing embedding status values in the document registry:
- "completed"
- "error_file_not_found"
- "obsolete"

It can add "archived" as a new status value if needed, and will set `should_be_vectorized = FALSE` for archived documents to ensure they are not included in future vectorization operations.

## Usage Examples

### Interactive Scan Mode

```bash
python 4-registry-archive-manager.py --scan
```

This will:
1. Scan the document registry for files that no longer exist
2. Present a list of these files with their IDs, titles, and current status
3. Provide options to:
   - Mark all files as archived
   - Mark specific files as archived (by selecting their numbers)
   - Exit without making changes

### List Missing Files

```bash
python 4-registry-archive-manager.py --list-missing
```

This will display a list of files in the registry that no longer exist at their specified paths, without making any changes.

### Mark a Specific File as Archived

```bash
python 4-registry-archive-manager.py --mark-archived 123
```

This will mark the document with ID 123 as archived.

### Mark a File as Archived by Path

```bash
python 4-registry-archive-manager.py --mark-archived-by-path /path/to/file.md
```

This will mark the document with the specified path as archived. If the exact path is not found, it will try to match by filename.

### List Archived Files

```bash
python 4-registry-archive-manager.py --list-archived
```

This will display a list of all files currently marked as archived or obsolete.

## Testing and Verification

The script has been tested with:
- Files that exist and don't exist
- Various file paths
- Interactive and non-interactive modes
- Database updates

## Next Steps

1. **Documentation Updates**:
   - Update `0-registry_librarian_persona.md` to include this new script's capabilities
   - Add a section about managing archived documents in the vector database workflow

2. **Integration with Vector Database Cleanup**:
   - Consider a future enhancement to remove archived documents from the vector database (`project_docs` table)
   - This would require a separate script or an additional feature in this script

3. **Potential Enhancements**:
   - Add a `--dry-run` option to simulate operations without making changes
   - Support for bulk operations via file input
   - Add pagination for large numbers of missing files

## Conclusion

The Registry Archive Manager script provides a clean, focused solution for managing documents that no longer exist at their specified paths. It maintains the separation of concerns principle by focusing solely on archive management, complementing the existing registry management scripts.
