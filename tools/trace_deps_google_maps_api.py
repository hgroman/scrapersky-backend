#!/usr/bin/env python
"""
MODIFIED: Trace dependencies specifically for src/routers/google_maps_api.py
"""
import json
import subprocess
import sys
import ast
from pathlib import Path
from collections import deque

ROOT = Path(__file__).resolve().parents[1]   # project root
REPORTS = ROOT / "reports"
REPORTS.mkdir(exist_ok=True)
SRC_DIR = ROOT / "src"

# --- AST Based Static Trace Helpers (Adapted from run_full_trace.py) --- #

class ImportVisitor(ast.NodeVisitor):
    """Collects project-specific imports (relative or starting with src_dir_name)."""
    def __init__(self, src_dir_name):
        self.imports = set()
        self.src_dir_name = src_dir_name

    def visit_Import(self, node):
        for alias in node.names:
            module_name = alias.name
            potential_file = SRC_DIR / (module_name + '.py')
            potential_pkg = SRC_DIR / module_name
            if module_name.startswith(self.src_dir_name + '.') or \
               ('.' not in module_name and potential_file.exists()) or \
               ('.' not in module_name and potential_pkg.is_dir() and (potential_pkg / '__init__.py').exists()):
                 self.imports.add(module_name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.level > 0:
            self.imports.add((node.module, node.level))
        elif node.module and node.module.startswith(self.src_dir_name + '.'):
            self.imports.add(node.module)
        self.generic_visit(node)

def resolve_import(imp, current_file_abs: Path, project_root: Path, src_path: Path) -> Path | None:
    """Resolves an import (string or tuple) to a *relative* Path object (relative to project_root) or None."""
    src_dir_name = src_path.name

    try:
        if isinstance(imp, tuple):
            module_name, level = imp
            current_dir = current_file_abs.parent
            anchor_dir = current_dir
            for _ in range(level - 1):
                anchor_dir = anchor_dir.parent

            module_parts = module_name.split('.') if module_name else []
            potential_target_base = anchor_dir.joinpath(*module_parts)

            potential_file = potential_target_base.with_suffix('.py')
            if potential_file.is_file() and str(potential_file).startswith(str(src_path)):
                return potential_file.relative_to(project_root)

            if potential_target_base.is_dir() and str(potential_target_base).startswith(str(src_path)):
                init_file = potential_target_base / '__init__.py'
                if init_file.is_file():
                    return init_file.relative_to(project_root)

        elif isinstance(imp, str):
            module_parts = []
            if imp.startswith(src_dir_name + '.'):
                module_parts = imp[len(src_dir_name)+1:].split('.')
            elif '.' not in imp:
                potential_file_in_src = src_path / (imp + '.py')
                potential_pkg_in_src = src_path / imp
                if potential_file_in_src.exists() or (potential_pkg_in_src.is_dir() and (potential_pkg_in_src / '__init__.py').exists()):
                     module_parts = [imp]
                else:
                    return None
            else:
                return None

            if not module_parts: return None

            base_path = src_path

            potential_file = base_path.joinpath(*module_parts).with_suffix('.py')
            if potential_file.is_file():
                return potential_file.relative_to(project_root)

            potential_dir = base_path.joinpath(*module_parts)
            if potential_dir.is_dir():
                init_file = potential_dir / '__init__.py'
                if init_file.is_file():
                    return init_file.relative_to(project_root)

    except ValueError:
        return None
    except Exception as e:
        print(f"Error resolving import '{imp}' in {current_file_abs.relative_to(project_root)}: {e}", file=sys.stderr)
        return None

    return None

def trace_static_ast(entry_point_rel: Path) -> set[str]:
    """Performs AST-based static import trace starting from a single entry point."""
    print(f"  Running AST trace on: {entry_point_rel}")
    project_root = ROOT
    src_path = SRC_DIR
    src_dir_name = src_path.name

    processed_files_abs = set()
    queue = deque()
    reachable_files_rel_set = set()

    abs_entry = (project_root / entry_point_rel).resolve()
    if abs_entry.is_file() and str(abs_entry).startswith(str(src_path)):
        queue.append(abs_entry)
        processed_files_abs.add(abs_entry)
        reachable_files_rel_set.add(str(entry_point_rel).replace('\\', '/'))
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
                if resolved_file_abs.is_file() and str(resolved_file_abs).startswith(str(src_path)) and resolved_file_abs not in processed_files_abs:
                    processed_files_abs.add(resolved_file_abs)
                    rel_path_str = str(resolved_path_rel).replace('\\', '/')
                    if not rel_path_str.endswith('/__init__.py'):
                         reachable_files_rel_set.add(rel_path_str)
                    queue.append(resolved_file_abs)

    print(f"    Found {len(reachable_files_rel_set)} src modules from {entry_point_rel} via AST trace")
    return reachable_files_rel_set

# --- Modified Main Function --- #

def main():
    print("=== Starting Google Maps API Router Trace ===")
    print(f"Project Root: {ROOT}")

    router_file_name = "google_maps_api.py"
    router_file = SRC_DIR / "routers" / router_file_name

    if not router_file.exists():
        print(f"Error: Router file {router_file} not found.", file=sys.stderr)
        sys.exit(1)

    router_rel_path = router_file.relative_to(ROOT)

    print(f"--- Tracing dependencies for: {router_rel_path} ---")
    ast_modules = trace_static_ast(router_rel_path)

    print(f"Total static src modules found from {router_rel_path} (AST): {len(ast_modules)}")

    output_filename = f"deps_{router_file_name.replace('.py', '')}.json"
    output_path = REPORTS / output_filename

    with output_path.open("w") as fp:
        json.dump(sorted(list(ast_modules)), fp, indent=2)
    print(f"Dependency list saved to: {output_path}")

    print("=== Trace Complete ===")
    return 0

if __name__ == "__main__":
    sys.exit(main())
