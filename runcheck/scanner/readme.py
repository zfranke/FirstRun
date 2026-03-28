"""README parser: extract code blocks, shell commands and file references."""

import re
from pathlib import Path

# Fenced code block pattern (``` or ~~~)
_CODE_BLOCK_RE = re.compile(r"```[\w]*\n(.*?)```", re.DOTALL)

# Lines that look like shell commands
_SHELL_LINE_RE = re.compile(
    r"(?:^\s*\$\s+.+|"
    r"(?:docker|python|python3|pip|pip3|npm|npx|yarn|make|sh|bash|node)\b.+)",
    re.MULTILINE,
)

# Referenced filenames in prose or code.
# Uses (?<!\w) to avoid mid-word matches on the left side.
# Uses (?!\w) on the right side so that trailing sentence punctuation
# (e.g. a period in "see compose.yaml.") is not treated as part of the
# filename and does not suppress the match.
_FILE_REF_RE = re.compile(
    r"(?<!\w)"
    r"(\.env[\w.]*"
    r"|[\w][\w\-]*\.(?:env\w*|yaml|yml|toml|json|sh|txt)"
    r"|compose\.[\w]+"
    r"|docker-compose\.[\w]+)"
    r"(?!\w)"
)


def extract_code_blocks(content: str) -> list[str]:
    """Return the inner text of every fenced code block in *content*."""
    return _CODE_BLOCK_RE.findall(content)


def extract_shell_commands(content: str) -> list[str]:
    """Return lines that appear to be shell commands."""
    return [m.strip() for m in _SHELL_LINE_RE.findall(content)]


def extract_referenced_files(content: str) -> list[str]:
    """Return unique filenames referenced in *content*."""
    return list(dict.fromkeys(_FILE_REF_RE.findall(content)))


def parse_readme(repo_path: Path) -> dict:
    """Parse the repository README and return extracted metadata.

    Returns a dict with keys:
        - ``code_blocks``       – list of fenced-block bodies
        - ``shell_commands``    – list of detected shell command strings
        - ``referenced_files``  – list of filenames mentioned in the README
    """
    for name in ("README.md", "README.rst"):
        readme_path = repo_path / name
        if readme_path.is_file():
            content = readme_path.read_text(encoding="utf-8", errors="replace")
            return {
                "code_blocks": extract_code_blocks(content),
                "shell_commands": extract_shell_commands(content),
                "referenced_files": extract_referenced_files(content),
            }

    return {
        "code_blocks": [],
        "shell_commands": [],
        "referenced_files": [],
    }
