"""Rule: repository must have a README file."""

from runcheck.models import Finding, Severity
from runcheck.scanner.context import ScanContext


def check(ctx: ScanContext) -> list[Finding]:
    """Return an ERROR finding if no README exists in the repository."""
    if "README.md" not in ctx.files and "README.rst" not in ctx.files:
        return [
            Finding(
                rule_id="missing_readme",
                severity=Severity.ERROR,
                message="No README found",
                detail="A README is essential for new users.",
            )
        ]
    return []
