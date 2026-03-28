"""Rule: repository must have a README file."""

from runcheck.models import Finding, Severity
from runcheck.scanner.context import ScanContext


def check(ctx: ScanContext) -> list[Finding]:
    """Return an ERROR finding if no README exists at the repository root."""
    if ctx.has_root_readme:
        return []

    # Check if there's a README somewhere in a subfolder
    has_subfolder_readme = "README.md" in ctx.basenames or "README.rst" in ctx.basenames
    if has_subfolder_readme:
        return [
            Finding(
                rule_id="missing_readme",
                severity=Severity.WARNING,
                message="No root-level README found (subfolder README detected)",
                detail=(
                    "A README was found in a subdirectory but not at the "
                    "repository root. Add a top-level README to help new users."
                ),
            )
        ]

    return [
        Finding(
            rule_id="missing_readme",
            severity=Severity.ERROR,
            message="No README found",
            detail="A README is essential for new users.",
        )
    ]
