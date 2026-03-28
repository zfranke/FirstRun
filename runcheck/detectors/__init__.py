"""Public API for the detectors sub-package."""

from runcheck.detectors import (
    docker_project,
    shell_project,
    make_project,
    node_project,
    python_project,
)
from runcheck.models import RunMethod
from runcheck.scanner.context import ScanContext

_DETECTORS = [
    python_project,
    node_project,
    docker_project,
    make_project,
    shell_project,
]


def detect_run_methods(ctx: ScanContext) -> list[RunMethod]:
    """Run all detectors and return the aggregated list of run methods."""
    methods: list[RunMethod] = []
    for detector in _DETECTORS:
        methods.extend(detector.detect(ctx))
    return methods


__all__ = ["detect_run_methods"]
