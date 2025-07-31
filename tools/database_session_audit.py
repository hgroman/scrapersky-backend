#!/usr/bin/env python3
"""
Database Session Anti-Pattern Audit Tool

This tool systematically scans the codebase for database session management
anti-patterns that can cause "idle in transaction" connections and block
database operations.

Usage:
    python tools/database_session_audit.py
    
    # Or run from docker:
    docker compose exec scrapersky python tools/database_session_audit.py
"""

import os
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Set
from dataclasses import dataclass


@dataclass
class AntiPatternMatch:
    file_path: str
    line_number: int
    line_content: str
    pattern_type: str
    severity: str
    description: str


class DatabaseSessionAuditor:
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.matches: List[AntiPatternMatch] = []
        
        # Context managers that handle transactions automatically
        self.transaction_context_managers = {
            "get_background_session",
            "get_session", 
            "session.begin",
            "async_session_maker"
        }
        
        # Manual transaction methods that shouldn't be mixed with context managers
        self.manual_transaction_methods = {
            "session.commit",
            "session.rollback", 
            "await session.commit",
            "await session.rollback"
        }

    def scan_for_anti_patterns(self) -> List[AntiPatternMatch]:
        """Scan the entire codebase for database session anti-patterns."""
        print("🔍 Starting Database Session Anti-Pattern Audit...")
        print("=" * 60)
        
        # Get all Python files in services, routers, and other relevant directories
        python_files = self._get_python_files()
        print(f"📁 Scanning {len(python_files)} Python files...")
        
        for file_path in python_files:
            self._scan_file(file_path)
        
        # Sort matches by severity and file path
        self.matches.sort(key=lambda x: (x.severity, x.file_path, x.line_number))
        
        return self.matches

    def _get_python_files(self) -> List[Path]:
        """Get all Python files to scan."""
        patterns = [
            "src/**/*.py",
            "tools/**/*.py",
            "scripts/**/*.py"
        ]
        
        files = []
        for pattern in patterns:
            files.extend(self.project_root.glob(pattern))
        
        # Filter out __pycache__ and other irrelevant files
        return [f for f in files if "__pycache__" not in str(f) and f.is_file()]

    def _scan_file(self, file_path: Path) -> None:
        """Scan a single file for anti-patterns."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Track context for multi-line analysis
            in_context_manager = False
            context_manager_type = None
            context_manager_start_line = 0
            indent_level = 0
            
            for line_num, line in enumerate(lines, 1):
                line_stripped = line.strip()
                
                # Skip empty lines and comments
                if not line_stripped or line_stripped.startswith('#'):
                    continue
                
                # Track context manager blocks
                if self._is_context_manager_start(line_stripped):
                    in_context_manager = True
                    context_manager_type = self._get_context_manager_type(line_stripped)
                    context_manager_start_line = line_num
                    indent_level = len(line) - len(line.lstrip())
                    continue
                
                # Check if we're exiting the context manager block
                if in_context_manager:
                    current_indent = len(line) - len(line.lstrip())
                    if current_indent <= indent_level and line_stripped and not line_stripped.startswith(('except', 'finally', 'else')):
                        in_context_manager = False
                        context_manager_type = None
                
                # Check for anti-patterns
                self._check_double_transaction_management(
                    file_path, line_num, line, line_stripped, 
                    in_context_manager, context_manager_type
                )
                self._check_missing_context_manager(file_path, line_num, line_stripped)
                self._check_session_leaks(file_path, line_num, line_stripped)
                self._check_transaction_in_loop(file_path, line_num, line_stripped)
                
        except Exception as e:
            print(f"⚠️  Error scanning {file_path}: {e}")

    def _is_context_manager_start(self, line: str) -> bool:
        """Check if line starts a database context manager."""
        patterns = [
            r'async\s+with\s+get_background_session\(\)',
            r'async\s+with\s+get_session\(\)',
            r'async\s+with\s+session\.begin\(\)',
            r'async\s+with\s+\w+_session\(\)',
        ]
        
        return any(re.search(pattern, line) for pattern in patterns)

    def _get_context_manager_type(self, line: str) -> str:
        """Identify which type of context manager is being used."""
        if 'get_background_session' in line:
            return 'get_background_session'
        elif 'get_session' in line:
            return 'get_session'
        elif 'session.begin' in line:
            return 'session.begin'
        return 'unknown'

    def _check_double_transaction_management(
        self, file_path: Path, line_num: int, full_line: str, 
        line_stripped: str, in_context_manager: bool, context_manager_type: str
    ) -> None:
        """Check for manual transaction management inside context managers."""
        if not in_context_manager:
            return
        
        # Look for manual commit/rollback inside context managers
        manual_tx_patterns = [
            r'await\s+session\.commit\(\)',
            r'await\s+session\.rollback\(\)',
            r'session\.commit\(\)',
            r'session\.rollback\(\)'
        ]
        
        for pattern in manual_tx_patterns:
            if re.search(pattern, line_stripped):
                self.matches.append(AntiPatternMatch(
                    file_path=str(file_path),
                    line_number=line_num,
                    line_content=line_stripped,
                    pattern_type="DOUBLE_TRANSACTION_MANAGEMENT",
                    severity="CRITICAL",
                    description=f"Manual transaction management inside {context_manager_type}() context manager. This causes 'idle in transaction' connections."
                ))

    def _check_missing_context_manager(self, file_path: Path, line_num: int, line: str) -> None:
        """Check for manual session management without context managers."""
        # Look for session creation without context manager
        if re.search(r'session\s*=\s*async_session_factory\(\)', line):
            # Check if this is inside a context manager (would be indented)
            if not line.startswith('    '):  # Not indented, likely at module level
                self.matches.append(AntiPatternMatch(
                    file_path=str(file_path),
                    line_number=line_num,
                    line_content=line.strip(),
                    pattern_type="MISSING_CONTEXT_MANAGER",
                    severity="HIGH",
                    description="Session created without context manager. May lead to connection leaks."
                ))

    def _check_session_leaks(self, file_path: Path, line_num: int, line: str) -> None:
        """Check for potential session leaks."""
        # Look for session creation in background tasks without proper cleanup
        if 'background_task_session_factory' in line and 'async with' not in line:
            self.matches.append(AntiPatternMatch(
                file_path=str(file_path),
                line_number=line_num,
                line_content=line.strip(),
                pattern_type="POTENTIAL_SESSION_LEAK",
                severity="MEDIUM",
                description="Background task session created without context manager."
            ))

    def _check_transaction_in_loop(self, file_path: Path, line_num: int, line: str) -> None:
        """Check for transaction management inside loops (potential performance issue)."""
        if re.search(r'for\s+\w+\s+in\s+', line) and 'session' in line:
            self.matches.append(AntiPatternMatch(
                file_path=str(file_path),
                line_number=line_num,
                line_content=line.strip(),
                pattern_type="TRANSACTION_IN_LOOP",
                severity="MEDIUM",
                description="Session operations inside loop. Consider batching for performance."
            ))

    def generate_report(self) -> str:
        """Generate a detailed audit report."""
        if not self.matches:
            return """
✅ DATABASE SESSION AUDIT - CLEAN
==================================

No database session anti-patterns detected.
All session management appears to follow best practices.
"""
        
        report_lines = [
            "❌ DATABASE SESSION AUDIT - ISSUES FOUND",
            "=" * 50,
            f"Found {len(self.matches)} potential issues:",
            ""
        ]
        
        # Group by severity
        by_severity = {}
        for match in self.matches:
            if match.severity not in by_severity:
                by_severity[match.severity] = []
            by_severity[match.severity].append(match)
        
        # Report critical issues first
        for severity in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
            if severity not in by_severity:
                continue
                
            matches = by_severity[severity]
            report_lines.extend([
                f"🚨 {severity} SEVERITY ({len(matches)} issues)",
                "-" * 40
            ])
            
            for match in matches:
                report_lines.extend([
                    f"📁 File: {match.file_path}",
                    f"📍 Line: {match.line_number}",
                    f"🔍 Pattern: {match.pattern_type}",
                    f"📝 Description: {match.description}",
                    f"💾 Code: {match.line_content}",
                    ""
                ])
        
        # Add remediation guidance
        report_lines.extend([
            "🛠️  REMEDIATION GUIDANCE",
            "=" * 30,
            "",
            "CRITICAL - Double Transaction Management:",
            "  ❌ async with get_background_session() as session:",
            "      await session.commit()  # DON'T DO THIS",
            "",
            "  ✅ async with get_background_session() as session:",
            "      # Context manager handles commit automatically",
            "",
            "HIGH - Missing Context Manager:",
            "  ❌ session = async_session_factory()",
            "      # Manual session management",
            "",
            "  ✅ async with get_background_session() as session:",
            "      # Automatic cleanup",
            "",
            "For more details, see:",
            "📚 Docs/Docs_27_Anti-Patterns/20250731_WF4_Double_Transaction_Management_CRITICAL.md"
        ])
        
        return "\n".join(report_lines)

    def save_report(self, filename: str = "database_session_audit_report.txt") -> None:
        """Save the audit report to a file."""
        report = self.generate_report()
        
        with open(filename, 'w') as f:
            f.write(report)
        
        print(f"📄 Report saved to: {filename}")


def main():
    """Run the database session audit."""
    auditor = DatabaseSessionAuditor()
    matches = auditor.scan_for_anti_patterns()
    
    # Print summary
    if matches:
        print(f"\n❌ AUDIT COMPLETE: {len(matches)} issues found")
        
        # Count by severity
        severity_counts = {}
        for match in matches:
            severity_counts[match.severity] = severity_counts.get(match.severity, 0) + 1
        
        for severity, count in severity_counts.items():
            print(f"   {severity}: {count} issues")
        
        print("\n" + "=" * 60)
        print(auditor.generate_report())
        
        # Save detailed report
        auditor.save_report()
        
    else:
        print("✅ AUDIT COMPLETE: No issues found!")
        print("All database session management follows best practices.")

    return len(matches)


if __name__ == "__main__":
    import sys
    
    issues_found = main()
    
    # Exit with error code if issues found (useful for CI/CD)
    sys.exit(1 if issues_found > 0 else 0)