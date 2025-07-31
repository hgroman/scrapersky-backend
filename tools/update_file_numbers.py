#!/usr/bin/env python3
"""
Update File Numbers Script

This script retrieves file information from the Supabase file_audit table
and updates local documentation files with the proper file numbers.

Usage:
    python update_file_numbers.py [document_path]

Example:
    python update_file_numbers.py ../Docs/Docs_10_Final_Audit/Layer-1.2-Models_Enums_Audit-Plan.md
"""

import os
import sys
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
import json

# Project constants
PROJECT_ID = "ddfldwzhdhhzhxywqnyz"
PROJECT_ROOT = Path(__file__).resolve().parent.parent


# Function to use for direct MCP SQL execution
def get_files_from_db_direct(layer: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Get files from the database using direct MCP function calls.

    Args:
        layer: Optional layer number to filter by

    Returns:
        List of file records with file_number, file_path, etc.
    """
    import os
    import tempfile
    import subprocess

    # Build query based on whether we want all files or just a specific layer
    if layer is not None:
        query = f"SELECT file_number, file_path, file_name, layer_number, layer_name, status FROM file_audit WHERE layer_number = {layer} ORDER BY file_number;"
    else:
        query = "SELECT file_number, file_path, file_name, layer_number, layer_name, status FROM file_audit ORDER BY layer_number, file_number;"

    # Use a temporary file to store the MCP output
    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as tmp:
        tmp_path = tmp.name

    # Execute the MCP command and save output to temp file
    cmd = f'windsurf mcp execute supabase-mcp-server execute_sql --project_id {PROJECT_ID} --query "{query}" > {tmp_path}'
    os.system(cmd)

    # Read the results
    try:
        with open(tmp_path, "r") as f:
            content = f.read()
            data = json.loads(content)
            return data
    except Exception as e:
        print(f"Error fetching data: {e}")
        return []
    finally:
        # Clean up temp file
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


def update_document(doc_path: str, files: List[Dict[str, Any]]) -> None:
    """
    Update a document with file numbers.

    Args:
        doc_path: Path to the document to update
        files: List of file records from the database
    """
    # Read the document
    with open(doc_path, "r") as f:
        content = f.read()

    # Create a lookup of file paths to file numbers
    file_lookup = {f["file_path"]: f["file_number"] for f in files}

    # Track changes
    changes_made = 0

    # Look for file paths in the document and add file numbers
    for file_path, file_number in file_lookup.items():
        # Look for the file path without a file number reference
        base_name = os.path.basename(file_path)

        # Skip if file is already referenced with its number
        if f"[FILE:{file_number}]" in content:
            continue

        # Pattern: the filename without a file number reference
        pattern = rf"`{re.escape(base_name)}`(?!\s*\[FILE:)"
        replacement = f"`{base_name}` [FILE:{file_number}]"

        if re.search(pattern, content):
            content = re.sub(pattern, replacement, content)
            changes_made += 1

    # Write the updated content back
    if changes_made > 0:
        with open(doc_path, "w") as f:
            f.write(content)
        print(f"Updated {doc_path} with {changes_made} file number references")
    else:
        print(f"No changes needed in {doc_path}")


def main():
    # Get all files from the database
    print("Retrieving files from database...")
    all_files = get_files_from_db_direct()
    print(f"Found {len(all_files)} files in database")

    # If a document path is provided, update that document
    if len(sys.argv) > 1:
        doc_path = sys.argv[1]
        if os.path.exists(doc_path):
            print(f"Updating document: {doc_path}")
            update_document(doc_path, all_files)
        else:
            print(f"Document not found: {doc_path}")
            sys.exit(1)
    else:
        # Print file information as a reference
        print("\nFile Number Reference:")
        print("-" * 80)
        print(f"{'Number':<8}{'Layer':<8}{'Path':<50}{'Status':<10}")
        print("-" * 80)

        for file in all_files:
            print(
                f"{file['file_number']:<8}{str(file['layer_number']):<8}{file['file_path']:<50}{file['status']:<10}"
            )


if __name__ == "__main__":
    main()
