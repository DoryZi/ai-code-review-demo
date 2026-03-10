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


@dataclass
class ReviewCost:
    """Cost and token usage from an LLM review call.

    Args:
        input_tokens (int): Number of input/prompt tokens.
        output_tokens (int): Number of output/completion
            tokens.
        cost_usd (float): Total cost in US dollars.
        provider (str): The LLM provider used.
        model (str): The model name used.

    Returns:
        ReviewCost: An instance with usage stats.

    Raises:
        TypeError: If required fields are missing.
    """

    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0.0
    provider: str = ""
    model: str = ""

    def __str__(self):
        """Format cost as a human-readable string."""
        return (
            f"${self.cost_usd:.4f} "
            f"({self.input_tokens}in/"
            f"{self.output_tokens}out) "
            f"[{self.provider}/{self.model}]"
        )
