import ast
import json
import os


class SchedulerVisitor(ast.NodeVisitor):
    """Collects all scheduler.add_job(...) calls."""

    def __init__(self, filepath):
        self.filepath = filepath
        self.jobs = []

    def visit_Call(self, node):
        # Detect scheduler.add_job(...) calls
        if isinstance(node.func, ast.Attribute) and node.func.attr == "add_job":
            target = None
            if node.args:
                arg = node.args[0]
                if isinstance(arg, ast.Name):
                    target = arg.id
                elif isinstance(arg, ast.Attribute):
                    # Attempt to reconstruct the full attribute path (e.g., service.func)
                    try:
                        target = ast.unparse(arg)
                    except AttributeError:  # Handle cases where unparse might fail on older ast versions or complex structures
                        # Fallback or log error if needed
                        pass

            # Also check keyword arguments like 'func='
            if target is None:
                for keyword in node.keywords:
                    if keyword.arg == "func":
                        if isinstance(keyword.value, ast.Name):
                            target = keyword.value.id
                        elif isinstance(keyword.value, ast.Attribute):
                            try:
                                target = ast.unparse(keyword.value)
                            except AttributeError:
                                pass  # Fallback
                        elif isinstance(keyword.value, ast.Lambda):
                            target = f"<lambda in {os.path.basename(self.filepath)}>"  # Represent lambda functions

            if target:  # Only add if we successfully identified a target function
                self.jobs.append(
                    {
                        "file": self.filepath,
                        "lineno": node.lineno,
                        "target_function": target,  # More specific key name
                    }
                )
        self.generic_visit(node)


def parse_scheduler_jobs(src_dir, out_file):
    jobs = []
    project_root = os.path.abspath(
        os.path.join(src_dir, "..")
    )  # Get project root for relative paths

    for root, _, files in os.walk(src_dir):
        for fname in files:
            if not fname.endswith(".py") or fname == "__init__.py":
                continue
            path = os.path.join(root, fname)
            try:
                with open(path, "r", encoding="utf-8") as f:  # Specify encoding
                    tree = ast.parse(
                        f.read(), filename=path
                    )  # Pass filename for better errors
                # Make path relative to project root
                relative_path = os.path.relpath(path, project_root)
                visitor = SchedulerVisitor(relative_path)  # Use relative path
                visitor.visit(tree)
                jobs.extend(visitor.jobs)
            except SyntaxError as e:
                print(f"SyntaxError parsing {path}: {e}")
            except Exception as e:
                print(f"Error parsing {path}: {e}")  # Catch other potential errors

    # Ensure the output directory exists
    os.makedirs(os.path.dirname(out_file), exist_ok=True)

    with open(out_file, "w", encoding="utf-8") as f:  # Specify encoding
        json.dump(jobs, f, indent=2)
    print(f"Scheduler job analysis complete. Results saved to {out_file}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Trace APScheduler jobs")
    parser.add_argument(
        "--src", default="src", help="Source directory (relative to project root)"
    )
    parser.add_argument(
        "--out",
        default="reports/scheduler_jobs.json",
        help="Output JSON file (relative to project root)",
    )
    args = parser.parse_args()

    # Get absolute paths based on the script's location or a known project structure marker
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(
        os.path.join(script_dir, "..")
    )  # Assumes script is in tools/

    abs_src_dir = os.path.join(project_root, args.src)
    abs_out_file = os.path.join(project_root, args.out)

    if not os.path.isdir(abs_src_dir):
        print(f"Error: Source directory not found: {abs_src_dir}")
    else:
        parse_scheduler_jobs(abs_src_dir, abs_out_file)
