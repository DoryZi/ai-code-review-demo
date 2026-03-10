"""Data models for code review findings."""

from dataclasses import dataclass

SEVERITIES = ("critical", "warning", "suggestion", "nitpick")
CATEGORIES = (
    "bug", "security", "performance",
    "style", "testing", "logic",
)


@dataclass
class Finding:
    """A single code review finding from Claude.

    Args:
        file (str): Relative path to the file.
        line (int): Line number in the diff.
        severity (str): One of critical, warning,
            suggestion, or nitpick.
        category (str): One of bug, security, performance,
            style, testing, or logic.
        comment (str): The review comment text.
        dont (str): Code example of what NOT to do.
        do (str): Code example of the correct fix.

    Returns:
        Finding: An instance with all fields set.

    Raises:
        TypeError: If required fields are missing.
    """

    file: str
    line: int
    severity: str
    category: str
    comment: str
    dont: str = ""
    do: str = ""
