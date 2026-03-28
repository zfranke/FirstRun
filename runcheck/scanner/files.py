"""File-system scanner: locate well-known files in a repository."""

from pathlib import Path

KNOWN_FILES: list[str] = [
    "README.md",
    "README.rst",
    "Dockerfile",
    "compose.yaml",
    "docker-compose.yml",
    "pyproject.toml",
    "requirements.txt",
    "package.json",
    "Makefile",
    ".env.example",
    ".env.sample",
    "start.sh",
    "run.sh",
    "setup.py",
    "setup.cfg",
]

# Maximum depth of subdirectories to recurse into
_MAX_DEPTH = 3

# Directories to skip during recursive scanning
_SKIP_DIRS = {
    ".git", "__pycache__", "node_modules", ".venv", "venv",
    ".tox", ".mypy_cache", ".pytest_cache", "dist", "build",
    ".eggs", "*.egg-info",
}


def _should_skip(name: str) -> bool:
    """Return True if a directory name should be skipped."""
    return name in _SKIP_DIRS or name.endswith(".egg-info")


def scan_files(repo_path: Path) -> list[str]:
    """Return known filenames found in *repo_path* and its subdirectories.

    Returns paths relative to *repo_path* (e.g. ``"src/Dockerfile"``).
    Root-level files are returned as bare names for backwards compatibility.
    """
    found: list[str] = []
    _scan_dir(repo_path, repo_path, found, depth=0)
    return found


def _scan_dir(base: Path, current: Path, found: list[str], depth: int) -> None:
    """Recursively scan *current* for known files up to *_MAX_DEPTH* levels."""
    if depth > _MAX_DEPTH:
        return

    try:
        entries = sorted(current.iterdir())
    except PermissionError:
        return

    known_set = set(KNOWN_FILES)
    for entry in entries:
        if entry.is_file() and entry.name in known_set:
            rel = entry.relative_to(base)
            found.append(str(rel).replace("\\", "/"))
        elif entry.is_dir() and not _should_skip(entry.name):
            _scan_dir(base, entry, found, depth + 1)
