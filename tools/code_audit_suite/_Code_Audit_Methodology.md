# Code Audit Methodology: Identifying Unused Code in `src/`

**Version:** 1.1
**Date:** $(date +'%Y-%m-%d')

## 1. Goal

The primary objective of this process is to identify potentially unused Python modules (`.py` files, excluding `__init__.py`) **strictly within the `src/` directory** of the ScraperSky backend application. A secondary goal is to map used files to the business functions they support. This aids in code maintenance, reduces complexity, and helps prevent reliance on obsolete components.

## 2. Methodology Overview

After significant iteration and encountering limitations with various tools (`modulefinder`, `importlab`, `pydeps`), the current, most reliable methodology uses a combination of techniques:

1.  **Initial Full Trace:** An Abstract Syntax Tree (AST) based trace starting from `src/main.py` and known scheduler entry points, executed via `tools/run_full_trace.py`. This generates the initial list of _all_ used files (`reports/all_used_modules.json`) required for identifying unused candidates.
2.  **Endpoint Identification:** Analysis of frontend code (e.g., `admin-dashboard.html`) and project knowledge to identify API router files (`src/routers/*.py`) corresponding to specific business functions or UI features.
3.  **Targeted Dependency Tracing:** Execution of dedicated AST-based tracing scripts (`tools/trace_deps_*.py`) for _each_ identified router/feature entry point. These scripts generate specific dependency lists (`reports/deps_*.json`).
4.  **Functional Mapping:** Consolidation of the specific dependency lists using `tools/build_functional_map.py`. This script maps each used file to the business function(s) that depend on it, based on the targeted traces.
5.  **Candidate Identification:** Comparing the _all used files_ list from Step 1 against all `.py` files found in `src/` to generate the list of potentially unused candidates (`reports/unused_candidates.json`).
6.  **Manual Audit:** Critical review of the candidate list, cross-referencing with the functional map and project knowledge.

**Key Principle:** This process explicitly **ignores** directories like `scripts/` and `tools/` for identifying candidates, focusing solely on the application code within `src/`. The functional mapping relies on targeted traces from specific entry points.

## 3. Key Scripts

- **`tools/run_full_trace.py`**: Orchestrates the initial full trace (Step 1) and generates the final unused candidate list (Step 5).
- **`tools/trace_deps_*.py`**: Individual scripts for tracing dependencies of specific router/feature entry points (Step 3).
- **`tools/build_functional_map.py`**: Consolidates targeted traces into a functional map (Step 4).

## 4. Analysis Steps Detailed

- **Initial Full Trace (`run_full_trace.py`)**

  - **Method:** Uses a custom AST parser (`ImportVisitor`, `resolve_import`, `trace_static_ast`).
  - **Entry Points:** Starts from `src/main.py` and known scheduler files (`*_scheduler.py`). Also incorporates results from `scheduler_trace.py` and `dynamic_imports.py`.
  - **Rationale:** Provides a comprehensive list of all files reachable through static analysis, scheduler definitions, and basic dynamic patterns.
  - **Output:** `reports/all_used_modules.json` (comprehensive used file list), `reports/unused_candidates.json` (primary list for manual review).

- **Endpoint Identification (Manual/Analysis)**

  - **Method:** Examine frontend code, API documentation, or project structure to identify key router files in `src/routers/` that represent distinct application features.

- **Targeted Dependency Tracing (`trace_deps_*.py`)**

  - **Method:** Each script uses the same core AST tracing logic as `run_full_trace.py` but starts from a _single_ specific router file (e.g., `trace_deps_google_maps_api.py` starts from `src/routers/google_maps_api.py`).
  - **Rationale:** Creates precise lists of dependencies for individual business functions.
  - **Output:** Multiple `reports/deps_*.json` files (e.g., `deps_google_maps_api.json`, `deps_places_staging.json`).

- **Functional Mapping (`build_functional_map.py`)**

  - **Method:** Reads `all_used_modules.json` and all `deps_*.json` files.
  - **Process:** Initializes a map for all used files. Iterates through each feature's dependency list (`deps_*.json`) and adds the corresponding feature name to the mapping for each file in that list. Files mapped to multiple features are re-categorized as `Core/Shared`. Limited keyword fallbacks (`CoreFastAPI`, `BackgroundScheduler`, `ScrapingTask`) are applied to files not mapped by any specific feature trace.
  - **Rationale:** Provides a structured view of the codebase organized by business function, based on direct tracing results.
  - **Output:** `Docs/Docs_0_Architecture_and_Status/functional_dependency_map.json`.

- **Candidate Identification (Performed by `run_full_trace.py`)**
  - **Method:** Compares the full list of `.py` files in `src/` (excluding `__init__.py`) against the `reports/all_used_modules.json` list.
  - **Rationale:** Identifies files present in the source directory but not found by any tracing mechanism (static, scheduler, dynamic, runtime).
  - **Output:** `reports/unused_candidates.json`.

## 5. Output Files Summary (Key Files)

- `reports/all_used_modules.json`: Comprehensive list of files identified as used by the initial full trace.
- `reports/deps_*.json`: Dependency lists for specific features/routers.
- `Docs/Docs_0_Architecture_and_Status/functional_dependency_map.json`: Map of used files categorized by the business function(s) they support.
- `reports/unused_candidates.json`: **Final candidate list for manual review.** Files present in `src/` but _not_ in `all_used_modules.json`.

## 6. CRITICAL: Manual Review Required

**The `reports/unused_candidates.json` list represents _potentially_ unused files ONLY.** Automated analysis has limitations:

- **Framework/DI Magic:** Usage might be obscured by framework conventions or dependency injection.
- **Dynamic Loading:** Less common dynamic patterns or configuration-driven loading might be missed.

**Therefore, manual review of every file listed in `unused_candidates.json` is MANDATORY before archiving.**

- Use the process outlined in `project-docs/41-Code-Audit-And-Archive/41.13-Unused-Code-Audit.md`.
- Cross-reference candidates with the `Docs/Docs_0_Architecture_and_Status/functional_dependency_map.json` and the list of `Unmapped` files within it.

## 7. Process Evolution Context

This methodology was reached after significant trial and error:

- Initial attempts using `modulefinder`, `importlab`, and `pydeps` proved unreliable or faced compatibility issues within this project's environment.
- Relying solely on broad static analysis from `main.py` missed critical components and led to incorrect conclusions.
- The current approach, combining a comprehensive initial trace (for candidate identification) with targeted, router-specific traces (for functional understanding), provides the most reliable automated foundation achieved so far, acknowledging the vital role of subsequent manual validation.
