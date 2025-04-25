import ast
import os
import json

class DynamicImportVisitor(ast.NodeVisitor):
    """Detects dynamic import patterns for human review."""
    def __init__(self, filepath):
        self.filepath = filepath
        self.entries = []

    def visit_Call(self, node):
        func = node.func
        # Check for importlib.import_module("module_name")
        if isinstance(func, ast.Attribute) and func.attr == 'import_module':
             # Ensure the object called upon is 'importlib' or similar
             if isinstance(func.value, ast.Name) and func.value.id == 'importlib':
                 if node.args and isinstance(node.args[0], (ast.Constant, ast.Str)): # Handle constants/strings
                     mod = node.args[0].value
                     self.entries.append({'file': self.filepath, 'lineno': node.lineno, 'type': 'importlib.import_module', 'module_name': mod})
                 elif node.args: # If arg is not a simple string, record the expression
                     mod_expr = ast.unparse(node.args[0])
                     self.entries.append({'file': self.filepath, 'lineno': node.lineno, 'type': 'importlib.import_module', 'module_expression': mod_expr})

        # Check for __import__("module_name")
        elif isinstance(func, ast.Name) and func.id == '__import__':
             if node.args and isinstance(node.args[0], (ast.Constant, ast.Str)): # Handle constants/strings
                 mod = node.args[0].value
                 self.entries.append({'file': self.filepath, 'lineno': node.lineno, 'type': '__import__', 'module_name': mod})
             elif node.args: # If arg is not a simple string, record the expression
                 mod_expr = ast.unparse(node.args[0])
                 self.entries.append({'file': self.filepath, 'lineno': node.lineno, 'type': '__import__', 'module_expression': mod_expr})

        self.generic_visit(node)


def detect_dynamic_imports(src_dir, out_file):
    results = []
    project_root = os.path.abspath(os.path.join(src_dir, '..')) # Get project root for relative paths

    for root, _, files in os.walk(src_dir):
        for fname in files:
            if not fname.endswith('.py') or fname == '__init__.py':
                continue
            path = os.path.join(root, fname)
            try:
                 with open(path, 'r', encoding='utf-8') as f: # Specify encoding
                     tree = ast.parse(f.read(), filename=path)
                 # Make path relative to project root
                 relative_path = os.path.relpath(path, project_root)
                 vis = DynamicImportVisitor(relative_path) # Use relative path
                 vis.visit(tree)
                 results.extend(vis.entries)
            except SyntaxError as e:
                 print(f"SyntaxError parsing {path}: {e}")
            except Exception as e:
                 print(f"Error parsing {path}: {e}") # Catch other potential errors

    # Ensure the output directory exists
    os.makedirs(os.path.dirname(out_file), exist_ok=True)

    with open(out_file, 'w', encoding='utf-8') as f: # Specify encoding
        json.dump(results, f, indent=2)
    print(f"Dynamic import analysis complete. Results saved to {out_file}")


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Detect dynamic imports')
    parser.add_argument('--src', default='src', help='Source directory (relative to project root)')
    parser.add_argument('--out', default='reports/dynamic_imports.json', help='Output JSON file (relative to project root)')
    args = parser.parse_args()

    # Get absolute paths based on the script's location or a known project structure marker
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, '..')) # Assumes script is in tools/

    abs_src_dir = os.path.join(project_root, args.src)
    abs_out_file = os.path.join(project_root, args.out)

    if not os.path.isdir(abs_src_dir):
        print(f"Error: Source directory not found: {abs_src_dir}")
    else:
        detect_dynamic_imports(abs_src_dir, abs_out_file)
