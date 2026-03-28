"""Tests for the scanner module."""

from pathlib import Path

import pytest

from runcheck.scanner.files import scan_files
from runcheck.scanner.readme import (
    extract_code_blocks,
    extract_referenced_files,
    extract_shell_commands,
    parse_readme,
)
from runcheck.scanner.context import build_context


# ---------------------------------------------------------------------------
# scan_files
# ---------------------------------------------------------------------------


def test_scan_files_empty_dir(tmp_path: Path) -> None:
    """An empty directory should yield an empty file list."""
    assert scan_files(tmp_path) == []


def test_scan_files_finds_readme(tmp_path: Path) -> None:
    """scan_files should detect a README.md file."""
    (tmp_path / "README.md").write_text("# Hello")
    files = scan_files(tmp_path)
    assert "README.md" in files


def test_scan_files_finds_multiple(tmp_path: Path) -> None:
    """scan_files should detect several known files at once."""
    for name in ("README.md", "pyproject.toml", "Makefile", ".env.example"):
        (tmp_path / name).write_text("")
    files = scan_files(tmp_path)
    assert "README.md" in files
    assert "pyproject.toml" in files
    assert "Makefile" in files
    assert ".env.example" in files


# ---------------------------------------------------------------------------
# parse_readme
# ---------------------------------------------------------------------------


def test_parse_readme_empty(tmp_path: Path) -> None:
    """parse_readme on a README with no special content returns empty lists."""
    (tmp_path / "README.md").write_text("Just some plain text with no code blocks.")
    result = parse_readme(tmp_path)
    assert result["code_blocks"] == []
    assert result["shell_commands"] == []
    assert result["referenced_files"] == []


def test_parse_readme_missing(tmp_path: Path) -> None:
    """parse_readme when no README exists returns empty data."""
    result = parse_readme(tmp_path)
    assert result == {"code_blocks": [], "shell_commands": [], "referenced_files": [], "docs_links": []}


# ---------------------------------------------------------------------------
# extract_code_blocks
# ---------------------------------------------------------------------------


def test_extract_code_blocks() -> None:
    """Fenced code blocks should be extracted."""
    content = "Some text\n```bash\npip install .\n```\nMore text"
    blocks = extract_code_blocks(content)
    assert len(blocks) == 1
    assert "pip install ." in blocks[0]


def test_extract_code_blocks_multiple() -> None:
    """Multiple fenced code blocks should all be extracted."""
    content = "```\nblock one\n```\nMiddle\n```python\nblock two\n```"
    blocks = extract_code_blocks(content)
    assert len(blocks) == 2


def test_extract_code_blocks_empty() -> None:
    """Content with no code blocks returns an empty list."""
    assert extract_code_blocks("no code here") == []


# ---------------------------------------------------------------------------
# extract_shell_commands
# ---------------------------------------------------------------------------


def test_extract_shell_commands() -> None:
    """Lines starting with $ should be detected as shell commands."""
    content = "Run the app:\n\n$ python main.py\n\nOr use docker build ."
    cmds = extract_shell_commands(content)
    assert any("python" in c for c in cmds)


def test_extract_shell_commands_docker() -> None:
    """docker-compose command should be detected."""
    content = "Start services:\n\ndocker-compose up -d"
    cmds = extract_shell_commands(content)
    assert any("docker" in c for c in cmds)


def test_extract_shell_commands_empty() -> None:
    """Content without shell commands returns empty list."""
    assert extract_shell_commands("No commands here, just text.") == []


# ---------------------------------------------------------------------------
# extract_referenced_files
# ---------------------------------------------------------------------------


def test_extract_referenced_files() -> None:
    """File references like .env, compose.yaml should be found."""
    content = "Copy the .env.example to .env and edit compose.yaml."
    refs = extract_referenced_files(content)
    assert ".env.example" in refs or any(".env" in r for r in refs)


def test_extract_referenced_files_yaml() -> None:
    """YAML and TOML file references should be found."""
    content = "See config.yaml and pyproject.toml for settings."
    refs = extract_referenced_files(content)
    assert "config.yaml" in refs
    assert "pyproject.toml" in refs


def test_extract_referenced_files_empty() -> None:
    """Content with no file references returns empty list."""
    assert extract_referenced_files("No files mentioned here.") == []


# ---------------------------------------------------------------------------
# build_context (integration)
# ---------------------------------------------------------------------------


def test_build_context(tmp_path: Path) -> None:
    """build_context integrates file scanning and README parsing."""
    (tmp_path / "README.md").write_text(
        "# Test\n\n```bash\npython main.py\n```\n\nSee requirements.txt."
    )
    (tmp_path / "requirements.txt").write_text("requests\n")

    ctx = build_context(tmp_path)
    assert ctx.repo_path == str(tmp_path)
    assert "README.md" in ctx.files
    assert "requirements.txt" in ctx.files
    assert ctx.run_methods == []  # not yet populated
    assert isinstance(ctx.readme_data, dict)
