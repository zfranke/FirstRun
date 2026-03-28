# runcheck

**runcheck** audits a repository's *runnability* – how easy it is for a new
contributor to clone the project and actually run it.

It scans the repository for well-known files, parses the README, detects the
likely run method(s), and produces a confidence score with actionable findings.

---

## Installation

```bash
pip install -e .
```

For development (includes `pytest`):

```bash
pip install -e ".[dev]"
```

---

## Usage

```bash
# Basic audit of the current directory
runcheck .

# Audit a specific path
runcheck /path/to/repo

# Machine-readable JSON output
runcheck . --json

# Verbose output (show all details)
runcheck . --verbose
runcheck . -v
```

---

## What it checks

| Rule | Severity | Description |
|------|----------|-------------|
| `missing_readme` | ERROR | No README.md or README.rst found |
| `missing_start_method` | ERROR | No pyproject.toml, package.json, Makefile, compose file, or shell script |
| `missing_env_example` | WARNING | `.env` referenced or Docker used, but no `.env.example` / `.env.sample` |
| `readme_file_mismatch` | WARNING | README references files that don't exist in the repo |
| `readme_command_mismatch` | WARNING | README mentions tools (docker-compose, npm) without matching config files |

---

## Confidence score

Starts at **100** and deducts:
- **−30** per ERROR finding
- **−15** per WARNING finding
- **−5** per INFO finding

Clamped to **[0, 100]**. Colour-coded in the terminal:
- 🟢 ≥ 70 – green
- 🟡 ≥ 40 – yellow
- 🔴 < 40 – red

---

## Output

The default console output shows:

- Repo path and detected run method(s)
- Confidence score (colour coded)
- Human-readable summary
- Findings table (severity · rule · message)

Use `--json` to emit a machine-readable JSON object compatible with CI
pipelines and automated tooling.
