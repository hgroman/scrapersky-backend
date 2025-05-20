# File Audit Cheat Sheet

## Quick Start

```bash
# Run the file discovery script to check for orphans and phantoms
python tools/file_discovery.py
```

## Common Audit Scenarios

### 1. Finding Orphaned Files

Orphaned files exist in the filesystem but not in the database. To investigate:

```bash
# Check file contents
cat <orphaned_file_path>

# Search for references
grep -r "<filename>" .
```

### 2. Finding Phantom Files

Phantom files exist in the database but not in the filesystem. To investigate:

```bash
# Search for references in documentation
grep -r "<filename>" ./Docs

# Check workflow documentation
grep -r "<filename>" ./workflow
```

### 3. Verifying File Registration

To verify a file's registration status:

1. Check if it exists in filesystem: `ls <file_path>`
2. Check if it exists in database: `python tools/file_discovery.py`
3. Search for references: `grep -r "<filename>" .`

## Common Patterns

### Orphaned Files

- Usually new files that haven't been registered
- May be test files or temporary files
- Could be moved files that weren't re-registered

### Phantom Files

- Often planned but not yet implemented
- May be referenced in documentation
- Usually part of a workflow that's in development

## Resolution Steps

### For Orphaned Files:

1. Review file contents to understand purpose
2. Determine appropriate layer and workflow
3. Register in database with correct status (NOVEL/SHARED/SYSTEM)
4. Update documentation if needed

### For Phantom Files:

1. Check documentation for implementation plans
2. Verify if file is still needed
3. Either:
   - Create the file if implementation is needed
   - Remove from database if no longer needed
4. Update documentation accordingly

## Best Practices

1. **Regular Audits**

   - Run `file_discovery.py` weekly
   - Document any findings
   - Resolve issues promptly

2. **Documentation**

   - Keep workflow documentation up to date
   - Document planned files clearly
   - Use consistent naming conventions

3. **File Registration**

   - Register new files immediately
   - Include all required metadata
   - Verify registration with `file_discovery.py`

4. **Cleanup**
   - Remove obsolete files from both filesystem and database
   - Update documentation when files are removed
   - Keep audit trail of changes

## Common Issues and Solutions

1. **File Not Found in Database**

   - Check if file is in correct location
   - Verify file name matches exactly
   - Check for case sensitivity issues

2. **Phantom File References**

   - Check workflow documentation
   - Verify implementation status
   - Update documentation if plans change

3. **Incorrect Layer Assignment**
   - Review file's dependencies
   - Check workflow documentation
   - Update database if needed

## Tools Reference

### file_discovery.py

```bash
# Basic usage
python tools/file_discovery.py

# Output includes:
# - Total files in database
# - Total files in filesystem
# - List of orphaned files
# - List of phantom files
```

### grep

```bash
# Search for file references
grep -r "<filename>" .

# Search in specific directories
grep -r "<filename>" ./src
grep -r "<filename>" ./Docs
```

## Notes

- Always run audits in a clean workspace
- Document all findings and resolutions
- Keep this cheat sheet updated with new patterns and solutions
