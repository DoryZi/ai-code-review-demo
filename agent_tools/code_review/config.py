"""Configuration settings for AI code review.

Edit these values to customize the review behavior.
"""

# Maximum diff size sent to the LLM (in characters).
# Diffs larger than this are truncated.
MAX_DIFF_CHARS = 100_000

# Max findings on a first/full review.
MAX_FINDINGS = 15

# Max findings on follow-up reviews (subsequent pushes).
MAX_FOLLOWUP_FINDINGS = 5

# Default OpenAI model when --provider openai is used.
DEFAULT_OPENAI_MODEL = "gpt-5.1-codex-mini"
