"""Rich-based console report renderer."""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
from rich.text import Text

from runcheck.models import ScanResult, Severity

_CONSOLE = Console()

_SEVERITY_STYLE = {
    Severity.ERROR: "bold red",
    Severity.WARNING: "yellow",
    Severity.INFO: "cyan",
}


def _score_color(score: int) -> str:
    if score >= 70:
        return "bold green"
    if score >= 40:
        return "bold yellow"
    return "bold red"


def print_report(result: ScanResult, verbose: bool = False) -> None:
    """Print a formatted runcheck report to the console using Rich."""
    _CONSOLE.rule("[bold]runcheck report[/bold]")

    # Header panel
    _CONSOLE.print(Panel(f"[bold]Repo:[/bold] {result.repo_path}", expand=False))

    # Confidence score
    color = _score_color(result.confidence_score)
    score_text = Text(f"Confidence score: {result.confidence_score}/100", style=color)
    _CONSOLE.print(score_text)

    # Run methods
    if result.run_methods:
        methods = ", ".join(m.value for m in result.run_methods)
        _CONSOLE.print(f"[bold]Run methods detected:[/bold] {methods}")
    else:
        _CONSOLE.print("[bold red]No run methods detected.[/bold red]")

    # Files found (verbose only)
    if verbose:
        _CONSOLE.print(f"[bold]Files found:[/bold] {', '.join(result.files_found) or 'none'}")

    # Summary
    _CONSOLE.print(f"\n[italic]{result.summary}[/italic]\n")

    # Container info
    if result.container_info:
        _CONSOLE.print(Panel(
            f"[bold]🐳 {result.container_info}[/bold]",
            title="Containerisation",
            border_style="blue",
            expand=False,
        ))
        _CONSOLE.print()

    # Scoring rubric
    rubric_table = Table(title="Score Rubric", box=box.SIMPLE, show_lines=False)
    rubric_table.add_column("Item", style="dim")
    rubric_table.add_column("Source", style="cyan", max_width=30, no_wrap=False)
    rubric_table.add_column("Points", justify="right", width=8)
    for entry in result.rubric:
        pts = f"+{entry.points}" if entry.points > 0 else str(entry.points)
        style = "green" if entry.points > 0 else ("red" if entry.points < -10 else "yellow")
        rubric_table.add_row(entry.description, entry.source, Text(pts, style=style))
    rubric_table.add_section()
    total_style = _score_color(result.confidence_score)
    rubric_table.add_row(
        Text("Total", style="bold"),
        "",
        Text(str(result.confidence_score), style=total_style),
    )
    _CONSOLE.print(rubric_table)
    _CONSOLE.print()

    # Findings table
    if result.findings:
        table = Table(title="Findings", box=box.ROUNDED, show_lines=True)
        table.add_column("Severity", style="bold", width=10)
        table.add_column("Rule", style="dim", width=25)
        table.add_column("Message")
        if verbose:
            table.add_column("Detail")

        for finding in result.findings:
            style = _SEVERITY_STYLE.get(finding.severity, "")
            row = [
                Text(finding.severity.value, style=style),
                finding.rule_id,
                finding.message,
            ]
            if verbose:
                row.append(finding.detail)
            table.add_row(*row)

        _CONSOLE.print(table)
    else:
        _CONSOLE.print("[bold green]✓ No findings – this repo looks great![/bold green]")
