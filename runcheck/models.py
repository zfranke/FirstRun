"""Pydantic v2 data models for runcheck."""

from enum import Enum
from typing import TypedDict

from pydantic import BaseModel


class ReadmeData(TypedDict):
    """Structured data extracted from a repository README."""

    code_blocks: list[str]
    shell_commands: list[str]
    referenced_files: list[str]
    docs_links: list[str]


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
    DOCKER = "DOCKER"
    PYTHON = "PYTHON"
    NODE = "NODE"
    MAKEFILE = "MAKEFILE"
    SHELL_SCRIPT = "SHELL_SCRIPT"
    UNKNOWN = "UNKNOWN"


class ScoreEntry(BaseModel):
    """A single line-item in the scoring rubric."""

    description: str
    points: int
    source: str = ""


class ScanResult(BaseModel):
    """Aggregated result of a full repository scan."""

    repo_path: str
    files_found: list[str]
    run_methods: list[RunMethod]
    findings: list[Finding]
    confidence_score: int
    rubric: list[ScoreEntry]
    summary: str
    container_info: str = ""
