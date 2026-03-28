"""Pydantic v2 data models for runcheck."""

from enum import Enum

from pydantic import BaseModel


class Severity(str, Enum):
    """Severity level for a finding."""

    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class Finding(BaseModel):
    """A single diagnostic finding produced by a rule check."""

    rule_id: str
    severity: Severity
    message: str
    detail: str = ""


class RunMethod(str, Enum):
    """Detected method(s) by which a repository can be run."""

    DOCKER_COMPOSE = "DOCKER_COMPOSE"
    PYTHON = "PYTHON"
    NODE = "NODE"
    MAKEFILE = "MAKEFILE"
    SHELL_SCRIPT = "SHELL_SCRIPT"
    UNKNOWN = "UNKNOWN"


class ScanResult(BaseModel):
    """Aggregated result of a full repository scan."""

    repo_path: str
    files_found: list[str]
    run_methods: list[RunMethod]
    findings: list[Finding]
    confidence_score: int
    summary: str
