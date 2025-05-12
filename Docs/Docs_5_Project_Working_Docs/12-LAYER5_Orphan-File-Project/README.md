# Orphan File Project

A simple tool to identify orphaned files and real scheduler components in your FastAPI project.

## Problem

The standard static analysis (`dependency_analyzer.py`) incorrectly marks scheduler components (like `domain_scheduler.py`) as "orphaned files" because they're not directly referenced by route handlers.

This creates a false impression that these files are unused, when they're actually critical components.

## Solution

This tool combines:

1. Standard analysis (finds orphaned files)
2. Enhanced analysis (finds scheduler components)
3. Comparison (identifies critical components incorrectly marked as orphaned)

## Usage

Run the entire analysis with one command:

```bash
python Orphan-File-Project/run_analysis.py
```

This will:

1. Run the standard analyzer
2. Run the enhanced analyzer
3. Compare results to find critical components marked as orphaned
4. Store all output files in the `Orphan-File-Project` directory

## Files

- `run_analysis.py` - Main script to run all analyzers
- `compare_analysis.py` - Compares results to find misidentified components
- `codebase_analysis_report.html` - Standard analysis results
- `enhanced_analysis_report.html` - Enhanced analysis results
- `enhanced_analysis_report.json` - Enhanced analysis data

## Example Output

The comparison identifies 9 critical scheduler components that are incorrectly marked as orphaned, including:

```
src/services/domain_scheduler.py 90%
* Standard analysis: Marked as orphaned with 90% confidence
* Enhanced analysis: Actually a SCHEDULER with 100% confidence
```
