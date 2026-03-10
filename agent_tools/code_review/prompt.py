"""Review prompt loader.

Loads the system prompt and review template from
text files in the prompts/ directory so they can
be easily customized without editing Python code.
"""

from pathlib import Path

from agent_tools.code_review.config import MAX_FINDINGS

_PROMPTS_DIR = Path(__file__).parent / "prompts"


def _load(filename):
    """Load a prompt file from the prompts directory.

    Args:
        filename (str): Name of the file to load.

    Returns:
        str: The file contents.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    return (_PROMPTS_DIR / filename).read_text()


SYSTEM_PROMPT = _load("system.txt")

# Template with {diff} and {max_findings} placeholders.
_REVIEW_TEMPLATE = _load("review.txt")

# Pre-fill max_findings, leaving {diff} for runtime.
REVIEW_PROMPT = _REVIEW_TEMPLATE.replace(
    "{max_findings}", str(MAX_FINDINGS),
)
