"""Scoring and summary generation for a completed scan."""

import posixpath

from runcheck.models import Finding, RunMethod, ScoreEntry, Severity
from runcheck.scanner.context import ScanContext

_SEVERITY_PENALTY: dict[Severity, int] = {
    Severity.ERROR: 30,
    Severity.WARNING: 15,
    Severity.INFO: 0,
}

# Positive rubric checks and their point values (must sum to 100)
_POSITIVE_CHECKS: list[tuple[str, int]] = [
    ("readme_present", 30),
    ("run_method_detected", 25),
    ("inline_commands", 20),
    ("config_files_match", 15),
    ("env_example", 10),
]


# Map run methods to the file basenames that trigger detection
_METHOD_SOURCE_BASENAMES: dict[RunMethod, set[str]] = {
    RunMethod.PYTHON: {"pyproject.toml", "requirements.txt", "setup.py", "setup.cfg"},
    RunMethod.NODE: {"package.json"},
    RunMethod.DOCKER_COMPOSE: {"compose.yaml", "docker-compose.yml"},
    RunMethod.DOCKER: {"Dockerfile"},
    RunMethod.MAKEFILE: {"Makefile"},
    RunMethod.SHELL_SCRIPT: {"start.sh", "run.sh"},
}


def _find_sources(ctx: ScanContext, target_basenames: set[str]) -> list[str]:
    """Return deduplicated basenames from *ctx.files* matching *target_basenames*."""
    seen: dict[str, None] = {}
    for f in ctx.files:
        bn = posixpath.basename(f)
        if bn in target_basenames:
            seen[bn] = None
    return list(seen)


def _readme_file(ctx: ScanContext) -> str:
    """Return the path to the README in the file list, or 'README.md'."""
    for f in ctx.files:
        if posixpath.basename(f).lower().startswith("readme"):
            return f
    return "README.md"


def _build_positive_rubric(ctx: ScanContext, findings: list[Finding]) -> list[ScoreEntry]:
    """Evaluate each positive rubric category and return earned entries."""
    rubric: list[ScoreEntry] = []
    finding_rules = {f.rule_id for f in findings}
    readme = _readme_file(ctx)

    # README present (+30)
    readme_findings = [f for f in findings if f.rule_id == "missing_readme"]
    if not readme_findings:
        rubric.append(ScoreEntry(description="README found", points=30, source=readme))
    elif readme_findings[0].severity == Severity.WARNING:
        # Subfolder README exists but no root README
        rubric.append(ScoreEntry(
            description="README found (subfolder only, no root README)",
            points=15,
            source=readme,
        ))
    else:
        rubric.append(ScoreEntry(description="README not found", points=0))

    # Run method detected (+25)
    if ctx.run_methods:
        labels = ", ".join(m.value for m in ctx.run_methods)
        # Collect source files for all detected methods
        method_sources: list[str] = []
        for m in ctx.run_methods:
            targets = _METHOD_SOURCE_BASENAMES.get(m, set())
            method_sources.extend(_find_sources(ctx, targets))
        # Shell detection from README commands (no disk file)
        if RunMethod.SHELL_SCRIPT in ctx.run_methods and not method_sources:
            method_sources.append(readme)
        source_str = ", ".join(dict.fromkeys(method_sources))  # dedupe, preserve order
        rubric.append(ScoreEntry(
            description=f"Run method detected ({labels})",
            points=25,
            source=source_str,
        ))
    else:
        rubric.append(ScoreEntry(description="No run method detected", points=0))

    # Inline setup commands in README (+20)
    has_commands = bool(ctx.readme_data.get("shell_commands"))
    if has_commands:
        rubric.append(ScoreEntry(description="Inline setup commands in README", points=20, source=readme))
    elif "missing_run_instructions" in finding_rules:
        rubric.append(ScoreEntry(description="No inline setup commands in README", points=0, source=readme))
    else:
        rubric.append(ScoreEntry(description="Inline setup commands in README", points=20, source=readme))

    # Config files consistent with README (+15)
    mismatch_rules = {"readme_file_mismatch", "readme_command_mismatch"}
    mismatches = [f for f in findings if f.rule_id in mismatch_rules]
    if not mismatches:
        rubric.append(ScoreEntry(description="README references match repo files", points=15, source=readme))
    else:
        rubric.append(ScoreEntry(description="README references have mismatches", points=0, source=readme))

    # Env example provided (+10)
    if "missing_env_example" not in finding_rules:
        env_sources = _find_sources(ctx, {".env.example", ".env.sample"})
        if env_sources:
            rubric.append(ScoreEntry(
                description=".env.example provided",
                points=10,
                source=", ".join(env_sources),
            ))
        else:
            rubric.append(ScoreEntry(
                description="No .env dependency detected",
                points=10,
            ))
    else:
        rubric.append(ScoreEntry(
            description=".env referenced but no .env.example found",
            points=0,
            source=readme,
        ))

    return rubric


def calculate_score(
    findings: list[Finding], ctx: ScanContext
) -> tuple[int, list[ScoreEntry]]:
    """Calculate a confidence score (0–100) and return the scoring rubric.

    Builds score from positive checks (earning up to 100) then deducts
    per finding severity:
    - ERROR   → −30
    - WARNING → −15
    - INFO    → 0 (finding only, no deduction)
    """
    rubric = _build_positive_rubric(ctx, findings)
    score = sum(entry.points for entry in rubric)

    # Rules whose impact is already baked into the positive rubric
    _RUBRIC_HANDLED = {"missing_readme", "missing_run_instructions", "missing_env_example"}

    # Apply penalties from findings not already handled by the rubric
    for finding in findings:
        if finding.rule_id in _RUBRIC_HANDLED:
            continue
        penalty = _SEVERITY_PENALTY.get(finding.severity, 0)
        if penalty > 0:
            score -= penalty
            rubric.append(
                ScoreEntry(
                    description=f"[{finding.severity.value}] {finding.message}",
                    points=-penalty,
                )
            )

    return max(0, min(100, score)), rubric


_METHOD_LABELS: dict[RunMethod, str] = {
    RunMethod.PYTHON: "Python",
    RunMethod.NODE: "Node.js",
    RunMethod.DOCKER_COMPOSE: "Docker Compose",
    RunMethod.DOCKER: "Docker",
    RunMethod.MAKEFILE: "Make",
    RunMethod.SHELL_SCRIPT: "shell script",
    RunMethod.UNKNOWN: "unknown",
}

_METHOD_DESCRIPTIONS: dict[RunMethod, str] = {
    RunMethod.PYTHON: "Python (install dependencies with pip, then run the main script)",
    RunMethod.NODE: "Node.js (install dependencies with npm/yarn, then run with node or npm start)",
    RunMethod.DOCKER_COMPOSE: "Docker Compose (run with `docker compose up`)",
    RunMethod.DOCKER: "Docker (build and run with `docker build` / `docker run`)",
    RunMethod.MAKEFILE: "Make (use `make` targets to build and run)",
    RunMethod.SHELL_SCRIPT: "shell script (execute the provided shell commands)",
    RunMethod.UNKNOWN: "an unknown method",
}


def generate_summary(ctx: ScanContext) -> str:
    """Generate a human-readable summary of how to run this repository."""
    methods = ctx.run_methods
    if not methods:
        return (
            "No obvious start method was detected. "
            "Consider adding a pyproject.toml, package.json, Makefile, "
            "compose.yaml, or a shell entry-point script."
        )

    labels = "/".join(_METHOD_LABELS.get(m, m.value) for m in methods)
    shell_commands = ctx.readme_data.get("shell_commands", [])
    docs_links = ctx.readme_data.get("docs_links", [])

    if shell_commands:
        shown = shell_commands[:3]
        steps = " → ".join(shown)
        suffix = f" (+ {len(shell_commands) - 3} more steps)" if len(shell_commands) > 3 else ""
        return f"This is a {labels} project. README setup: {steps}{suffix}"

    if docs_links:
        return f"This is a {labels} project. External setup docs: {docs_links[0]}"

    descriptions = [_METHOD_DESCRIPTIONS.get(m, str(m)) for m in methods]
    if len(descriptions) == 1:
        return f"This project uses {descriptions[0]}."
    joined = "; ".join(descriptions[:-1]) + f"; and {descriptions[-1]}"
    return f"This project supports multiple run methods: {joined}."
