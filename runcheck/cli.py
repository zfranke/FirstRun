"""runcheck CLI entry point."""

import sys
from pathlib import Path

import requests
import typer

from runcheck.detectors import detect_run_methods
from runcheck.github import build_context_from_url, is_github_url
from runcheck.models import RunMethod, ScanResult
from runcheck.report import print_report, to_json
from runcheck.rules import run_all_rules
from runcheck.scanner import build_context
from runcheck.scoring import calculate_score, generate_summary

app = typer.Typer(help="Audit a repository's runnability for new users.")

_CONTAINER_FILES = {"Dockerfile", "compose.yaml", "docker-compose.yml"}

_CONTAINER_HINTS: dict[str, str] = {
    "Dockerfile": "docker build -t <image> . && docker run <image>",
    "docker-compose.yml": "docker compose up",
    "compose.yaml": "docker compose up",
}


def _build_container_info(ctx) -> str:
    """Build a human-readable containerisation summary."""
    found = _CONTAINER_FILES.intersection(ctx.basenames)
    if not found:
        return ""

    # Check if docker commands are already in README
    shell_commands = ctx.readme_data.get("shell_commands", [])
    docker_in_readme = any("docker" in cmd.lower() for cmd in shell_commands)

    parts: list[str] = []
    for f in sorted(found):
        hint = _CONTAINER_HINTS.get(f, "")
        parts.append(f"{f} ({hint})" if hint else f)

    files_str = ", ".join(parts)
    if docker_in_readme:
        return f"Container deployment available and documented: {files_str}"
    return f"Container deployment available: {files_str}"


@app.command()
def main(
    target: str = typer.Argument(
        ..., help="Local path to a repository, or a GitHub URL (https://github.com/owner/repo)"
    ),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
) -> None:
    """Audit a repository and produce a run-confidence report.

    Accepts either a local directory path or a GitHub repository URL.
    Set the GITHUB_TOKEN environment variable to avoid API rate limits.
    """
    # --- 1. Scan repo & build context ---
    try:
        if is_github_url(target):
            ctx = build_context_from_url(target)
        else:
            repo_path = Path(target)
            if not repo_path.is_dir():
                typer.echo(f"Error: '{target}' is not a directory.", err=True)
                raise typer.Exit(1)
            ctx = build_context(repo_path)
    except requests.HTTPError as exc:
        typer.echo(f"GitHub API error: {exc}", err=True)
        if exc.response is not None and exc.response.status_code == 403:
            typer.echo(
                "Tip: set the GITHUB_TOKEN environment variable to increase your rate limit.",
                err=True,
            )
        raise typer.Exit(1)

    # --- 2. Detect run methods ---
    ctx.run_methods = detect_run_methods(ctx)

    # --- 3. Run rules ---
    findings = run_all_rules(ctx)

    # --- 4. Score ---
    score, rubric = calculate_score(findings, ctx)
    summary = generate_summary(ctx)

    # --- 4b. Container info ---
    container_info = _build_container_info(ctx)

    # --- 5. Render report ---
    result = ScanResult(
        repo_path=ctx.repo_path,
        files_found=ctx.files,
        run_methods=ctx.run_methods,
        findings=findings,
        confidence_score=score,
        rubric=rubric,
        summary=summary,
        container_info=container_info,
    )
    if json_output:
        print(to_json(result))
    else:
        print_report(result, verbose=verbose)
