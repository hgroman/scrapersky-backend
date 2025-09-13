#!/usr/bin/env python3
"""
ScraperSky Enum Value Validator
Prevents the enum comparison/assignment bug that has repeatedly broken the codebase.

Usage: python -m linting_rules.scrapersky_enum_validator [files...]
"""

import ast
import sys
import argparse
from pathlib import Path
from typing import List, Set, Generator, Tuple

# Enum types from src/models/enums.py that need .value for database operations
ENUM_TYPES = {
    'ContactCurationStatus',
    'ContactProcessingStatus',
    'ContactEmailTypeEnum',
    'HubSpotSyncStatus',
    'HubSpotProcessingStatus',
    'SitemapCurationStatusEnum',
    'SitemapAnalysisStatusEnum',
    'SitemapImportCurationStatusEnum',
    'PageTypeEnum',
    'PageCurationStatusEnum',
    'LocalBusinessCurationStatusEnum'
}

class EnumUsageVisitor(ast.NodeVisitor):
    """AST visitor to detect enum comparison/assignment bugs"""

    def __init__(self, filename: str):
        self.filename = filename
        self.errors: List[Tuple[int, str]] = []
        self.imported_enums: Set[str] = set()

    def visit_ImportFrom(self, node: ast.ImportFrom):
        """Track enum imports to know which names to watch for"""
        if node.module and 'enums' in node.module:
            for alias in node.names:
                if alias.name in ENUM_TYPES:
                    self.imported_enums.add(alias.name)
        self.generic_visit(node)

    def visit_Compare(self, node: ast.Compare):
        """Check comparison operations for enum bugs - only SQLAlchemy model field comparisons"""
        # Only flag comparisons that look like SQLAlchemy field comparisons
        # Pattern: Model.field == EnumType.VALUE (SQLAlchemy)
        # Allow: enum_var == EnumType.VALUE (Python enum comparison)

        if (isinstance(node.left, ast.Attribute) and  # Model.field
            len(node.comparators) > 0):

            for comparator in node.comparators:
                if self._is_enum_without_value(comparator):
                    self.errors.append((
                        node.lineno,
                        f"SQLAlchemy enum comparison without .value: Use {self._get_node_name(comparator)}.value for database operations"
                    ))
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign):
        """Check assignments for enum bugs"""
        if self._is_enum_without_value(node.value):
            self.errors.append((
                node.lineno,
                f"Enum assignment without .value: Use {self._get_node_name(node.value)}.value for SQLAlchemy operations"
            ))
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        """Check function calls, specifically filters.append() pattern"""
        if (isinstance(node.func, ast.Attribute) and
            node.func.attr == 'append' and
            len(node.args) > 0):

            # Check if it's a comparison in the append
            arg = node.args[0]
            if isinstance(arg, ast.Compare):
                for comparator in arg.comparators:
                    if self._is_enum_without_value(comparator):
                        self.errors.append((
                            node.lineno,
                            f"CRITICAL filters.append() enum bug: Use {self._get_node_name(comparator)}.value - This exact pattern broke contacts filtering!"
                        ))
        self.generic_visit(node)

    def _is_enum_without_value(self, node: ast.AST) -> bool:
        """Check if node is an enum access without .value"""
        if not isinstance(node, ast.Attribute):
            return False

        # Check pattern: EnumType.VALUE (should be EnumType.VALUE.value)
        if (isinstance(node.value, ast.Name) and
            node.value.id in self.imported_enums):
            # This is EnumType.SOMETHING - check if it's missing .value
            return True

        # Check pattern: SomeEnum.VALUE (where SomeEnum contains known enum types)
        if (isinstance(node.value, ast.Name) and
            node.value.id in ENUM_TYPES):
            return True

        return False

    def _get_node_name(self, node: ast.AST) -> str:
        """Get readable name from AST node for error messages"""
        if isinstance(node, ast.Attribute):
            if isinstance(node.value, ast.Name):
                return f"{node.value.id}.{node.attr}"
        return "enum_value"

def check_file(filepath: Path) -> List[Tuple[int, str]]:
    """Check a single file for enum bugs"""
    try:
        content = filepath.read_text(encoding='utf-8')
        tree = ast.parse(content, filename=str(filepath))
        visitor = EnumUsageVisitor(str(filepath))
        visitor.visit(tree)
        return visitor.errors
    except Exception as e:
        return [(0, f"Failed to parse file: {e}")]

def main():
    parser = argparse.ArgumentParser(description='ScraperSky Enum Value Validator')
    parser.add_argument('files', nargs='*', help='Files to check')
    args = parser.parse_args()

    if not args.files:
        print("No files specified")
        return 0

    total_errors = 0
    for filepath in args.files:
        path = Path(filepath)
        if not path.exists():
            continue

        errors = check_file(path)
        if errors:
            print(f"\n{filepath}:")
            for line_no, message in errors:
                print(f"  Line {line_no}: {message}")
                total_errors += 1

    if total_errors > 0:
        print(f"\n💀 FOUND {total_errors} ENUM BUG(S) - These WILL cause SQLAlchemy runtime errors!")
        print("🔥 FIX: Add .value to all enum comparisons and assignments in SQLAlchemy operations")
        return 1
    else:
        print("✅ No enum bugs detected")
        return 0

if __name__ == '__main__':
    sys.exit(main())