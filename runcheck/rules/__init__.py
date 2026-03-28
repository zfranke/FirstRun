"""Public API for the rules sub-package."""

from runcheck.models import Finding
from runcheck.rules import (
    container_available,
    missing_env_example,
    missing_readme,
    missing_run_instructions,
    missing_start_method,
    readme_command_mismatch,
    readme_file_mismatch,
)
from runcheck.scanner.context import ScanContext

_RULES = [
    missing_readme,
    missing_start_method,
    missing_env_example,
    missing_run_instructions,
    readme_file_mismatch,
    readme_command_mismatch,
    container_available,
]


def run_all_rules(ctx: ScanContext) -> list[Finding]:
    """Execute every rule and return the combined list of findings."""
    findings: list[Finding] = []
    for rule in _RULES:
        findings.extend(rule.check(ctx))
    return findings


__all__ = ["run_all_rules"]
