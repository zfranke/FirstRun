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
