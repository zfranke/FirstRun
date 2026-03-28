"""Rule: a .env.example or .env.sample should accompany env-var usage."""

import re

from runcheck.models import Finding, Severity
from runcheck.scanner.context import ScanContext

_ENV_EXAMPLE_FILES = {".env.example", ".env.sample"}

# Matches ".env" but not ".env.example" or ".env.sample"
_ENV_REF_RE = re.compile(r"\.env(?!\.example|\.sample)\b")


def _env_usage_detected(ctx: ScanContext) -> bool:
    """Return True if the project appears to rely on a .env file."""
    # Check referenced files in README
    for f in ctx.readme_data.get("referenced_files", []):
        if f == ".env" or (f.startswith(".env") and f not in _ENV_EXAMPLE_FILES):
            return True

    # Check shell commands for .env references (e.g. "cp .env.example .env")
    for cmd in ctx.readme_data.get("shell_commands", []):
        if _ENV_REF_RE.search(cmd):
            return True

    # Check code blocks for .env mentions
    for block in ctx.readme_data.get("code_blocks", []):
        if _ENV_REF_RE.search(block):
            return True

    return False


def check(ctx: ScanContext) -> list[Finding]:
    """Warn when .env usage is evident but no .env example file exists.

    Only fires when the README explicitly references .env files.
    Projects that don't use .env are not flagged.
    """
    if not _env_usage_detected(ctx):
        return []  # project doesn't use .env — nothing to flag

    has_example = bool(_ENV_EXAMPLE_FILES.intersection(ctx.basenames))
    if has_example:
        return []

    return [
        Finding(
            rule_id="missing_env_example",
            severity=Severity.WARNING,
            message="No .env.example or .env.sample found",
            detail=(
                "The README references .env files but no .env.example or "
                ".env.sample was found. New contributors won't know what "
                "environment variables to configure."
            ),
        )
    ]
