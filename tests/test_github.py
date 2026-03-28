"""Tests for the GitHub URL scanning module."""

from __future__ import annotations

import base64
from unittest.mock import MagicMock, patch

import pytest

from runcheck.github import build_context_from_url, is_github_url
from runcheck.scanner.context import ScanContext


# ---------------------------------------------------------------------------
# is_github_url
# ---------------------------------------------------------------------------


def test_is_github_url_valid() -> None:
    assert is_github_url("https://github.com/owner/repo") is True


def test_is_github_url_valid_http() -> None:
    assert is_github_url("http://github.com/owner/repo") is True


def test_is_github_url_local_path() -> None:
    assert is_github_url("/home/user/project") is False


def test_is_github_url_other_domain() -> None:
    assert is_github_url("https://gitlab.com/owner/repo") is False


def test_is_github_url_with_trailing_path() -> None:
    assert is_github_url("https://github.com/owner/repo/tree/main") is True


# ---------------------------------------------------------------------------
# build_context_from_url
# ---------------------------------------------------------------------------


def _encoded(text: str) -> str:
    """Return base64-encoded bytes of *text* as a string (mimics GitHub API)."""
    return base64.b64encode(text.encode()).decode()


@patch("runcheck.github.requests.get")
def test_build_context_from_url_basic(mock_get: MagicMock) -> None:
    """build_context_from_url returns a ScanContext with files and readme data."""
    # First call → /git/trees/HEAD?recursive=1 (tree listing)
    tree_response = MagicMock()
    tree_response.status_code = 200
    tree_response.json.return_value = {
        "tree": [
            {"path": "README.md", "type": "blob"},
            {"path": "pyproject.toml", "type": "blob"},
            {"path": "src", "type": "tree"},
        ]
    }

    # Second call → /readme
    readme_text = "# Hello\n\n```bash\npip install .\n```\n"
    readme_response = MagicMock()
    readme_response.status_code = 200
    readme_response.json.return_value = {"content": _encoded(readme_text)}

    mock_get.side_effect = [tree_response, readme_response]

    ctx = build_context_from_url("https://github.com/owner/myrepo")

    assert isinstance(ctx, ScanContext)
    assert ctx.repo_path == "github:owner/myrepo"
    assert "README.md" in ctx.files
    assert "pyproject.toml" in ctx.files
    assert "src" not in ctx.files  # directories excluded
    assert any("pip install" in block for block in ctx.readme_data["code_blocks"])


@patch("runcheck.github.requests.get")
def test_build_context_from_url_no_readme(mock_get: MagicMock) -> None:
    """build_context_from_url handles repos without a README (HTTP 404)."""
    tree_response = MagicMock()
    tree_response.status_code = 200
    tree_response.json.return_value = {
        "tree": [{"path": "Makefile", "type": "blob"}]
    }

    readme_response = MagicMock()
    readme_response.status_code = 404

    mock_get.side_effect = [tree_response, readme_response]

    ctx = build_context_from_url("https://github.com/owner/bare-repo")

    assert "Makefile" in ctx.files
    assert ctx.readme_data["code_blocks"] == []
    assert ctx.readme_data["shell_commands"] == []
    assert ctx.readme_data["referenced_files"] == []


def test_build_context_from_url_invalid() -> None:
    """build_context_from_url raises ValueError for non-GitHub URLs."""
    with pytest.raises(ValueError, match="Not a valid GitHub repository URL"):
        build_context_from_url("https://example.com/not-github")
