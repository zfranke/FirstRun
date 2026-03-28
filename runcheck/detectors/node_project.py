"""Detector: Node.js projects."""

from runcheck.models import RunMethod
from runcheck.scanner.context import ScanContext


def detect(ctx: ScanContext) -> list[RunMethod]:
    """Return ``[RunMethod.NODE]`` when a package.json is present."""
    if "package.json" in ctx.files:
        return [RunMethod.NODE]
    return []
