"""ScanContext dataclass and the build_context factory function."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from runcheck.scanner.files import scan_files
from runcheck.scanner.readme import parse_readme


@dataclass
class ScanContext:
    """Holds all gathered data about a repository during a scan pass."""

    repo_path: Path
    files: list[str]
    readme_data: dict
    run_methods: list = field(default_factory=list)


def build_context(repo_path: Path) -> ScanContext:
    """Build and return a :class:`ScanContext` for the given repository path."""
    files = scan_files(repo_path)
    readme_data = parse_readme(repo_path)
    return ScanContext(repo_path=repo_path, files=files, readme_data=readme_data)
