#!/usr/bin/env python
"""
Run the complete tracing pipeline:

1.  Static import scan (AST for main.py, pydeps for others).
2.  Scheduler trace
3.  Dynamic-import pattern scan
4.  Merge static + pattern + runtime log into:
      - reports/all_used_modules.json
      - reports/unused_candidates.json
"""

import ast  # Added for AST-based tracing
import json

# import os # Removed unused import
import subprocess
import sys
from collections import deque  # Added for AST-based tracing
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]  # project root
REPORTS = ROOT / "reports"
REPORTS.mkdir(exist_ok=True)
SRC_DIR = ROOT / "src"
# SCRIPTS_DIR = ROOT / "scripts" # Removed - Scripts dir is irrelevant for this trace

# ENTRY_SCRIPTS definition is no longer needed as we only trace from src/main.py statically
# ENTRY_SCRIPTS = [...]
# ENTRY_SCRIPTS.extend(...) # Removed


def run_command(cmd_list, description):
    """Helper to run a command and handle errors."""
    print(f"Running: {description}...")
    try:
        # Line length fixed by using text=True implicitly with check=True and capture_output=True
        # Also moved cwd to the beginning for slightly better readability
        result = subprocess.run(
            cmd_list, cwd=ROOT, capture_output=True, text=True, check=True
        )
        # print(result.stdout) # Optional: uncomment to see stdout
        # if result.stderr:
        #     # Line length fixed
        #     print(f"Stderr:\n{result.stderr}", file=sys.stderr)
        print(f"Finished: {description}")
        return result
    except FileNotFoundError:
        # Line length fixed
        print(
            f"Error: Command '{cmd_list[0]}' not found. Is it installed and in PATH?",
            file=sys.stderr,
        )
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"Error running {description}: {e}", file=sys.stderr)
        # Line length fixed
        print(f"Command: {' '.join(map(str, cmd_list))}", file=sys.stderr)
        print(f"Stderr:\n{e.stderr}", file=sys.stderr)  # Corrected f-string escape
        print(f"Stdout:\n{e.stdout}", file=sys.stderr)  # Corrected f-string escape
        # Optionally exit, or return None to allow partial results
        # sys.exit(1)
        return None
    except Exception as e:
        print(f"Unexpected error running {description}: {e}", file=sys.stderr)
        sys.exit(1)


# --- AST Based Static Trace Helpers (Adapted from static_import_trace.py) --- #


class ImportVisitor(ast.NodeVisitor):
    """Collects project-specific imports (relative or starting with src_dir_name)."""

    def __init__(self, src_dir_name):
        self.imports = set()
        self.src_dir_name = src_dir_name

    def visit_Import(self, node):
        for alias in node.names:
            module_name = alias.name
            # Only consider if it starts with src or is a top-level file/dir in src
            # Check if module name itself is a py file in src or a package dir in src
            potential_file = SRC_DIR / (module_name + ".py")
            potential_pkg = SRC_DIR / module_name
            if (
                module_name.startswith(self.src_dir_name + ".")
                or ("." not in module_name and potential_file.exists())
                or (
                    "." not in module_name
                    and potential_pkg.is_dir()
                    and (potential_pkg / "__init__.py").exists()
                )
            ):
                self.imports.add(module_name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.level > 0:
            # Relative import: store tuple (module_name or None, level)
            self.imports.add((node.module, node.level))
        elif node.module and node.module.startswith(self.src_dir_name + "."):
            # Absolute import starting with src directory name
            self.imports.add(node.module)
        # Ignore external/non-src absolute imports
        self.generic_visit(node)


def resolve_import(
    imp, current_file_abs: Path, project_root: Path, src_path: Path
) -> Path | None:
    """Resolves an import (string or tuple) to a *relative* Path object (relative to project_root) or None."""
    src_dir_name = src_path.name

    try:
        if isinstance(imp, tuple):
            # --- Resolve Relative Import --- #
            module_name, level = imp
            current_dir = current_file_abs.parent
            anchor_dir = current_dir
            for _ in range(level - 1):
                anchor_dir = anchor_dir.parent

            module_parts = module_name.split(".") if module_name else []
            potential_target_base = anchor_dir.joinpath(*module_parts)

            # Check 1: Is it a python file?
            potential_file = potential_target_base.with_suffix(".py")
            if potential_file.is_file() and str(potential_file).startswith(
                str(src_path)
            ):
                return potential_file.relative_to(project_root)

            # Check 2: Is it a package directory?
            if potential_target_base.is_dir() and str(potential_target_base).startswith(
                str(src_path)
            ):
                init_file = potential_target_base / "__init__.py"
                if init_file.is_file():
                    return init_file.relative_to(project_root)

        elif isinstance(imp, str):
            # --- Resolve Absolute Import within Project --- #
            module_parts = []
            if imp.startswith(src_dir_name + "."):
                module_parts = imp[len(src_dir_name) + 1 :].split(".")
            elif "." not in imp:  # Top-level import like 'import scheduler_instance'
                potential_file_in_src = src_path / (imp + ".py")
                potential_pkg_in_src = src_path / imp
                if potential_file_in_src.exists() or (
                    potential_pkg_in_src.is_dir()
                    and (potential_pkg_in_src / "__init__.py").exists()
                ):
                    module_parts = [imp]
                else:
                    return None  # Not a project import
            else:
                return None  # External or non-project import

            if not module_parts:
                return None

            base_path = src_path  # Start resolution from src/

            # Check 1: Is it a python file? (e.g., src/services/utils.py)
            potential_file = base_path.joinpath(*module_parts).with_suffix(".py")
            if potential_file.is_file():
                return potential_file.relative_to(project_root)

            # Check 2: Is it a package directory? (e.g., src/services/utils/__init__.py)
            potential_dir = base_path.joinpath(*module_parts)
            if potential_dir.is_dir():
                init_file = potential_dir / "__init__.py"
                if init_file.is_file():
                    return init_file.relative_to(project_root)

    except ValueError:
        # Handles cases where relative_to fails (e.g., path outside project root)
        return None
    except Exception as e:
        print(
            f"Error resolving import '{imp}' in {current_file_abs.relative_to(project_root)}: {e}",
            file=sys.stderr,
        )
        return None

    return None  # Import could not be resolved to a file in src


def trace_static_ast(entry_point_rel: Path) -> set[str]:
    """Performs AST-based static import trace starting from a single entry point."""
    print(f"  Running AST trace on: {entry_point_rel}")
    project_root = ROOT
    src_path = SRC_DIR
    src_dir_name = src_path.name

    processed_files_abs = set()  # Store absolute paths processed
    queue = deque()
    reachable_files_rel_set = set()

    # Initialize queue
    abs_entry = (project_root / entry_point_rel).resolve()
    if abs_entry.is_file() and str(abs_entry).startswith(str(src_path)):
        queue.append(abs_entry)
        processed_files_abs.add(abs_entry)
        reachable_files_rel_set.add(
            str(entry_point_rel).replace("\\\\", "/")
        )  # Add entry point itself
    else:
        print(f"Warning: AST Entry point not found or outside src: {entry_point_rel}")
        return set()

    while queue:
        current_file_abs = queue.popleft()
        current_file_rel_for_error = current_file_abs.relative_to(project_root)

        try:
            with open(current_file_abs, "r", encoding="utf-8") as f:
                content = f.read()
            tree = ast.parse(content, filename=str(current_file_abs))
        except SyntaxError as e:
            print(
                f"SyntaxError parsing {current_file_rel_for_error}: {e}",
                file=sys.stderr,
            )
            continue
        except Exception as e:
            print(
                f"Error reading/parsing {current_file_rel_for_error}: {e}",
                file=sys.stderr,
            )
            continue

        visitor = ImportVisitor(src_dir_name)
        visitor.visit(tree)

        for imp in visitor.imports:
            resolved_path_rel = resolve_import(
                imp, current_file_abs, project_root, src_path
            )

            if resolved_path_rel:
                resolved_file_abs = (project_root / resolved_path_rel).resolve()
                # Ensure it's a file within src and not already processed
                if (
                    resolved_file_abs.is_file()
                    and str(resolved_file_abs).startswith(str(src_path))
                    and resolved_file_abs not in processed_files_abs
                ):
                    processed_files_abs.add(resolved_file_abs)
                    # Store as normalized string path
                    rel_path_str = str(resolved_path_rel).replace("\\\\", "/")
                    if not rel_path_str.endswith("/__init__.py"):  # Exclude __init__.py
                        reachable_files_rel_set.add(rel_path_str)
                    queue.append(resolved_file_abs)

    print(
        f"    Found {len(reachable_files_rel_set)} src modules from {entry_point_rel} via AST trace"
    )
    return reachable_files_rel_set


# --- End AST Based Static Trace Helpers --- #


def collect_static() -> set[str]:
    """Collects static imports using AST starting ONLY from main.py."""
    print("--- Collecting Static Imports (AST from main.py) ---")
    main_entry_point = SRC_DIR / "main.py"
    # Check if main.py exists before trying to trace
    if not main_entry_point.exists():
        print(f"Error: Entry point {main_entry_point} not found.", file=sys.stderr)
        return set()
    main_rel_path = main_entry_point.relative_to(ROOT)

    # Use AST trace for main.py ONLY
    ast_modules = trace_static_ast(main_rel_path)

    print(f"Total static src modules found from main.py (AST): {len(ast_modules)}")
    output_filename = "used_files_static_ast_main.json"
    (REPORTS / output_filename).write_text(
        json.dumps(sorted(list(ast_modules)), indent=2)
    )
    print(f"Static analysis report saved to {output_filename}")
    return ast_modules


def run_ast_script(script_name: str, output_file: Path):
    """Runs an AST analysis script from the tools directory."""
    script_path = ROOT / "tools" / script_name
    if not script_path.exists():
        print(f"Error: AST script not found: {script_path}", file=sys.stderr)
        return False

    # Line length fixed
    cmd = [
        sys.executable,
        str(script_path),
        "--out",
        str(output_file.relative_to(ROOT)),
    ]
    result = run_command(cmd, f"Run {script_name}")
    return result is not None and result.returncode == 0


def collect_scheduler() -> set[str]:
    """Runs scheduler_trace.py and returns files containing job definitions."""
    print("--- Collecting Scheduler Job Definitions --- ")
    output_file = REPORTS / "scheduler_jobs.json"
    success = run_ast_script("scheduler_trace.py", output_file)
    files_with_jobs = set()
    if success and output_file.exists():
        try:
            data = json.loads(output_file.read_text())
            # Use relative paths stored by the script
            files_with_jobs = {entry["file"] for entry in data if "file" in entry}
            print(f"Found {len(files_with_jobs)} files with scheduler job definitions.")
        except json.JSONDecodeError as e:
            print(f"Error reading scheduler report {output_file}: {e}", file=sys.stderr)
        except Exception as e:
            # Line length fixed
            print(
                f"Error processing scheduler report {output_file}: {e}", file=sys.stderr
            )
    else:
        # Removed unnecessary f-string
        print("Scheduler trace did not run successfully or output file missing.")
    return files_with_jobs


def collect_dynamic_patterns() -> set[str]:
    """Runs dynamic_imports.py and returns files containing dynamic patterns."""
    print("--- Collecting Dynamic Import Patterns --- ")
    output_file = REPORTS / "dynamic_imports.json"
    success = run_ast_script("dynamic_imports.py", output_file)
    files_with_patterns = set()
    if success and output_file.exists():
        try:
            data = json.loads(output_file.read_text())
            files_with_patterns = {entry["file"] for entry in data if "file" in entry}
            # Line length fixed
            print(
                f"Found {len(files_with_patterns)} files with dynamic import patterns."
            )
        except json.JSONDecodeError as e:
            # Line length fixed
            print(
                f"Error reading dynamic imports report {output_file}: {e}",
                file=sys.stderr,
            )
        except Exception as e:
            # Line length fixed
            print(
                f"Error processing dynamic imports report {output_file}: {e}",
                file=sys.stderr,
            )
    else:
        # Removed unnecessary f-string
        print("Dynamic import scan did not run successfully or output file missing.")
    return files_with_patterns


# Line length fixed
def map_module_name_to_path(
    module_name: str, src_dir: Path, project_root: Path
) -> str | None:
    """Maps a potentially dotted module name to a relative file path within src."""
    parts = module_name.split(".")
    potential_file = src_dir.joinpath(*parts).with_suffix(".py")
    if potential_file.is_file():
        return str(potential_file.relative_to(project_root)).replace("\\\\", "/")
    potential_init = src_dir.joinpath(*parts, "__init__.py")
    if potential_init.is_file():
        # Return the package init file itself, we filter later if needed
        return str(potential_init.relative_to(project_root)).replace("\\\\", "/")
    return None


def collect_runtime() -> set[str]:
    """Parses runtime_imports.log and maps module names to relative file paths."""
    print("--- Collecting Runtime Imports --- ")
    runtime_paths = set()
    log_file = REPORTS / "runtime_imports.log"
    if log_file.exists():
        try:
            lines = log_file.read_text(encoding="utf-8").splitlines()
            count = 0
            for line in lines:
                if line.startswith("#") or " | " not in line:
                    continue
                try:
                    module_name = line.split(" | ", 2)[1].strip()
                    # Only map modules potentially within our src directory
                    if module_name.startswith(SRC_DIR.name):
                        # Map src.services.utils -> src/services/utils.py
                        path = map_module_name_to_path(module_name, ROOT, ROOT)
                        if path:
                            runtime_paths.add(path)
                            count += 1
                    elif "." not in module_name:  # Could be top-level in src?
                        path = map_module_name_to_path(module_name, SRC_DIR, ROOT)
                        if path:
                            runtime_paths.add(path)
                            count += 1
                except IndexError:
                    print(f"Warning: Skipping malformed runtime log line: {line}")
            print(f"Mapped {count} runtime modules to project file paths.")
        except Exception as e:
            # Line length fixed
            print(
                f"Error reading or processing runtime log {log_file}: {e}",
                file=sys.stderr,
            )
    else:
        print(f"Runtime log file not found: {log_file}")
    return runtime_paths


# Modified find_all_project_py_files to ONLY scan src_dir
def find_all_project_py_files(src_dir: Path, project_root: Path) -> set[str]:
    """Finds all .py files in the specified src_dir, excluding __init__.py."""
    all_py = set()
    if not src_dir.is_dir():
        print(
            f"Warning: Source directory {src_dir} not found or not a directory.",
            file=sys.stderr,
        )
        return all_py
    for p in src_dir.rglob("*.py"):
        if p.name != "__init__.py":
            all_py.add(str(p.relative_to(project_root)).replace("\\\\", "/"))
    # Removed scan for scripts_dir
    return all_py


def main():
    # Removed unnecessary f-string
    print("=== Starting Full Dependency Trace ===")
    print(f"Project Root: {ROOT}")

    # --- Run Analysis Steps --- #
    static_files = collect_static()  # Only traces from src/main.py
    sched_files = collect_scheduler()  # Scans src/ for scheduler jobs
    dyn_files = collect_dynamic_patterns()  # Scans src/ for dynamic imports
    runtime_files = collect_runtime()  # Parses runtime log if available

    # --- Combine Used Files --- #
    used_files = set(static_files)
    used_files.update(sched_files)
    used_files.update(dyn_files)
    used_files.update(runtime_files)

    # Filter out any __init__.py files from the final used set
    final_used_files = {f for f in used_files if not f.endswith("/__init__.py")}

    print("--- Aggregation --- ")
    print(
        f"Total unique used files identified in src/ "
        f"(Static from main.py + Scheduler + Dynamic + Runtime): {len(final_used_files)}"
    )
    output_used_file = REPORTS / "all_used_modules.json"
    with output_used_file.open("w") as fp:
        json.dump(sorted(list(final_used_files)), fp, indent=2)
    print(f"Combined list of used files saved to: {output_used_file}")

    # --- Find All Python Files in Project (src ONLY) --- #
    all_py_files = find_all_project_py_files(SRC_DIR, ROOT)  # Only pass SRC_DIR
    print(f"Found {len(all_py_files)} total potentially relevant .py files in src/")

    # --- Calculate Unused (src ONLY) --- #
    unused_candidate_files = sorted(list(all_py_files - final_used_files))
    print(
        f"Identified {len(unused_candidate_files)} potentially unused files within src/."
    )
    output_unused_file = REPORTS / "unused_candidates.json"
    with output_unused_file.open("w") as fp:
        json.dump(unused_candidate_files, fp, indent=2)
    print(f"Unused candidates saved to: {output_unused_file}")
    print("=== Trace Complete ===")

    return 0  # Explicitly return 0 on success


if __name__ == "__main__":
    # Example pydeps config file (pydeps_config.yaml) - Optional
    # Create this file in the project root if needed
    # ```yaml
    # excludes:
    #   - ^tests\.
    # skip_missing: true
    # max_bacon: 2
    # ```
    sys.exit(main())
