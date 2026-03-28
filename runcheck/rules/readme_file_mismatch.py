"""Rule: files referenced in the README should actually exist."""

from runcheck.models import Finding, Severity
from runcheck.scanner.context import ScanContext

_COMPOSE_ALIASES = {"compose.yaml", "docker-compose.yml"}


def check(ctx: ScanContext) -> list[Finding]:
    """Warn about files the README mentions that are not present in the repo."""
    findings: list[Finding] = []
    files_set = set(ctx.files)

    for ref in ctx.readme_data.get("referenced_files", []):
        if ref in files_set:
            continue

        # Special case: docker-compose.yml ↔ compose.yaml aliasing
        if ref in _COMPOSE_ALIASES and _COMPOSE_ALIASES.intersection(files_set):
            present = next(iter(_COMPOSE_ALIASES.intersection(files_set)))
            findings.append(
                Finding(
                    rule_id="readme_file_mismatch",
                    severity=Severity.WARNING,
                    message=f"README references '{ref}' but only '{present}' was found",
                    detail=(
                        "Consider updating the README to use the actual filename, "
                        "or rename the file to match."
                    ),
                )
            )
            continue

        findings.append(
            Finding(
                rule_id="readme_file_mismatch",
                severity=Severity.WARNING,
                message=f"README references '{ref}' but the file was not found",
                detail="Ensure referenced files exist or remove stale references from the README.",
            )
        )

    return findings
