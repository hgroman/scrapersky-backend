import argparse
import json
import os
import sys
from typing import List, Set

# Constants
LOG_SEARCH_PREFIX = "INFO - LOADED_MODULE:"  # Prefix to search for in log lines
# Define modules to always ignore (using user-provided set)
ALWAYS_IGNORE_MODULES = {
    "src.__init__",  # Explicitly ignore top-level init if desired
    "src.config",  # Ignore entire config package
    "src.utils",  # Ignore entire utils package
    "src.config.runtime_tracer",  # Keep ignoring the tracer
    # Add other modules/packages if needed
}


def extract_loaded_modules(logs: List[str]) -> Set[str]:
    """Extracts module names from log lines containing LOG_SEARCH_PREFIX."""
    loaded_modules = set()
    for line in logs:
        if LOG_SEARCH_PREFIX in line:
            try:
                # Split based on the full prefix to get the module name
                parts = line.split(LOG_SEARCH_PREFIX, 1)
                if len(parts) > 1:
                    module_name = parts[1].strip()
                    if module_name:
                        loaded_modules.add(module_name)
            except Exception as e:
                print(
                    f"Warning: Could not parse module from log line: '{line}'. "
                    f"Error: {e}"
                )
    return loaded_modules


# Using the more robust path_to_module from previous iteration
def path_to_module(file_path: str, src_root_abs: str) -> str | None:
    """Converts an absolute file path within the src root to a module path."""
    # Ensure src_root_abs ends with a separator for clean replacement
    src_root_abs_norm = os.path.join(src_root_abs, "")
    if not file_path.startswith(src_root_abs_norm):
        # Handle cases where file_path might not have trailing sep but src_root does
        if (
            file_path == os.path.normpath(src_root_abs)
            and os.path.basename(file_path) == "__init__.py"
        ):
            # Special case for src_root/__init__.py
            pass  # Will be handled below
        else:
            print(
                f"Warning: File '{file_path}' not under src_root '{src_root_abs_norm}'. Skipping."
            )
            return None

    # Remove root, replace / with ., remove .py
    relative_path = file_path[len(src_root_abs_norm) :]
    module_path = relative_path.replace(os.sep, ".")
    if module_path.endswith(".py"):
        module_path = module_path[:-3]

    # Handle __init__.py -> package name
    if module_path.endswith(".__init__"):
        module_path = module_path[: -len(".__init__")]
    elif module_path == "__init__":  # Handle top-level __init__.py
        # Return the name of the source directory itself as the module
        module_path = os.path.basename(src_root_abs)

    # Add the src directory name as the root if not already present
    # Assumes src_root_abs is something like /app/src
    src_dir_name = os.path.basename(src_root_abs)
    if not module_path.startswith(src_dir_name + ".") and module_path != src_dir_name:
        if (
            module_path
        ):  # Avoid prefixing if module_path became empty (e.g., was just __init__)
            module_path = f"{src_dir_name}.{module_path}"
        elif (
            os.path.basename(file_path) == "__init__.py"
        ):  # Handle /app/src/__init__.py explicitly
            module_path = src_dir_name

    # Skip empty/invalid module paths
    if not module_path or module_path.endswith("."):
        return None

    return module_path


# Using the more robust find_all_src_modules logic
def find_all_src_modules(src_dir_abs: str) -> Set[str]:
    """Find all Python modules within the src directory."""
    all_modules = set()
    if not os.path.isdir(src_dir_abs):
        print(f"Error: Source directory '{src_dir_abs}' not found or not a directory.")
        return all_modules

    src_dir_abs = os.path.abspath(src_dir_abs)

    for root, dirs, files in os.walk(src_dir_abs, topdown=True):
        # Prune __pycache__ directories
        dirs[:] = [d for d in dirs if d != "__pycache__"]

        # Process Python files
        for file in files:
            if file.endswith(".py"):
                full_path = os.path.join(root, file)
                # Use parent directory as root for top-level __init__.py
                current_src_root = (
                    os.path.dirname(src_dir_abs)
                    if file == "__init__.py" and root == src_dir_abs
                    else src_dir_abs
                )
                module_name = path_to_module(full_path, current_src_root)
                if module_name:
                    all_modules.add(module_name)

    return all_modules


def main():
    # Use argparse as provided by user
    parser = argparse.ArgumentParser(
        description="Analyze runtime results to find unused modules."
    )
    parser.add_argument(
        "--src-dir", default="/app/src", help="Directory containing source code."
    )
    parser.add_argument(
        "--report-dir", default="/app/reports", help="Directory to save the report."
    )
    args = parser.parse_args()

    src_dir = args.src_dir
    report_dir = args.report_dir
    output_file = os.path.join(report_dir, "unused_modules.json")

    print(f"--- Analyzing Source Modules in: {src_dir} ---")
    print("--- Reading logs from stdin --- ")
    # Read logs from standard input
    logs = sys.stdin.read().splitlines()
    print(f"Read {len(logs)} lines from stdin.")

    # --- Step 1: Extract Loaded Modules ---
    print("--- Step 1: Extracting Loaded Modules from Logs ---")
    loaded_modules = extract_loaded_modules(logs)
    print(
        f"Found {len(loaded_modules)} unique loaded modules matching '{LOG_SEARCH_PREFIX}*'."
    )
    if not loaded_modules:
        print("Warning: No loaded modules found in logs. Analysis might be inaccurate.")

    # --- Step 2: Find All Modules in Source --- #
    print(f"--- Step 2: Finding All Modules in '{src_dir}' ---")
    all_src_modules = find_all_src_modules(src_dir)
    print(f"Found {len(all_src_modules)} total Python modules in source.")
    if not all_src_modules:
        print(f"Error: No Python modules found in '{src_dir}'. Check path. Aborting.")
        sys.exit(1)  # Exit if no source modules found

    # --- Step 3: Calculate Unused --- #
    print("--- Step 3: Calculating Unused Modules ---")
    potentially_unused = all_src_modules - loaded_modules

    # Apply manual ignores (using user-provided set directly is difficult here, let's filter)
    final_unused = set()
    ignored_count = 0
    for module in potentially_unused:
        is_ignored = False
        for ignore_pattern in ALWAYS_IGNORE_MODULES:
            if module == ignore_pattern or module.startswith(ignore_pattern + "."):
                is_ignored = True
                break
        if is_ignored:
            ignored_count += 1
        else:
            final_unused.add(module)

    print(f"Total modules found: {len(all_src_modules)}")
    print(f"Modules loaded during runtime: {len(loaded_modules)}")
    print(f"Potentially unused modules (Total - Loaded): {len(potentially_unused)}")
    print(f"Manually ignored modules/packages: {ignored_count}")
    print(f"Final count of unused modules: {len(final_unused)}")

    # --- Step 4: Save and Print Results --- #
    print(f"--- Step 4: Saving Results to {output_file} ---")
    # Ensure the report directory exists inside the container
    try:
        os.makedirs(report_dir, exist_ok=True)
        print(f"Ensured output directory exists: {report_dir}")
    except OSError as e:
        print(f"Error creating output directory '{report_dir}': {e}")
        sys.exit(1)

    unused_list = sorted(list(final_unused))
    try:
        with open(output_file, "w") as f:
            json.dump(unused_list, f, indent=2)
        print("Unused module list saved successfully.")
    except IOError as e:
        print(f"Error writing results to '{output_file}': {e}")
        sys.exit(1)

    if unused_list:
        print("\nUnused Modules Found: (Check JSON file for full list)")
    else:
        print("\nNo unused modules identified!")


if __name__ == "__main__":
    main()
