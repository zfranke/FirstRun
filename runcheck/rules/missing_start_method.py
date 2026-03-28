"""Rule: a repository must have at least one detectable start method."""

from runcheck.models import Finding, Severity
from runcheck.scanner.context import ScanContext


def check(ctx: ScanContext) -> list[Finding]:
    """Return an ERROR finding when no run method was detected."""
    if not ctx.run_methods:
        return [
            Finding(
                rule_id="missing_start_method",
                severity=Severity.ERROR,
                message="No obvious start method detected",
                detail=(
                    "Add a pyproject.toml, package.json, Makefile, "
                    "compose.yaml, or a start/run shell script."
                ),
            )
        ]
    return []
