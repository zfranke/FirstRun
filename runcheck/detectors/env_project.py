"""Detector: shell-script entry points (start.sh / run.sh).

Despite the filename, this module detects shell-script-based run methods
(start.sh / run.sh), not environment-variable configuration.
"""

from runcheck.models import RunMethod
from runcheck.scanner.context import ScanContext

_SCRIPT_FILES = {"start.sh", "run.sh"}


def detect(ctx: ScanContext) -> list[RunMethod]:
    """Return ``[RunMethod.SHELL_SCRIPT]`` when a shell entry-point is present."""
    if _SCRIPT_FILES.intersection(ctx.files):
        return [RunMethod.SHELL_SCRIPT]
    return []
