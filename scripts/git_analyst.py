#!/usr/bin/env python3
import subprocess
import os
import re
from collections import defaultdict

def run_command(command):
    """Runs a command and returns its output."""
    result = subprocess.run(command, capture_output=True, text=True, shell=True)
    if result.returncode != 0:
        # Don't raise an error for grep, which returns 1 if no lines are selected
        if 'grep' not in command and 'No such file' not in result.stderr:
            print(f"Error running command: {command}\n{result.stderr}")
            return ""
    return result.stdout.strip()

def get_git_status():
    """Gets the git status using porcelain format for script parsing."""
    return run_command('git status --porcelain')

def classify_changes(status_output):
    """Classifies changes into categories."""
    changes = defaultdict(list)
    lines = status_output.split('\n')
    for line in lines:
        if not line:
            continue
        status = line[:2]
        path = line[3:]
        if status == ' D':
            changes['deleted'].append(path)
        elif status == ' M':
            changes['modified'].append(path)
        elif status == '??':
            changes['untracked'].append(path)
        elif status.startswith('R'):
            original, new = path.split(' -> ')
            changes['renamed'].append((original, new))
        elif status == ' A':
            changes['added'].append(path)

    return changes

def analyze_renames(deleted, untracked):
    """Analyzes deleted and untracked files to find renames for vectorization."""
    renames = []
    true_deletions = list(deleted)
    new_untracked = list(untracked)

    for d_file in deleted:
        d_basename = os.path.basename(d_file)
        # Check for v_ prefix renames
        if d_basename.endswith('.md'):
            possible_rename = f"v_{d_basename}"
            # Search for this possible rename in the untracked files, could be in a different path
            found_rename = None
            for u_file in new_untracked:
                if os.path.basename(u_file) == possible_rename:
                    found_rename = u_file
                    break
            
            if found_rename:
                renames.append((d_file, found_rename))
                if d_file in true_deletions:
                    true_deletions.remove(d_file)
                if found_rename in new_untracked:
                    new_untracked.remove(found_rename)

    return renames, true_deletions, new_untracked

def print_table(title, headers, rows):
    """Prints a markdown table."""
    print(f"### {title}")
    print(f"| {' | '.join(headers)} |")
    print(f"| {' | '.join(['---'] * len(headers))} |")
    for row in rows:
        print(f"| {' | '.join(row)} |")
    print("\n")

def main():
    """Main function to run the git analysis."""
    status_output = get_git_status()
    if not status_output:
        print("No changes detected in the repository.")
        return

    changes = classify_changes(status_output)
    
    deleted = changes.get('deleted', [])
    untracked = changes.get('untracked', [])
    modified = changes.get('modified', [])
    git_renamed = changes.get('renamed', [])

    vector_renames, true_deletions, remaining_untracked = analyze_renames(deleted, untracked)

    # Table 1: File Renames (Vectorization Queue)
    if vector_renames:
        rows = [("Dependency Traces", orig, new, "Renamed for vectorization") for orig, new in vector_renames]
        print_table("File Renames (Vectorization Queue)", ["Category", "Original File (Deleted)", "New File (Untracked)", "Status"], rows)

    # Table 2: Workflow Personas Reorganization (Git Renames)
    if git_renamed:
        rows = [(orig, new, "Moved & renamed") for orig, new in git_renamed]
        print_table("Workflow Personas Reorganization", ["Original File (Deleted)", "New Location/File (Untracked)", "Status"], rows)

    # Table 3: Truly New Files
    if remaining_untracked:
        rows = [("Subagent System", f, "New subagent functionality") for f in remaining_untracked]
        print_table("Truly New Files", ["Category", "File", "Purpose"], rows)

    # Table 4: Modified Files
    if modified:
        rows = [(f, "Code", "Service improvements") for f in modified]
        print_table("Modified Files (No Renames)", ["File", "Type", "Changes"], rows)

    # Table 5: Summary Statistics
    summary_rows = [
        ("**Files Renamed**", str(len(vector_renames)), "Vectorization queue preparation"),
        ("**Files Reorganized**", str(len(git_renamed)), "Workflow persona restructuring"),
        ("**Truly New Files**", str(len(remaining_untracked)), "Subagent system + research docs"),
        ("**Code Files Modified**", str(len(modified)), "Service layer improvements"),
        ("**Actual Deletions**", str(len(true_deletions)), "All \"deleted\" files have new versions" if not true_deletions else ""),
    ]
    print_table("Summary Statistics", ["Metric", "Count", "Notes"], summary_rows)

if __name__ == "__main__":
    main()
