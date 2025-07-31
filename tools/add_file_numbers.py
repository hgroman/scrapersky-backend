#!/usr/bin/env python3
"""
Add File Numbers Script

This script updates Markdown documentation with file numbers from the Supabase file_audit table.
It's specifically designed to handle the comprehensive files document format.

Usage:
    python add_file_numbers.py <target_doc>
"""

import os
import sys
import re
import json
import subprocess

# Target document
if len(sys.argv) < 2:
    print("Usage: python add_file_numbers.py <target_doc>")
    sys.exit(1)

TARGET_DOC = sys.argv[1]
PROJECT_ID = "ddfldwzhdhhzhxywqnyz"


# Get file information from database
def get_db_files():
    """Get file data from the Supabase database using MCP."""
    # Create temporary file for output
    temp_file = "temp_file_data.json"

    # Use MCP command to get file data
    cmd = f'windsurf mcp execute supabase-mcp-server execute_sql --project_id {PROJECT_ID} --query "SELECT file_number, file_path, file_name FROM file_audit ORDER BY file_number;" > {temp_file}'

    # Run the command
    os.system(cmd)

    # Read result from temporary file
    try:
        with open(temp_file, "r") as f:
            data = json.load(f)
        # Create a lookup dictionary by file path
        file_lookup = {f["file_path"]: f["file_number"] for f in data}
        return file_lookup
    except Exception as e:
        print(f"Error loading file data: {e}")
        return {}
    finally:
        # Clean up
        if os.path.exists(temp_file):
            os.remove(temp_file)


# Function to update the document
def update_document(doc_path, file_lookup):
    """Update document with file numbers."""
    print(f"Updating document: {doc_path}")

    # Read the document
    with open(doc_path, "r") as f:
        content = f.read()

    # Track stats
    files_found = 0
    files_updated = 0

    # Look for file paths using regex patterns
    # Specifically targeting src/x/y.py formats in backticks
    pattern = r"`(src/[^`]+\.py)`"

    # Function to replace each match
    def replace_match(match):
        nonlocal files_found, files_updated
        file_path = match.group(1)
        files_found += 1

        # If path already has a file number, don't replace
        if re.search(r"\[FILE:\d+\]", match.group(0)):
            return match.group(0)

        # Check if this file path is in our lookup
        if file_path in file_lookup:
            file_number = file_lookup[file_path]
            files_updated += 1
            return f"`{file_path}` [FILE:{file_number}]"
        else:
            # File not found in database
            return match.group(0)

    # Replace file references in the content
    updated_content = re.sub(pattern, replace_match, content)

    # Write the updated content back
    if files_updated > 0:
        with open(doc_path, "w") as f:
            f.write(updated_content)
        print(f"Updated {files_updated} file references out of {files_found} found")
    else:
        print(f"No file references needed updating (found {files_found})")


# Main execution
print("Getting file data from database...")
file_lookup = get_db_files()
print(f"Found {len(file_lookup)} files in database")

# Update the document
if os.path.exists(TARGET_DOC):
    update_document(TARGET_DOC, file_lookup)
else:
    print(f"Error: Document not found: {TARGET_DOC}")
    sys.exit(1)
