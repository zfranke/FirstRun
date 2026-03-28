"""Detector: Docker and Docker Compose projects."""

from runcheck.models import RunMethod
from runcheck.scanner.context import ScanContext

_COMPOSE_FILES = {"compose.yaml", "docker-compose.yml"}


def detect(ctx: ScanContext) -> list[RunMethod]:
    """Return Docker-related run methods when containerisation files are present."""
    methods: list[RunMethod] = []
    if _COMPOSE_FILES.intersection(ctx.basenames):
        methods.append(RunMethod.DOCKER_COMPOSE)
    if "Dockerfile" in ctx.basenames and RunMethod.DOCKER_COMPOSE not in methods:
        methods.append(RunMethod.DOCKER)
    return methods
