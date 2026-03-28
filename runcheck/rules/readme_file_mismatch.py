"""Rule: files referenced in the README should actually exist."""

from runcheck.models import Finding, Severity
from runcheck.scanner.context import ScanContext

_COMPOSE_ALIASES = {"compose.yaml", "docker-compose.yml"}

# File extensions that are typically invoked as commands, not config files
# a contributor needs to locate at the repo root.
_COMMAND_EXTENSIONS = {".sh"}


def _is_command_file(filename: str) -> bool:
    """Return True if the file looks like an executable script in a shell command."""
    return any(filename.endswith(ext) for ext in _COMMAND_EXTENSIONS)


def check(ctx: ScanContext) -> list[Finding]:
    """Warn about files the README mentions that are not present in the repo."""
    findings: list[Finding] = []
    files_set = ctx.basenames

    for ref in ctx.readme_data.get("referenced_files", []):
        if ref in files_set:
            continue

        # Skip .sh files — they may live in subdirectories or be
        # downloaded/created by the install process.
        if _is_command_file(ref):
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
