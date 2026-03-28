"""Scoring and summary generation for a completed scan."""

from runcheck.models import Finding, RunMethod, Severity
from runcheck.scanner.context import ScanContext

_SEVERITY_PENALTY = {
    Severity.ERROR: 30,
    Severity.WARNING: 15,
    Severity.INFO: 5,
}

_METHOD_DESCRIPTIONS: dict[RunMethod, str] = {
    RunMethod.PYTHON: "Python (install dependencies with pip, then run the main script)",
    RunMethod.NODE: "Node.js (install dependencies with npm/yarn, then run with node or npm start)",
    RunMethod.DOCKER_COMPOSE: "Docker Compose (run with `docker compose up`)",
    RunMethod.MAKEFILE: "Make (use `make` targets to build and run)",
    RunMethod.SHELL_SCRIPT: "shell script (execute start.sh or run.sh)",
    RunMethod.UNKNOWN: "an unknown method",
}


def calculate_score(ctx: ScanContext, findings: list[Finding]) -> int:
    """Calculate a confidence score (0–100) for a repository's runnability.

    Starts at 100 and deducts points per finding severity:
    - ERROR   → −30
    - WARNING → −15
    - INFO    → −5
    """
    score = 100
    for finding in findings:
        score -= _SEVERITY_PENALTY.get(finding.severity, 0)
    return max(0, min(100, score))


def generate_summary(ctx: ScanContext) -> str:
    """Generate a human-readable summary of how to run this repository."""
    methods = ctx.run_methods
    if not methods:
        return (
            "No obvious start method was detected. "
            "Consider adding a pyproject.toml, package.json, Makefile, "
            "compose.yaml, or a shell entry-point script."
        )

    descriptions = [_METHOD_DESCRIPTIONS.get(m, str(m)) for m in methods]

    if len(descriptions) == 1:
        return f"This project uses {descriptions[0]}."

    joined = "; ".join(descriptions[:-1]) + f"; and {descriptions[-1]}"
    return f"This project supports multiple run methods: {joined}."
