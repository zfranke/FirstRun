"""Detector: Python projects."""

from runcheck.models import RunMethod
from runcheck.scanner.context import ScanContext

_PYTHON_FILES = {"pyproject.toml", "requirements.txt", "setup.py", "setup.cfg"}


def detect(ctx: ScanContext) -> list[RunMethod]:
    """Return ``[RunMethod.PYTHON]`` when Python project files are present."""
    if _PYTHON_FILES.intersection(ctx.basenames):
        return [RunMethod.PYTHON]
    return []
