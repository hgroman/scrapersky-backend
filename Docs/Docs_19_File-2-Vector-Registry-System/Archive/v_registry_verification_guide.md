# ScraperSky Vector Document Registry: Verification & Testing Guide

**Purpose:**  
This document provides a comprehensive guide for validating the controlled document registry and directory approval system. It ensures that all components work correctly for systematic, large-scale document management.

## System Overview

The document registry system provides controlled scanning and vectorization through:

1. **Approved Directory Tracking**: Only directories explicitly approved are scanned
2. **Controlled Document Marking**: Only files with `v_` prefix are considered for vectorization
3. **Systematic Workflow**: Conversational, step-by-step approach to document management

## Environment Setup

Before beginning verification:

```bash
# Ensure DATABASE_URL is set
echo $DATABASE_URL

# If not set, load it from .env if available
source .env
```

## 1. Initial System Verification

### Database Schema

First, ensure the database schema is correctly deployed:

```bash
# Apply the migration script if needed
psql $DATABASE_URL -f Docs/Docs_18_Vector_Operations/Scripts/sql/approved_directories_migration.sql
```

### Run Setup Script

```bash
python Docs/Docs_18_Vector_Operations/Scripts/setup_registry_system.py
```

**Expected Output:**
- Confirmation that the approval table was created
- Four directories approved: 
  - Docs/Docs_6_Architecture_and_Status
  - Docs/Docs_18_Vector_Operations
  - Docs/Docs_18_Vector_Operations/Documentation
  - Docs/Docs_1_AI_GUIDES

### Verify Approved Directories

```bash
python Docs/Docs_18_Vector_Operations/Scripts/directory_approval.py --list-approved
```

**Expected Output:**
- All four directories listed with ACTIVE status
- Each should have a description and approved_by field

## 2. Directory & Document Operations

### List Candidates in Architecture Directory

```bash
python Docs/Docs_18_Vector_Operations/Scripts/directory_approval.py --list-candidates "Docs/Docs_6_Architecture_and_Status"
```

**Expected Output:**
- List of markdown files in the directory without `v_` prefix
- Should show filename, path, and whether it's marked

### Mark Files for Vectorization

```bash
# Test with an actual file from the directory
python Docs/Docs_18_Vector_Operations/Scripts/manage_document_registry.py --mark "Docs/Docs_6_Architecture_and_Status/filename.md"
```

**Expected Output:**
- File renamed to `v_filename.md`
- Confirmation message

### Directory Unapproval Test

```bash
# Unapprove a directory
python Docs/Docs_18_Vector_Operations/Scripts/directory_approval.py --unapprove "Docs/Docs_6_Architecture_and_Status"

# Verify it's no longer listed as ACTIVE
python Docs/Docs_18_Vector_Operations/Scripts/directory_approval.py --list-approved

# Try to scan with unapproved directory
python Docs/Docs_18_Vector_Operations/Scripts/manage_document_registry.py --scan --approved-only

# Re-approve the directory
python Docs/Docs_18_Vector_Operations/Scripts/directory_approval.py --approve "Docs/Docs_6_Architecture_and_Status"
```

**Expected Output:**
- Directory should no longer appear as ACTIVE after unapproval
- Scan should skip the unapproved directory
- Directory should appear as ACTIVE again after re-approval

## 3. Registry Management

### Scan Approved Directories

```bash
# Scan only approved directories
python Docs/Docs_18_Vector_Operations/Scripts/manage_document_registry.py --scan --approved-only
```

**Expected Output:**
- Only files with `v_` prefix in approved directories should be added to registry
- Confirmation of directories scanned
- Count of documents found/added

### Generate Status Report

```bash
python Docs/Docs_18_Vector_Operations/Scripts/manage_document_registry.py --report
```

**Expected Output:**
- Status report showing approved directories
- Documents pending vectorization (files with `v_` prefix)
- Documents already vectorized (if any)

## 4. Edge Case Testing

### Empty Directory Test

```bash
# Create an empty test directory
mkdir -p test_empty_dir

# Try to approve it
python Docs/Docs_18_Vector_Operations/Scripts/directory_approval.py --approve "test_empty_dir"

# List candidates
python Docs/Docs_18_Vector_Operations/Scripts/directory_approval.py --list-candidates "test_empty_dir"

# Scan with approved-only
python Docs/Docs_18_Vector_Operations/Scripts/manage_document_registry.py --scan --approved-only

# Clean up
rm -rf test_empty_dir
```

**Expected Output:**
- Directory should be approved successfully
- List candidates should report empty or no files found
- Scan should handle empty directory gracefully

### Invalid Directory Test

```bash
# Try to approve a non-existent directory
python Docs/Docs_18_Vector_Operations/Scripts/directory_approval.py --approve "non_existent_dir"
```

**Expected Output:**
- Error message indicating directory does not exist
- System should not crash

### Duplicate Action Test

```bash
# Try to mark an already marked file
python Docs/Docs_18_Vector_Operations/Scripts/manage_document_registry.py --mark "Docs/Docs_6_Architecture_and_Status/v_filename.md"
```

**Expected Output:**
- Warning or message stating file is already marked
- No duplicate `v_v_` prefix should be added

## 5. Database Function Testing

### Test SQL Functions (Optional)

```bash
# If you have access to run SQL directly:
psql $DATABASE_URL -c "SELECT * FROM get_directory_stats();"
```

**Expected Output:**
- List of directories with document counts
- Total, marked, and pending document counts for each directory

## 6. Comprehensive System Test

Test the entire workflow as it would be used in a typical conversation:

1. Approve a new directory (if any exist that aren't approved yet)
2. List candidates in that directory
3. Mark selected files with `v_` prefix
4. Scan approved directories
5. Generate a status report
6. Verify files appear correctly in the report

## 7. Performance Testing

For large directories (if available):

```bash
# Time how long it takes to scan a large directory
time python Docs/Docs_18_Vector_Operations/Scripts/manage_document_registry.py --scan --approved-only --directory "large_directory_path"
```

**Expected Output:**
- Scan completes in reasonable time
- No memory errors or crashes

## 8. Final Checklist

- [ ] All specified directories are approved and active
- [ ] File marking adds the `v_` prefix correctly
- [ ] Only approved directories are scanned
- [ ] Only marked files are considered for vectorization
- [ ] Unapproving a directory excludes it from scanning
- [ ] Reports are accurate and reflect the current state
- [ ] All edge cases handled gracefully without crashes
- [ ] The conversational workflow is effective and intuitive

## Test Results Documentation

Document any issues, bugs, or suggestions in this section:

1. Issue: ________________
   - Description:
   - Reproduction steps:
   - Suggested fix:

2. Enhancement suggestion: ________________
   - Current behavior:
   - Proposed improvement:
   - Benefit:

---

**This verification is complete when all tests pass and any identified issues have been addressed.**
