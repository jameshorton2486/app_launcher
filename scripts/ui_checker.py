#!/usr/bin/env python
"""
UI Consistency Checker
Validates design system compliance across the codebase.

Usage:
    python scripts/ui_checker.py
    python scripts/ui_checker.py --fix  # Auto-fix simple issues
"""

import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple
from dataclasses import dataclass
from collections import defaultdict


@dataclass
class Issue:
    """Represents a UI consistency issue."""
    file: Path
    line: int
    category: str
    message: str
    severity: str  # "error", "warning", "info"
    suggestion: str = ""


class UIChecker:
    """Checks UI consistency across Python files."""

    # Patterns to detect
    PATTERNS = {
        # Magic color literals (hex colors not from theme)
        "hardcoded_color": {
            "pattern": r'["\']#[0-9a-fA-F]{6}["\']',
            "message": "Hardcoded color literal",
            "severity": "warning",
            "suggestion": "Use COLORS['key'] from src/theme.py",
            "exceptions": ["#ffffff", "#000000", "#ff00ff", "#FFFFFF"]  # Common defaults
        },

        # Magic padding/margin numbers
        "magic_padding": {
            "pattern": r'pad[xy]=\d+(?!\s*#)',
            "message": "Magic padding number",
            "severity": "info",
            "suggestion": "Consider using SPACING['key'] from src/theme.py"
        },

        # Direct CTkButton usage (potential Button3D candidate)
        "ctk_button": {
            "pattern": r'ctk\.CTkButton\s*\(',
            "message": "CTkButton found (review for Button3D replacement)",
            "severity": "info",
            "suggestion": "Consider Button3D for prominent actions"
        },

        # Missing theme import
        "missing_theme_import": {
            "pattern": r'^(?!.*from\s+utils\.theme\s+import).*THEME\.',
            "message": "THEME used without import",
            "severity": "error",
            "suggestion": "Add: from src.theme import COLORS"
        },

        # Hardcoded font sizes
        "hardcoded_font": {
            "pattern": r'font=\([^)]*\d{2}[^)]*\)',
            "message": "Hardcoded font configuration",
            "severity": "info",
            "suggestion": "Consider using FONTS['size_*'] from src/theme.py"
        },

        "bare_except": {
            "pattern": r"except\s*:",
            "message": "Bare except clause (catches SystemExit/KeyboardInterrupt)",
            "severity": "warning",
            "suggestion": "Use 'except Exception:' or a more specific type",
        },

        "hardcoded_font_size": {
            "pattern": r"font\s*=\s*\(['\"][^'\"]+['\"],\s*\d+",
            "message": "Hardcoded font size in font tuple",
            "severity": "info",
            "suggestion": "Use FONTS['size_*'] from theme.py",
        }
    }

    # Files/patterns to skip
    SKIP_PATTERNS = [
        "**/venv/**",
        "**/__pycache__/**",
        "**/test_*.py",
        "**/*.pyc",
        "**/theme*.py",  # Theme files can have literals
        "**/design_system.json",
        "**/animation.py"
    ]

    def __init__(self, root_dir: Path):
        self.root = root_dir
        self.issues: List[Issue] = []
        self.stats = defaultdict(int)

    def check_all(self) -> List[Issue]:
        """Run all checks on the codebase."""
        self.issues = []

        # Find UI-related Python files only
        src_dir = self.root / "src"
        if not src_dir.exists():
            print(f"Warning: {src_dir} not found")
            return self.issues
        ui_roots = [
            src_dir / "app.py",
            src_dir / "components",
            src_dir / "tabs",
        ]
        for ui_path in ui_roots:
            if ui_path.is_file():
                if not self._should_skip(ui_path):
                    self._check_file(ui_path)
                continue
            if ui_path.is_dir():
                for py_file in ui_path.rglob("*.py"):
                    if self._should_skip(py_file):
                        continue
                    self._check_file(py_file)

        return self.issues

    def _should_skip(self, path: Path) -> bool:
        """Check if file should be skipped."""
        path_str = str(path)
        for pattern in self.SKIP_PATTERNS:
            if Path(path_str).match(pattern):
                return True
        return False

    def _check_file(self, path: Path) -> None:
        """Check a single file for issues."""
        try:
            content = path.read_text(encoding='utf-8', errors='replace')
            lines = content.split('\n')
        except Exception as e:
            print(f"Error reading {path}: {e}")
            return

        for line_num, line in enumerate(lines, 1):
            # Skip comments
            if line.strip().startswith('#'):
                continue

            for check_name, check_config in self.PATTERNS.items():
                pattern = check_config["pattern"]

                if re.search(pattern, line):
                    # Check exceptions
                    exceptions = check_config.get("exceptions", [])
                    if any(exc in line for exc in exceptions):
                        continue

                    self.issues.append(Issue(
                        file=path,
                        line=line_num,
                        category=check_name,
                        message=check_config["message"],
                        severity=check_config["severity"],
                        suggestion=check_config.get("suggestion", "")
                    ))
                    self.stats[check_name] += 1

    def check_required_components(self) -> None:
        """Verify required components exist in expected locations."""
        required = {
            "src/components/button_3d.py": ["Button3D", "BUTTON_COLORS"],
            "src/components/card_frame.py": ["CardFrame"],
            "src/components/status_bar.py": ["StatusBar", "StatusType"],
            "src/theme.py": ["COLORS", "FONTS", "SPACING"],
        }

        for file_path, expected_exports in required.items():
            full_path = self.root / file_path
            if not full_path.exists():
                self.issues.append(Issue(
                    file=full_path,
                    line=0,
                    category="missing_file",
                    message=f"Required file missing: {file_path}",
                    severity="error"
                ))
                continue

            content = full_path.read_text(encoding='utf-8', errors='replace')
            for export in expected_exports:
                if export not in content:
                    self.issues.append(Issue(
                        file=full_path,
                        line=0,
                        category="missing_export",
                        message=f"Expected export '{export}' not found",
                        severity="error"
                    ))

    def print_report(self) -> None:
        """Print formatted report."""
        print("\n" + "=" * 60)
        print("UI CONSISTENCY CHECK REPORT")
        print("=" * 60)

        if not self.issues:
            print("\n✅ No issues found! Great job!")
            return

        # Group by severity
        by_severity = defaultdict(list)
        for issue in self.issues:
            by_severity[issue.severity].append(issue)

        # Print errors first
        for severity in ["error", "warning", "info"]:
            issues = by_severity.get(severity, [])
            if not issues:
                continue

            icon = {"error": "❌", "warning": "⚠️", "info": "ℹ️"}[severity]
            print(f"\n{icon} {severity.upper()}S ({len(issues)})")
            print("-" * 40)

            # Group by file
            by_file = defaultdict(list)
            for issue in issues:
                by_file[issue.file].append(issue)

            for file, file_issues in by_file.items():
                rel_path = file.relative_to(self.root) if file.is_relative_to(self.root) else file
                print(f"\n  {rel_path}:")
                for issue in file_issues[:5]:  # Limit per file
                    print(f"    Line {issue.line}: {issue.message}")
                    if issue.suggestion:
                        print(f"      → {issue.suggestion}")
                if len(file_issues) > 5:
                    print(f"    ... and {len(file_issues) - 5} more")

        # Summary
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("-" * 40)
        print(f"  Total issues: {len(self.issues)}")
        print(f"  Errors: {len(by_severity['error'])}")
        print(f"  Warnings: {len(by_severity['warning'])}")
        print(f"  Info: {len(by_severity['info'])}")

        print("\nBy category:")
        for category, count in sorted(self.stats.items(), key=lambda x: -x[1]):
            print(f"  {category}: {count}")


def main():
    """Main entry point."""
    import argparse
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(description="UI Consistency Checker")
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Project root directory"
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Auto-fix simple issues (not implemented)"
    )

    args = parser.parse_args()

    checker = UIChecker(args.root)
    checker.check_all()
    checker.check_required_components()
    checker.print_report()

    # Exit with error code if errors found
    errors = [i for i in checker.issues if i.severity == "error"]
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
