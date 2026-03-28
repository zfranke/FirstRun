"""Rule: README commands should be consistent with detected project files."""

import re

from runcheck.models import Finding, Severity
from runcheck.scanner.context import ScanContext

_DOCKER_COMPOSE_CMD_RE = re.compile(r"docker[\s-]compose\b", re.IGNORECASE)
_NPM_YARN_CMD_RE = re.compile(r"\b(?:npm|yarn)\b", re.IGNORECASE)
_COMPOSE_FILES = {"compose.yaml", "docker-compose.yml"}


def _commands_text(ctx: ScanContext) -> str:
    """Return a single string combining all shell commands from the README."""
    return " ".join(ctx.readme_data.get("shell_commands", []))


def check(ctx: ScanContext) -> list[Finding]:
    """Warn when README commands imply tools whose config files are absent."""
    findings: list[Finding] = []
    cmds = _commands_text(ctx)

    if _DOCKER_COMPOSE_CMD_RE.search(cmds) and not _COMPOSE_FILES.intersection(ctx.basenames):
        findings.append(
            Finding(
                rule_id="readme_command_mismatch",
                severity=Severity.WARNING,
                message="README references docker-compose commands but no compose file found",
                detail="Add a compose.yaml / docker-compose.yml or update the README.",
            )
        )

    if _NPM_YARN_CMD_RE.search(cmds) and "package.json" not in ctx.basenames:
        findings.append(
            Finding(
                rule_id="readme_command_mismatch",
                severity=Severity.WARNING,
                message="README references npm/yarn commands but no package.json found",
                detail="Add a package.json or update the README.",
            )
        )

    return findings
