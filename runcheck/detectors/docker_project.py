"""Detector: Docker Compose projects."""

from runcheck.models import RunMethod
from runcheck.scanner.context import ScanContext

_COMPOSE_FILES = {"compose.yaml", "docker-compose.yml"}


def detect(ctx: ScanContext) -> list[RunMethod]:
    """Return ``[RunMethod.DOCKER_COMPOSE]`` when a compose file is present."""
    if _COMPOSE_FILES.intersection(ctx.files):
        return [RunMethod.DOCKER_COMPOSE]
    return []
