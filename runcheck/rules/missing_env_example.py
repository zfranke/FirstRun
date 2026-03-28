"""Rule: a .env.example or .env.sample should accompany env-var usage."""

from runcheck.models import Finding, Severity
from runcheck.scanner.context import ScanContext

_ENV_EXAMPLE_FILES = {".env.example", ".env.sample"}
_COMPOSE_FILES = {"compose.yaml", "docker-compose.yml", "Dockerfile"}


def _env_referenced_in_readme(ctx: ScanContext) -> bool:
    """Return True if the README mentions .env files (but not example variants)."""
    referenced = ctx.readme_data.get("referenced_files", [])
    return any(
        ".env" in f and f not in _ENV_EXAMPLE_FILES for f in referenced
    )


def check(ctx: ScanContext) -> list[Finding]:
    """Warn when env-var usage is implied but no .env example file exists."""
    has_example = bool(_ENV_EXAMPLE_FILES.intersection(ctx.files))
    if has_example:
        return []

    env_in_readme = _env_referenced_in_readme(ctx)
    has_docker = bool(_COMPOSE_FILES.intersection(ctx.files))

    if env_in_readme or has_docker:
        return [
            Finding(
                rule_id="missing_env_example",
                severity=Severity.WARNING,
                message="No .env.example or .env.sample found",
                detail=(
                    "Projects that use environment variables should ship a "
                    ".env.example file so new contributors know what to configure."
                ),
            )
        ]
    return []
