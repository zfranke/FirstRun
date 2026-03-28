"""Detector: shell-script entry points (start.sh / run.sh / README commands)."""

import re

from runcheck.models import RunMethod
from runcheck.scanner.context import ScanContext

_SCRIPT_FILES = {"start.sh", "run.sh"}

# Shell commands in README that indicate the project is run via shell
_SHELL_CMD_RE = re.compile(
    r"\b(?:curl|wget|sudo\s+bash|bash\s+\S+\.sh)\b", re.IGNORECASE
)


def detect(ctx: ScanContext) -> list[RunMethod]:
    """Return ``[RunMethod.SHELL_SCRIPT]`` when a shell entry-point is present.

    Detects via on-disk script files or README code-block commands
    (e.g. ``curl ... | bash``, ``sudo bash install.sh``).
    """
    if _SCRIPT_FILES.intersection(ctx.basenames):
        return [RunMethod.SHELL_SCRIPT]

    # Check README code-block shell commands for bash/curl/wget patterns
    for cmd in ctx.readme_data.get("shell_commands", []):
        if _SHELL_CMD_RE.search(cmd):
            return [RunMethod.SHELL_SCRIPT]

    return []
