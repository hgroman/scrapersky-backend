#!/usr/bin/env python
"""
Run the complete tracing pipeline:

1.  Static import scan (AST for main.py, pydeps for others).
2.  Scheduler trace
3.  Dynamic-import pattern scan
4.  Merge static + pattern + runtime log into:
      - reports/all_used_modules.json
      - reports/unused_candidates.json

MODIFIED: This version is tailored to trace dependencies for a SINGLE router.
"""
import json
# import os # Removed unused import
import subprocess
import sys
import ast # Added for AST-based tracing
from pathlib import Path
from collections import deque # Added for AST-based tracing

ROOT = Path(__file__).resolve().parents[1]   # project root
REPORTS = ROOT / "reports"
REPORTS.mkdir(exist_ok=True)
SRC_DIR = ROOT / "src"

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
            f"Error: Command '{cmd_list[0]}' not found. "
            f"Is it installed and in PATH?",
            file=sys.stderr
        )
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"Error running {description}: {e}", file=sys.stderr)
        # Line length fixed
        print(f"Command: {' '.join(map(str, cmd_list))}", file=sys.stderr)
        print(f"Stderr:\n{e.stderr}", file=sys.stderr) # Corrected f-string escape
        print(f"Stdout:\n{e.stdout}", file=sys.stderr) # Corrected f-string escape
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
            potential_file = SRC_DIR / (module_name + '.py')
            potential_pkg = SRC_DIR / module_name
            if module_name.startswith(self.src_dir_name + '.') or \
               ('.' not in module_name and potential_file.exists()) or \
               ('.' not in module_name and potential_pkg.is_dir() and (potential_pkg / '__init__.py').exists()):
                 self.imports.add(module_name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.level > 0:
            # Relative import: store tuple (module_name or None, level)
            self.imports.add((node.module, node.level))
        elif node.module and node.module.startswith(self.src_dir_name + '.'):
            # Absolute import starting with src directory name
            self.imports.add(node.module)
        # Ignore external/non-src absolute imports
        self.generic_visit(node)

def resolve_import(imp, current_file_abs: Path, project_root: Path, src_path: Path) -> Path | None:
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

            module_parts = module_name.split('.') if module_name else []
            potential_target_base = anchor_dir.joinpath(*module_parts)

            # Check 1: Is it a python file?
            potential_file = potential_target_base.with_suffix('.py')
            if potential_file.is_file() and str(potential_file).startswith(str(src_path)):
                return potential_file.relative_to(project_root)

            # Check 2: Is it a package directory?
            if potential_target_base.is_dir() and str(potential_target_base).startswith(str(src_path)):
                init_file = potential_target_base / '__init__.py'
                if init_file.is_file():
                    return init_file.relative_to(project_root)

        elif isinstance(imp, str):
            # --- Resolve Absolute Import within Project --- #
            module_parts = []
            if imp.startswith(src_dir_name + '.'):
                module_parts = imp[len(src_dir_name)+1:].split('.')
            elif '.' not in imp: # Top-level import like 'import scheduler_instance'
                potential_file_in_src = src_path / (imp + '.py')
                potential_pkg_in_src = src_path / imp
                if potential_file_in_src.exists() or (potential_pkg_in_src.is_dir() and (potential_pkg_in_src / '__init__.py').exists()):
                     module_parts = [imp]
                else:
                    return None # Not a project import
            else:
                return None # External or non-project import

            if not module_parts: return None

            base_path = src_path # Start resolution from src/

            # Check 1: Is it a python file? (e.g., src/services/utils.py)
            potential_file = base_path.joinpath(*module_parts).with_suffix('.py')
            if potential_file.is_file():
                return potential_file.relative_to(project_root)

            # Check 2: Is it a package directory? (e.g., src/services/utils/__init__.py)
            potential_dir = base_path.joinpath(*module_parts)
            if potential_dir.is_dir():
                init_file = potential_dir / '__init__.py'
                if init_file.is_file():
                    return init_file.relative_to(project_root)

    except ValueError:
        # Handles cases where relative_to fails (e.g., path outside project root)
        return None
    except Exception as e:
        print(f"Error resolving import '{imp}' in {current_file_abs.relative_to(project_root)}: {e}", file=sys.stderr)
        return None

    return None # Import could not be resolved to a file in src

def trace_static_ast(entry_point_rel: Path) -> set[str]:
    """Performs AST-based static import trace starting from a single entry point."""
    print(f"  Running AST trace on: {entry_point_rel}")
    project_root = ROOT
    src_path = SRC_DIR
    src_dir_name = src_path.name

    processed_files_abs = set() # Store absolute paths processed
    queue = deque()
    reachable_files_rel_set = set()

    # Initialize queue
    abs_entry = (project_root / entry_point_rel).resolve()
    if abs_entry.is_file() and str(abs_entry).startswith(str(src_path)):
        queue.append(abs_entry)
        processed_files_abs.add(abs_entry)
        reachable_files_rel_set.add(str(entry_point_rel).replace('\\\\', '/')) # Add entry point itself
    else:
         print(f"Warning: AST Entry point not found or outside src: {entry_point_rel}")
         return set()

    while queue:
        current_file_abs = queue.popleft()
        current_file_rel_for_error = current_file_abs.relative_to(project_root)

        try:
            with open(current_file_abs, 'r', encoding='utf-8') as f:
                content = f.read()
            tree = ast.parse(content, filename=str(current_file_abs))
        except SyntaxError as e:
            print(f"SyntaxError parsing {current_file_rel_for_error}: {e}", file=sys.stderr)
            continue
        except Exception as e:
            print(f"Error reading/parsing {current_file_rel_for_error}: {e}", file=sys.stderr)
            continue

        visitor = ImportVisitor(src_dir_name)
        visitor.visit(tree)

        for imp in visitor.imports:
            resolved_path_rel = resolve_import(imp, current_file_abs, project_root, src_path)

            if resolved_path_rel:
                resolved_file_abs = (project_root / resolved_path_rel).resolve()
                # Ensure it's a file within src and not already processed
                if resolved_file_abs.is_file() and str(resolved_file_abs).startswith(str(src_path)) and resolved_file_abs not in processed_files_abs:
                    processed_files_abs.add(resolved_file_abs)
                    # Store as normalized string path
                    rel_path_str = str(resolved_path_rel).replace('\\\\', '/')
                    if not rel_path_str.endswith('/__init__.py'): # Exclude __init__.py
                         reachable_files_rel_set.add(rel_path_str)
                    queue.append(resolved_file_abs)

    print(f"    Found {len(reachable_files_rel_set)} src modules from {entry_point_rel} via AST trace")
    return reachable_files_rel_set

# --- End AST Based Static Trace Helpers --- #

def main():
    # Removed unnecessary f-string
    print("=== Starting Single Router Trace ===")
    print(f"Project Root: {ROOT}")

    # Define the single router file to trace
    router_file_name = "google_maps_api.py"
    router_file = SRC_DIR / "routers" / router_file_name

    # Check if the target router file exists
    if not router_file.exists():
        print(f"Error: Router file {router_file} not found.", file=sys.stderr)
        sys.exit(1)

    router_rel_path = router_file.relative_to(ROOT)

    # --- Run AST Trace for the specified router --- #
    print("--- Collecting Static Imports (AST from single router) ---")
    ast_modules = trace_static_ast(router_rel_path)

    print(f"Total static src modules found from {router_rel_path} (AST): {len(ast_modules)}")

    # --- Define Output File Name --- #
    # Use a descriptive name based on the traced router
    output_filename = f"deps_{router_file_name.replace('.py', '')}.json"
    output_path = REPORTS / output_filename

    # --- Write Results --- #
    with output_path.open("w") as fp:
        json.dump(sorted(list(ast_modules)), fp, indent=2)
    print(f"Dependency list saved to: {output_path}")

    print("=== Trace Complete ===")

    return 0 # Explicitly return 0 on success

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
