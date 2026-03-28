"""JSON serialisation for scan results."""

from runcheck.models import ScanResult


def to_json(result: ScanResult) -> str:
    """Return a JSON string representation of *result*."""
    return result.model_dump_json(indent=2)
