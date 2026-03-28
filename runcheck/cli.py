"""runcheck CLI entry point."""

import typer
from pathlib import Path

from runcheck.scanner import build_context
from runcheck.detectors import detect_run_methods
from runcheck.rules import run_all_rules
from runcheck.scoring import calculate_score, generate_summary
from runcheck.models import ScanResult
from runcheck.report import print_report, to_json

app = typer.Typer(help="Audit a repository's runnability for new users.")


@app.command()
def main(
    repo_path: Path = typer.Argument(..., help="Path to the repository to audit"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
) -> None:
    """Audit a repository and produce a run-confidence report."""
    ctx = build_context(repo_path)
    ctx.run_methods = detect_run_methods(ctx)
    findings = run_all_rules(ctx)
    score = calculate_score(ctx, findings)
    summary = generate_summary(ctx)
    result = ScanResult(
        repo_path=str(repo_path),
        files_found=ctx.files,
        run_methods=ctx.run_methods,
        findings=findings,
        confidence_score=score,
        summary=summary,
    )
    if json_output:
        print(to_json(result))
    else:
        print_report(result, verbose=verbose)
