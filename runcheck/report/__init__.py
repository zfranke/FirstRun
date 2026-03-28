"""Public API for the report sub-package."""

from runcheck.report.console import print_report
from runcheck.report.json_output import to_json

__all__ = ["print_report", "to_json"]
