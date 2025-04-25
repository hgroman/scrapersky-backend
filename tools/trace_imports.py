import argparse
import ast
import json
import os
import sys
from pathlib import Path
import yaml
import glob

# Attempt to import importlab
try:
    from importlab.graph import ImportGraph
    from importlab.resolve import RelativeResolver, AbsoluteResolver
except ImportError as e:
    import pprint
    print("\n[IMPORTLAB DIAGNOSTIC ERROR]")
    print("ImportError:", e)
    print("sys.path:")
    pprint.pprint(sys.path)
    print("os.environ (PYTHONPATH if set):")
    print(os.environ.get('PYTHONPATH', '<not set>'))
    print("Error: importlab is not installed. Please install it: pip install importlab")
    sys.exit(1)

# Add src directory to Python path to allow finding modules
SRC_DIR = Path(__file__).parent.parent / 'src'
# sys.path.insert(0, str(SRC_DIR.resolve()))

# --- Configuration ---
DEFAULT_ENTRY_POINT = 'src/main.py'
DEFAULT_CONFIG_FILE = 'reports/cleanup_config.yaml'
DEFAULT_USED_OUTPUT = 'reports/used_files.json'
DEFAULT_UNUSED_OUTPUT = 'reports/unused_candidates.json'
SRC_ROOT = 'src'

# --- Helper Functions ---

def load_config(config_path):
    """Loads exclusion patterns from the YAML config file."""
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            return config.get('exclude_paths', [])
    except FileNotFoundError:
        print(f"Warning: Config file not found at {config_path}. No exclusions applied.")
        return []
    except Exception as e:
        print(f"Error loading config file {config_path}: {e}")
        return []

def find_routers_ast(entry_point_path):
    """Parses the entry point file using AST to find app.include_router calls and the source files."""
    router_paths = set()
    variable_to_module_map = {}
    router_variables_used = set()

    try:
        with open(entry_point_path, 'r') as f:
            content = f.read()
        tree = ast.parse(content)

        # Walk the AST to find imports and include_router calls
        for node in ast.walk(tree):
            # Find imports like: from .routers.module import router as variable_name
            if isinstance(node, ast.ImportFrom):
                if node.module and node.module.startswith('.routers') and node.names:
                    for alias in node.names:
                        if alias.name == 'router' and alias.asname:
                            variable_to_module_map[alias.asname] = node.module
            # Find calls like: app.include_router(router_variable, ...)
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute) and \
                   isinstance(node.func.value, ast.Name) and \
                   node.func.value.id == 'app' and \
                   node.func.attr == 'include_router':
                    if node.args and isinstance(node.args[0], ast.Name):
                        router_variables_used.add(node.args[0].id)

        # Resolve the file path for each used router variable
        for variable_name in router_variables_used:
            if variable_name in variable_to_module_map:
                module_path_str = variable_to_module_map[variable_name]
                relative_file_path = module_path_str.strip('.').replace('.', '/') + '.py'
                router_file_path = entry_point_path.parent / relative_file_path
                router_paths.add(str(router_file_path.resolve()))
            else:
                print(f"Warning: Could not map router variable '{variable_name}' to an import statement via AST.")

    except FileNotFoundError:
        print(f"Error: Entry point file not found at {entry_point_path}")
    except Exception as e:
        print(f"Error parsing entry point {entry_point_path} for routers using AST: {e}")

    return list(router_paths)

def find_schedulers(src_root_path):
    """Finds scheduler files based on naming convention."""
    scheduler_pattern = os.path.join(src_root_path, 'services', '*_scheduler.py')
    return glob.glob(scheduler_pattern)

def is_excluded(file_path, exclude_patterns, project_root_path):
    """Checks if a file path matches any exclusion glob patterns relative to project root."""
    try:
        relative_path = Path(file_path).relative_to(project_root_path)
    except ValueError:
        # File is not inside the project root (e.g., system library)
        return False # Don't exclude system libs based on project patterns

    for pattern in exclude_patterns:
        if relative_path.match(pattern):
            return True
    # Also exclude the archive directory by default
    if relative_path.match('src/archive/**'):
        return True
    return False

def find_all_py_files(src_root_path):
    """Finds all .py files within the source directory, excluding __init__.py."""
    all_files = set()
    for root, _, files in os.walk(src_root_path):
        for file in files:
            if file.endswith('.py') and file != '__init__.py':
                # Store absolute paths
                all_files.add(str(Path(os.path.join(root, file)).resolve()))
    return all_files

# --- Main Execution ---

def main():
    parser = argparse.ArgumentParser(description="Trace Python module imports using importlab to find unused files.")
    parser.add_argument('--entry', default=DEFAULT_ENTRY_POINT, help=f"Primary entry point script (default: {DEFAULT_ENTRY_POINT})")
    parser.add_argument('--config', default=DEFAULT_CONFIG_FILE, help=f"Path to YAML config file with exclusions (default: {DEFAULT_CONFIG_FILE})")
    parser.add_argument('--out-used', default=DEFAULT_USED_OUTPUT, help=f"Output JSON file for used modules (default: {DEFAULT_USED_OUTPUT})")
    parser.add_argument('--out-unused', default=DEFAULT_UNUSED_OUTPUT, help=f"Output JSON file for unused candidates (default: {DEFAULT_UNUSED_OUTPUT})")
    args = parser.parse_args()

    print(f"Starting import trace using importlab...")
    print(f"Entry Point: {args.entry}")
    print(f"Config File: {args.config}")

    # --- Initialization ---
    entry_point_path = Path(args.entry).resolve()
    config_path = Path(args.config).resolve()
    src_root_path = Path(SRC_ROOT).resolve()
    project_root_path = src_root_path.parent # Assumes src is directly under project root

    exclude_patterns = load_config(config_path)
    print(f"Loaded {len(exclude_patterns)} exclusion patterns: {exclude_patterns}")

    # --- Tracing with importlab ---
    # importlab needs the directory containing the entry point in the path
    sys.path.insert(0, str(entry_point_path.parent))

    try:
        print(f"Building import graph starting from: {entry_point_path}")
        # Use both resolvers: Absolute for system libs, Relative for local modules
        resolvers = [AbsoluteResolver(sys.path), RelativeResolver()]
        graph = ImportGraph.create(entry_point_path, resolvers)

        # Add routers found by AST
        routers_found = find_routers_ast(entry_point_path)
        print(f"Found potential router files via AST: {routers_found}")
        for router_path_str in routers_found:
             if Path(router_path_str).exists():
                 print(f"Adding router to graph: {router_path_str}")
                 try:
                     graph.add_file(Path(router_path_str))
                 except Exception as e:
                     print(f"Error adding router {router_path_str} to graph: {e}")
             else:
                 print(f"Warning: Router path {router_path_str} derived via AST does not exist. Skipping add.")

        # Add schedulers
        schedulers_found = find_schedulers(str(src_root_path))
        print(f"Found scheduler files: {schedulers_found}")
        for scheduler_path in schedulers_found:
             if Path(scheduler_path).exists():
                 print(f"Adding scheduler to graph: {scheduler_path}")
                 try:
                    graph.add_file(Path(scheduler_path))
                 except Exception as e:
                    print(f"Error adding scheduler {scheduler_path} to graph: {e}")
             else:
                 print(f"Warning: Scheduler path {scheduler_path} does not exist. Skipping add.")

    except Exception as e:
        print(f"Error creating import graph with importlab: {e}")
        sys.exit(1)

    # --- Analysis ---
    # Collect all unique file paths from the graph nodes within the src directory
    used_module_paths = set()
    print("\n--- Analyzing Import Graph ---")
    for node in graph:
        if node.path and node.path.is_file():
            abs_path = str(node.path.resolve())
            # Only include files within our source directory
            if abs_path.startswith(str(src_root_path)):
                # Exclude __init__.py files as they are implicitly used
                if not abs_path.endswith('__init__.py'):
                    used_module_paths.add(abs_path)
                    # print(f"  Used: {abs_path}") # Debug print

    print(f"\nTotal unique modules traced within '{SRC_ROOT}' via importlab: {len(used_module_paths)}")

    # Find all potentially relevant .py files in the source directory
    all_py_files = find_all_py_files(src_root_path)
    print(f"Total .py files found in '{SRC_ROOT}': {len(all_py_files)}")

    # Determine unused files
    unused_candidates = set()
    actually_used = set() # Store relative paths for output

    for abs_file_path in all_py_files:
        # Convert to relative path for output consistency and exclusion checks
        relative_path = os.path.relpath(abs_file_path, project_root_path)

        if is_excluded(abs_file_path, exclude_patterns, project_root_path):
            print(f"Excluding (config/archive): {relative_path}")
            continue

        if abs_file_path in used_module_paths:
            actually_used.add(relative_path)
        else:
            # Since importlab graph should be comprehensive, files not in the graph are candidates
            print(f"Candidate for unused: {relative_path}")
            unused_candidates.add(relative_path)

    # Sort for consistent output
    used_list = sorted(list(actually_used))
    unused_list = sorted(list(unused_candidates))

    print(f"\nFinal count - Used files: {len(used_list)}, Unused candidates: {len(unused_list)}")

    # --- Output ---
    os.makedirs(os.path.dirname(args.out_used), exist_ok=True)
    os.makedirs(os.path.dirname(args.out_unused), exist_ok=True)

    print(f"Writing used files list to: {args.out_used}")
    with open(args.out_used, 'w') as f:
        json.dump(used_list, f, indent=2)

    print(f"Writing unused candidates list to: {args.out_unused}")
    with open(args.out_unused, 'w') as f:
        json.dump(unused_list, f, indent=2)

    print("Trace complete.")

if __name__ == "__main__":
    main()
