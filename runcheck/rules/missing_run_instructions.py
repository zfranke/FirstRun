"""Rule: README should contain inline run instructions when a run method is detected."""

from runcheck.models import Finding, Severity
from runcheck.scanner.context import ScanContext


def check(ctx: ScanContext) -> list[Finding]:
    """Warn (or note) when no inline setup commands are found in the README."""
    if not ctx.run_methods:
        return []  # missing_start_method covers this case

    if ctx.readme_data.get("shell_commands"):
        return []  # inline commands exist, nothing to flag

    docs_links = ctx.readme_data.get("docs_links", [])
    if docs_links:
        links_str = ", ".join(docs_links[:2])
        return [
            Finding(
                rule_id="missing_run_instructions",
                severity=Severity.INFO,
                message="No inline setup commands in README — external docs found",
                detail=(
                    "Contributors are directed to external docs for setup instructions. "
                    "Consider adding the key steps inline for quicker onboarding. "
                    f"Linked docs: {links_str}"
                ),
            )
        ]

    return [
        Finding(
            rule_id="missing_run_instructions",
            severity=Severity.WARNING,
            message="README has no inline run commands",
            detail=(
                "Add code blocks showing how to install dependencies and start the project "
                "so new contributors can get up and running quickly."
            ),
        )
    ]
