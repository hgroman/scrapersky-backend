#!/usr/bin/env python3
"""
Update Comprehensive Document with File Numbers

This script updates the comprehensive file document with file numbers from the
Supabase database. It handles the specific format of the comprehensive document.
"""

import re
import os
import sys
from pathlib import Path

# File paths
DOC_PATH = "../Docs/Docs_10_Final_Audit/0-ScraperSky-Comprehensive-Files-By-Layer-And-Workflow.md"
FILE_DATA_PATH = "file_numbers.txt"


# Process the database file information
def create_file_lookup(file_data_path):
    """Create a lookup dictionary from file data."""
    file_lookup = {}

    with open(file_data_path, "r") as f:
        for line in f:
            # Parse line format: file_number, file_path, file_name
            parts = line.strip().split(",")
            if len(parts) >= 2:
                file_number = parts[0].strip()
                file_path = parts[1].strip()
                file_lookup[file_path] = file_number

    return file_lookup


# Update the comprehensive document
def update_document(doc_path, file_lookup):
    """Update the comprehensive document with file numbers."""
    # Read the document
    with open(doc_path, "r") as f:
        content = f.read()

    # Find all backtick-delimited Python file paths
    # Pattern for file path in backticks without a file number already present
    pattern = r"`(src/[^`]+\.py)`(?!\s*\[FILE:\d+\])"

    # Count updates
    count = 0

    # Function to replace matches
    def replace_match(match):
        nonlocal count
        file_path = match.group(1)
        if file_path in file_lookup:
            count += 1
            return f"`{file_path}` [FILE:{file_lookup[file_path]}]"
        return match.group(0)

    # Update content
    updated_content = re.sub(pattern, replace_match, content)

    # Write updated content back to file
    with open(doc_path, "w") as f:
        f.write(updated_content)

    return count


# Main process
if __name__ == "__main__":
    # Get current directory
    current_dir = Path(__file__).resolve().parent

    # Build full path to document
    doc_path = os.path.join(current_dir, DOC_PATH)

    # Adjust path if running from tools directory
    if not os.path.exists(doc_path):
        doc_path = os.path.join(
            current_dir.parent,
            "Docs/Docs_10_Final_Audit/0-ScraperSky-Comprehensive-Files-By-Layer-And-Workflow.md",
        )

    # Check if document exists
    if not os.path.exists(doc_path):
        print(f"Error: Document not found at {doc_path}")
        sys.exit(1)

    # Create file data if it doesn't exist
    if len(sys.argv) > 1:
        file_data_path = sys.argv[1]
    else:
        file_data_path = os.path.join(current_dir, FILE_DATA_PATH)

        # Create sample file data if it doesn't exist
        if not os.path.exists(file_data_path):
            print(f"Creating file data at {file_data_path}")
            with open(file_data_path, "w") as f:
                f.write("0001, src/main.py, main.py\n")
                f.write("0003, src/db/engine.py, engine.py\n")
                f.write("0004, src/db/session.py, session.py\n")
                f.write("# Add more file data here\n")
            print(f"Please update {file_data_path} with complete file data")
            sys.exit(0)

    # Create file lookup
    file_lookup = create_file_lookup(file_data_path)

    # Update document
    count = update_document(doc_path, file_lookup)

    print(f"Updated {count} file references in {doc_path}")
