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


def scan_files(repo_path: Path) -> list[str]:
    """Return a list of known filenames that exist directly inside *repo_path*.

    Only the base filename is returned, not the full path.
    """
    found: list[str] = []
    for name in KNOWN_FILES:
        if (repo_path / name).is_file():
            found.append(name)
    return found
