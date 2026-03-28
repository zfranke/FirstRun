# runcheck

**runcheck** audits a repository's *runnability* – how easy it is for a new
contributor to clone the project and actually run it.

It scans the repository for well-known files, parses the README, detects the
likely run method(s), and produces a confidence score with actionable findings.
Works on **local paths** and **GitHub URLs**.

---

## Installation

> **Requires Python 3.12+.** If `python` is not on your PATH, use `py -3` on Windows.

```bash
# Clone the repo
git clone https://github.com/zfranke/FirstRun.git
cd FirstRun

# Install (adds the `runcheck` command to your environment)
pip install -e .
```

> **Note:** After install, `runcheck` is placed in your Python Scripts folder.
> If it isn't on your PATH run it via `python -m runcheck` instead, or add
> the Scripts directory to PATH.
>
> On Windows with the `py` launcher you can always use:
> ```
> py -3 -m runcheck <target>
> ```

For development (includes `pytest`):

```bash
pip install -e ".[dev]"
```

---

## Usage

### Scan a local repository

```bash
# Audit the current directory
runcheck .

# Audit a specific path
runcheck /path/to/repo

# Or if runcheck isn't on your PATH:
py -3 -m runcheck .
```

### Scan a GitHub repository (no clone needed)

```bash
runcheck https://github.com/owner/repo
```

Set `GITHUB_TOKEN` to avoid GitHub API rate limits (60 req/hr unauthenticated → 5 000 req/hr authenticated):

```bash
# Windows
set GITHUB_TOKEN=ghp_yourtoken
runcheck https://github.com/owner/repo

# macOS / Linux
export GITHUB_TOKEN=ghp_yourtoken
runcheck https://github.com/owner/repo
```

### Output options

```bash
# Verbose: show file list and finding details
runcheck . --verbose
runcheck . -v

# Machine-readable JSON (useful in CI)
runcheck . --json
runcheck https://github.com/owner/repo --json
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
