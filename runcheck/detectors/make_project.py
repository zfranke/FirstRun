"""Detector: Makefile-driven projects."""

from runcheck.models import RunMethod
from runcheck.scanner.context import ScanContext


def detect(ctx: ScanContext) -> list[RunMethod]:
    """Return ``[RunMethod.MAKEFILE]`` when a Makefile is present."""
    if "Makefile" in ctx.files:
        return [RunMethod.MAKEFILE]
    return []
