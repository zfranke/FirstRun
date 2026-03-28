"""ScanContext dataclass and the build_context factory function."""

from __future__ import annotations

import posixpath
from dataclasses import dataclass, field
from pathlib import Path

from runcheck.models import ReadmeData, RunMethod
from runcheck.scanner.files import scan_files
from runcheck.scanner.readme import parse_readme


@dataclass
class ScanContext:
    """Holds all gathered data about a repository during a scan pass."""

    repo_path: str
    files: list[str]
    readme_data: ReadmeData
    run_methods: list[RunMethod] = field(default_factory=list)

    @property
    def basenames(self) -> set[str]:
        """Return a set of base filenames from all found files."""
        return {posixpath.basename(f) for f in self.files}


def build_context(repo_path: Path) -> ScanContext:
    """Build and return a :class:`ScanContext` for the given local repository path."""
    files = scan_files(repo_path)
    readme_data = parse_readme(repo_path)
    return ScanContext(repo_path=str(repo_path), files=files, readme_data=readme_data)
