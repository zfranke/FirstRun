"""README parser: extract code blocks, shell commands and file references."""

import re
from pathlib import Path

from runcheck.models import ReadmeData

# Fenced code block pattern (``` or ~~~), capturing optional language tag
_CODE_BLOCK_RE = re.compile(r"```(\w*)\n(.*?)```", re.DOTALL)

# Language tags that indicate config/data examples (not shell commands)
_CONFIG_LANGS = {"yaml", "yml", "json", "toml", "xml", "ini", "conf", "env"}

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

# External URLs that look like documentation or quickstart pages
_DOCS_URL_RE = re.compile(r"https?://[^\s<>\"'\]\)]+", re.IGNORECASE)
_DOCS_KEYWORD_RE = re.compile(
    r"quickstart|quick-start|getting.started|install|setup|deploy"
    r"|doc(?:s|umentation)|wiki|guide|tutorial",
    re.IGNORECASE,
)


def extract_code_blocks(content: str) -> list[str]:
    """Return the inner text of every fenced code block in *content*."""
    return [body for _lang, body in _CODE_BLOCK_RE.findall(content)]


def _classify_code_blocks(content: str) -> tuple[list[str], list[str]]:
    """Split code blocks into (shell_blocks, config_blocks) by language tag.

    Blocks tagged with config languages (yaml, json, etc.) go into
    config_blocks.  Everything else (bash, sh, docker, untagged, etc.)
    goes into shell_blocks.
    """
    shell_blocks: list[str] = []
    config_blocks: list[str] = []
    for lang, body in _CODE_BLOCK_RE.findall(content):
        if lang.lower() in _CONFIG_LANGS:
            config_blocks.append(body)
        else:
            shell_blocks.append(body)
    return shell_blocks, config_blocks


def extract_shell_commands(content: str) -> list[str]:
    """Return lines that appear to be shell commands."""
    return [m.strip() for m in _SHELL_LINE_RE.findall(content)]


def extract_referenced_files(content: str) -> list[str]:
    """Return unique filenames referenced in *content*.

    Filters out files that appear to be example/placeholder paths
    (e.g. inside docker ``-v`` mounts or preceded by path separators).
    """
    results: dict[str, None] = {}
    for match in _FILE_REF_RE.finditer(content):
        filename = match.group(1)
        # Check context: skip if preceded by a path separator (e.g. /root/foo.yml,
        # /app/user-data/conf.yml) — these are example mount paths, not repo files.
        start = match.start()
        if start > 0 and content[start - 1] in ("/", "\\"):
            continue
        results[filename] = None
    return list(results)


def extract_docs_links(content: str) -> list[str]:
    """Return unique external documentation/quickstart URLs referenced in *content*."""
    seen: dict[str, None] = {}
    for url in _DOCS_URL_RE.findall(content):
        url = url.rstrip(".,;:!?)")
        if _DOCS_KEYWORD_RE.search(url):
            seen[url] = None
    return list(seen)


def parse_readme(repo_path: Path) -> ReadmeData:
    """Parse the repository README and return extracted metadata."""
    for name in ("README.md", "README.rst"):
        readme_path = repo_path / name
        if readme_path.is_file():
            content = readme_path.read_text(encoding="utf-8", errors="replace")
            code_blocks = extract_code_blocks(content)
            shell_blocks, _config_blocks = _classify_code_blocks(content)
            all_code = "\n".join(code_blocks)
            shell_only = "\n".join(shell_blocks)
            return ReadmeData(
                code_blocks=code_blocks,
                shell_commands=extract_shell_commands(all_code),
                referenced_files=extract_referenced_files(shell_only),
                docs_links=extract_docs_links(content),
            )

    return ReadmeData(code_blocks=[], shell_commands=[], referenced_files=[], docs_links=[])
