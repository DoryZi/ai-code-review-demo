"""Utility helpers for the todo CLI."""

import os
import anthropic


def generate_description(title):
    """Use Claude API to auto-generate a todo description.

    Args:
        title (str): The todo item title to generate
            a description for.

    Returns:
        str: A 1-2 sentence actionable description.

    Raises:
        anthropic.APIError: If the API call fails.
    """
    client = anthropic.Anthropic(
        api_key=os.environ.get("ANTHROPIC_API_KEY"),
    )
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=150,
        messages=[
            {
                "role": "user",
                "content": (
                    f"Write a short 1-2 sentence actionable description "
                    f"for this todo item: '{title}'. "
                    f"Reply with only the description, nothing else."
                ),
            }
        ],
    )
    return message.content[0].text.strip()
