#!/usr/bin/env python3
"""
Orphaned File Analysis - Run Script
Run both standard and enhanced analysis and store results in one place
"""

import os
import shutil
import subprocess

# Use the directory of this script
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(PROJECT_DIR)


def run_command(cmd):
    """Run a shell command and print output"""
    print(f"Running: {cmd}")
    process = subprocess.run(
        cmd, shell=True, cwd=ROOT_DIR, capture_output=True, text=True
    )
    print(process.stdout)
    if process.stderr:
        print(f"Errors: {process.stderr}")
    return process.returncode == 0


def main():
    """Run both analyzers and organize results"""
    print("\n" + "=" * 50)
    print("ORPHANED FILE ANALYSIS")
    print("=" * 50)

    # Step 1: Run standard analysis
    print("\n1. Running standard codebase analysis...")
    success = run_command("python scripts/analyze_codebase.py")
    if not success:
        print("Standard analysis failed!")
        return

    # Step 2: Run enhanced analysis
    print("\n2. Running enhanced analysis...")
    success = run_command("python scripts/enhanced_codebase_analyzer.py")
    if not success:
        print("Enhanced analysis failed!")
        return

    # Step 3: Copy results to project directory
    print("\n3. Copying results to Orphan-File-Project...")
    for file in [
        "codebase_analysis_report.html",
        "enhanced_analysis_report.html",
        "enhanced_analysis_report.json",
        "dependency_graph.json",
    ]:
        if os.path.exists(os.path.join(ROOT_DIR, file)):
            shutil.copy2(os.path.join(ROOT_DIR, file), os.path.join(PROJECT_DIR, file))
            print(f"  - Copied {file}")

    # Step 4: Run comparison
    print("\n4. Running comparison analysis...")
    run_command(f"cd {PROJECT_DIR} && python compare_analysis.py")

    print("\n" + "=" * 50)
    print("ANALYSIS COMPLETE")
    print("All files saved to Orphan-File-Project directory")
    print("=" * 50)


if __name__ == "__main__":
    main()
