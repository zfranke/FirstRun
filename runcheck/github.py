"""Fetch repository data from GitHub via the public REST API.

Supports both unauthenticated access and token-authenticated access
(set the GITHUB_TOKEN environment variable to avoid rate limits).

Typical usage::

    from runcheck.github import is_github_url, build_context_from_url

    if is_github_url(target):
        ctx = build_context_from_url(target)
"""

from __future__ import annotations

import base64
import os
import re

import requests

from runcheck.models import ReadmeData
from runcheck.scanner.context import ScanContext
from runcheck.scanner.files import KNOWN_FILES
from runcheck.scanner.readme import (
    _classify_code_blocks,
    extract_code_blocks,
    extract_docs_links,
    extract_referenced_files,
    extract_shell_commands,
)

# Matches https://github.com/owner/repo (with optional trailing path)
_GITHUB_URL_RE = re.compile(
    r"https?://github\.com/(?P<owner>[^/]+)/(?P<repo>[^/?\s#]+)"
)

_API_BASE = "https://api.github.com"


def is_github_url(target: str) -> bool:
    """Return True if *target* looks like a GitHub repository URL."""
    return bool(_GITHUB_URL_RE.match(target))


def _api_headers() -> dict[str, str]:
    """Build request headers, including a Bearer token when GITHUB_TOKEN is set."""
    headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _list_repo_files(owner: str, repo: str) -> list[str]:
    """Return KNOWN_FILES found anywhere in the repo tree (up to depth 3).

    Uses the Git Trees API with ``recursive=1`` so that a single request
    covers the entire repository, matching the local scanner behaviour.
    """
    url = f"{_API_BASE}/repos/{owner}/{repo}/git/trees/HEAD?recursive=1"
    response = requests.get(url, headers=_api_headers(), timeout=15)
    response.raise_for_status()

    known_set = set(KNOWN_FILES)
    found: list[str] = []
    for item in response.json().get("tree", []):
        if item["type"] != "blob":
            continue
        path: str = item["path"]
        # Honour the same depth limit as the local scanner
        if path.count("/") > 3:
            continue
        basename = path.rsplit("/", 1)[-1] if "/" in path else path
        if basename in known_set:
            found.append(path)
    return found


def _fetch_readme(owner: str, repo: str) -> ReadmeData:
    """Fetch and parse the default README via the GitHub API.

    Returns empty lists if no README exists (HTTP 404).
    """
    url = f"{_API_BASE}/repos/{owner}/{repo}/readme"
    response = requests.get(url, headers=_api_headers(), timeout=15)
    if response.status_code == 404:
        return ReadmeData(code_blocks=[], shell_commands=[], referenced_files=[], docs_links=[])
    response.raise_for_status()

    data = response.json()
    content = base64.b64decode(data.get("content", "")).decode("utf-8", errors="replace")
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


def build_context_from_url(url: str) -> ScanContext:
    """Build a :class:`ScanContext` by fetching repository data from GitHub.

    Args:
        url: A GitHub repository URL, e.g. ``https://github.com/owner/repo``.

    Raises:
        ValueError: If *url* is not a recognisable GitHub repository URL.
        requests.HTTPError: If the GitHub API returns a non-2xx status.
    """
    match = _GITHUB_URL_RE.match(url)
    if not match:
        raise ValueError(f"Not a valid GitHub repository URL: {url!r}")

    owner = match.group("owner")
    repo = match.group("repo").rstrip("/")

    files = _list_repo_files(owner, repo)
    readme_data = _fetch_readme(owner, repo)

    return ScanContext(
        repo_path=f"github:{owner}/{repo}",
        files=files,
        readme_data=readme_data,
    )
