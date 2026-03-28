"""Tests for the rules module."""

from pathlib import Path

import pytest

from runcheck.models import RunMethod, Severity
from runcheck.scanner.context import ScanContext
from runcheck.rules import missing_readme, missing_start_method, missing_env_example
from runcheck.rules import readme_file_mismatch


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _ctx(
    files: list[str] | None = None,
    run_methods: list[RunMethod] | None = None,
    readme_data: dict | None = None,
    repo_path: Path | None = None,
) -> ScanContext:
    return ScanContext(
        repo_path=repo_path or Path("."),
        files=files or [],
        readme_data=readme_data
        or {"code_blocks": [], "shell_commands": [], "referenced_files": []},
        run_methods=run_methods or [],
    )


# ---------------------------------------------------------------------------
# missing_readme
# ---------------------------------------------------------------------------


def test_missing_readme_no_files() -> None:
    """An ERROR finding is produced when no README is present."""
    findings = missing_readme.check(_ctx())
    assert len(findings) == 1
    assert findings[0].severity == Severity.ERROR
    assert findings[0].rule_id == "missing_readme"


def test_missing_readme_with_readme() -> None:
    """No finding when README.md is present."""
    findings = missing_readme.check(_ctx(files=["README.md"]))
    assert findings == []


def test_missing_readme_with_rst() -> None:
    """No finding when README.rst is present."""
    findings = missing_readme.check(_ctx(files=["README.rst"]))
    assert findings == []


# ---------------------------------------------------------------------------
# missing_start_method
# ---------------------------------------------------------------------------


def test_missing_start_method_empty() -> None:
    """An ERROR finding is produced when run_methods is empty."""
    findings = missing_start_method.check(_ctx())
    assert len(findings) == 1
    assert findings[0].severity == Severity.ERROR
    assert findings[0].rule_id == "missing_start_method"


def test_missing_start_method_with_methods() -> None:
    """No finding when at least one run method is detected."""
    findings = missing_start_method.check(_ctx(run_methods=[RunMethod.PYTHON]))
    assert findings == []


# ---------------------------------------------------------------------------
# readme_file_mismatch
# ---------------------------------------------------------------------------


def test_readme_file_mismatch() -> None:
    """A WARNING is produced when the README references a file not in ctx.files."""
    ctx = _ctx(
        files=["README.md"],
        readme_data={
            "code_blocks": [],
            "shell_commands": [],
            "referenced_files": ["requirements.txt"],
        },
    )
    findings = readme_file_mismatch.check(ctx)
    assert len(findings) == 1
    assert findings[0].severity == Severity.WARNING
    assert findings[0].rule_id == "readme_file_mismatch"


def test_readme_file_mismatch_no_issue() -> None:
    """No finding when all referenced files actually exist."""
    ctx = _ctx(
        files=["README.md", "requirements.txt"],
        readme_data={
            "code_blocks": [],
            "shell_commands": [],
            "referenced_files": ["requirements.txt"],
        },
    )
    findings = readme_file_mismatch.check(ctx)
    assert findings == []


def test_readme_file_mismatch_compose_alias() -> None:
    """Compose alias mismatch produces a specific WARNING (not generic missing)."""
    ctx = _ctx(
        files=["README.md", "compose.yaml"],
        readme_data={
            "code_blocks": [],
            "shell_commands": [],
            "referenced_files": ["docker-compose.yml"],
        },
    )
    findings = readme_file_mismatch.check(ctx)
    assert len(findings) == 1
    assert "compose.yaml" in findings[0].message


# ---------------------------------------------------------------------------
# missing_env_example
# ---------------------------------------------------------------------------


def test_missing_env_example_detected() -> None:
    """A WARNING is produced when .env is referenced but no example exists."""
    ctx = _ctx(
        files=["README.md"],
        readme_data={
            "code_blocks": [],
            "shell_commands": [],
            "referenced_files": [".env"],
        },
    )
    findings = missing_env_example.check(ctx)
    assert len(findings) == 1
    assert findings[0].severity == Severity.WARNING
    assert findings[0].rule_id == "missing_env_example"


def test_missing_env_example_present() -> None:
    """No WARNING when .env.example is already present."""
    ctx = _ctx(
        files=["README.md", ".env.example"],
        readme_data={
            "code_blocks": [],
            "shell_commands": [],
            "referenced_files": [".env"],
        },
    )
    findings = missing_env_example.check(ctx)
    assert findings == []


def test_missing_env_example_docker_triggers_warning() -> None:
    """A Dockerfile without .env.example triggers a WARNING."""
    ctx = _ctx(files=["README.md", "Dockerfile"])
    findings = missing_env_example.check(ctx)
    assert any(f.rule_id == "missing_env_example" for f in findings)
