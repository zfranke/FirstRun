"""Detector: shell-script entry points (start.sh / run.sh)."""

from runcheck.models import RunMethod
from runcheck.scanner.context import ScanContext

_SCRIPT_FILES = {"start.sh", "run.sh"}


def detect(ctx: ScanContext) -> list[RunMethod]:
    """Return ``[RunMethod.SHELL_SCRIPT]`` when a shell entry-point is present."""
    if _SCRIPT_FILES.intersection(ctx.files):
        return [RunMethod.SHELL_SCRIPT]
    return []
