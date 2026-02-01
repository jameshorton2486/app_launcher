#!/usr/bin/env python
"""
UI Consistency Checker
Validates design system compliance across the codebase.

Usage:
    python scripts/ui_checker.py
    python scripts/ui_checker.py --root C:\\path\\to\\app_launcher
"""

import re
import sys
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass
from collections import defaultdict


@dataclass
class Issue:
    """Represents a UI consistency issue."""

    file: Path
    line: int
    category: str
    message: str
    severity: str
    suggestion: str = ""


class UIChecker:
    """Checks UI consistency across Python files."""

    PATTERNS = {
        "hardcoded_color": {
            "pattern": r'["\']#[0-9a-fA-F]{6}["\']',
            "message": "Hardcoded color literal",
            "severity": "warning",
            "suggestion": "Use THEME or COLORS constant instead",
            "exceptions": ["#ffffff", "#000000", "#ff00ff"],
        },
        "ctk_button": {
            "pattern": r"ctk\.CTkButton\s*\(",
            "message": "CTkButton found (review for Button3D)",
            "severity": "info",
            "suggestion": "Consider Button3D for prominent actions",
        },
    }

    SKIP_PATTERNS = [
        "**/venv/**",
        "**/__pycache__/**",
        "**/test_*.py",
        "**/*.pyc",
        "**/theme.py",
        "**/theme_extended.py",
        "**/animation.py",
        "**/design_system.json",
        "**/button_3d.py",
    ]

    REQUIRED_FILES = {
        "src/components/button_3d.py": ["Button3D", "BUTTON_COLORS"],
        "src/components/card_frame.py": ["CardFrame"],
        "src/components/status_bar.py": ["StatusBar", "StatusType"],
        "src/utils/theme_extended.py": ["THEME", "SPACING"],
    }

    def __init__(self, root_dir: Path):
        self.root = Path(root_dir).resolve()
        self.issues: List[Issue] = []
        self.stats = defaultdict(int)

    def check_all(self) -> List[Issue]:
        """Run all checks on the codebase."""
        self.issues = []
        src_dir = self.root / "src"
        if not src_dir.exists():
            return self.issues

        for py_file in src_dir.rglob("*.py"):
            if self._should_skip(py_file):
                continue
            self._check_file(py_file)

        self._check_required_components()
        return self.issues

    def _should_skip(self, path: Path) -> bool:
        path_str = str(path).replace("\\", "/")
        if "venv" in path_str or "__pycache__" in path_str:
            return True
        if path.name.startswith("test_"):
            return True
        if path.name in ("theme.py", "theme_extended.py", "animation.py", "button_3d.py"):
            return True
        return False

    def _check_file(self, path: Path) -> None:
        try:
            content = path.read_text(encoding="utf-8")
            lines = content.split("\n")
        except Exception as e:
            print(f"Error reading {path}: {e}", file=sys.stderr)
            return

        for line_num, line in enumerate(lines, 1):
            if line.strip().startswith("#"):
                continue

            for check_name, cfg in self.PATTERNS.items():
                if not re.search(cfg["pattern"], line):
                    continue
                exceptions = cfg.get("exceptions", [])
                if any(exc in line for exc in exceptions):
                    continue

                self.issues.append(
                    Issue(
                        file=path,
                        line=line_num,
                        category=check_name,
                        message=cfg["message"],
                        severity=cfg["severity"],
                        suggestion=cfg.get("suggestion", ""),
                    )
                )
                self.stats[check_name] += 1

    def _check_required_components(self) -> None:
        for rel_path, expected in self.REQUIRED_FILES.items():
            full_path = self.root / rel_path
            if not full_path.exists():
                self.issues.append(
                    Issue(
                        file=full_path,
                        line=0,
                        category="missing_file",
                        message=f"Required file missing: {rel_path}",
                        severity="error",
                    )
                )
                continue

            try:
                content = full_path.read_text(encoding="utf-8")
            except Exception:
                continue

            for export in expected:
                if export not in content:
                    self.issues.append(
                        Issue(
                            file=full_path,
                            line=0,
                            category="missing_export",
                            message=f"Expected export '{export}' not found in {rel_path}",
                            severity="error",
                        )
                    )

    def print_report(self) -> None:
        """Print formatted report."""
        print("\n" + "=" * 60)
        print("UI CONSISTENCY CHECK REPORT")
        print("=" * 60)

        if not self.issues:
            print("\nNo issues found.")
            return

        by_severity = defaultdict(list)
        for issue in self.issues:
            by_severity[issue.severity].append(issue)

        for severity in ["error", "warning", "info"]:
            issues = by_severity.get(severity, [])
            if not issues:
                continue

            icon = {"error": "[ERROR]", "warning": "[WARN]", "info": "[INFO]"}[severity]
            print(f"\n{icon} ({len(issues)})")
            print("-" * 40)

            by_file = defaultdict(list)
            for issue in issues:
                try:
                    rel = issue.file.relative_to(self.root)
                except ValueError:
                    rel = issue.file
                by_file[rel].append(issue)

            for file_path, file_issues in sorted(by_file.items(), key=lambda x: str(x[0])):
                print(f"\n  {file_path}:")
                for issue in file_issues[:8]:
                    loc = f"Line {issue.line}" if issue.line else ""
                    print(f"    {loc}: {issue.message}")
                    if issue.suggestion:
                        print(f"      -> {issue.suggestion}")
                if len(file_issues) > 8:
                    print(f"    ... and {len(file_issues) - 8} more")

        print("\n" + "=" * 60)
        print("SUMMARY")
        print("-" * 40)
        print(f"  Total: {len(self.issues)}")
        print(f"  Errors: {len(by_severity['error'])}")
        print(f"  Warnings: {len(by_severity['warning'])}")
        print(f"  Info: {len(by_severity['info'])}")


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="UI Consistency Checker")
    parser.add_argument(
        "--root",
        type=Path,
        default=None,
        help="Project root (default: parent of scripts/ or cwd)",
    )
    args = parser.parse_args()

    root = args.root
    if root is None:
        script_dir = Path(__file__).resolve().parent
        root = script_dir.parent if script_dir.name == "scripts" else Path.cwd()

    checker = UIChecker(root)
    checker.check_all()
    checker.print_report()

    errors = [i for i in checker.issues if i.severity == "error"]
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
