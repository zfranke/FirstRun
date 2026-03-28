"""Rule: hint that containerisation is available when not mentioned in instructions."""

from runcheck.models import Finding, RunMethod, Severity
from runcheck.scanner.context import ScanContext

_CONTAINER_FILES = {"Dockerfile", "compose.yaml", "docker-compose.yml"}
_DOCKER_METHODS = {RunMethod.DOCKER, RunMethod.DOCKER_COMPOSE}


def check(ctx: ScanContext) -> list[Finding]:
    """Emit an INFO finding when Docker files exist but instructions don't mention them."""
    container_files = _CONTAINER_FILES.intersection(ctx.basenames)
    if not container_files:
        return []

    # If a Docker run method is already the primary documented path, skip
    docker_already_primary = bool(_DOCKER_METHODS.intersection(ctx.run_methods))
    shell_commands = ctx.readme_data.get("shell_commands", [])
    docker_in_cmds = any("docker" in cmd.lower() for cmd in shell_commands)

    if docker_already_primary and docker_in_cmds:
        return []

    files_str = ", ".join(sorted(container_files))
    return [
        Finding(
            rule_id="container_available",
            severity=Severity.INFO,
            message=f"Containerisation files found ({files_str})",
            detail=(
                "This project includes container configuration that can simplify "
                "deployment. Consider documenting `docker build`/`docker compose up` "
                "in the README if not already covered."
            ),
        )
    ]
