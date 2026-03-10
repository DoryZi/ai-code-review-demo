"""Invoke Claude CLI for code review."""

import json
import re
import subprocess

from scripts.code_review.models import Finding
from scripts.code_review.prompt import REVIEW_PROMPT
EMPTY = {"summary": "No review generated.", "findings": []}


def _extract_json(text):
    """Extract first JSON object from text.

    Args:
        text (str): Raw text that may contain a
            JSON object among other content.

    Returns:
        dict: The parsed JSON object, or empty dict
            with summary if no JSON found.
    """
    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        return EMPTY
    try:
        return json.loads(match.group())
    except json.JSONDecodeError:
        print(f"  Failed to parse: {match.group()[:200]}")
        return EMPTY


def run_review(diff_text):
    """Send diff to Claude and parse findings.

    Args:
        diff_text (str): The unified diff text to
            review.

    Returns:
        tuple: A (summary, findings) tuple where
            summary is str and findings is list
            of Finding objects.

    Raises:
        subprocess.CalledProcessError: If the Claude
            CLI invocation fails.
    """
    prompt = REVIEW_PROMPT.format(diff=diff_text)
    cmd = [
        "claude", "-p",
        "--output-format", "json",
        "--max-turns", "5",
    ]
    print(f"  Claude cmd: {' '.join(cmd[:6])}...")
    print(f"  Prompt length: {len(prompt)} chars")
    result = subprocess.run(
        cmd,
        input=prompt,
        capture_output=True,
        text=True,
        check=True,
        timeout=300,
    )
    raw = result.stdout
    print(f"  Claude stdout: {raw[:500]}")
    if result.stderr:
        print(f"  Claude stderr: {result.stderr[:500]}")

    wrapper = json.loads(raw)
    inner = wrapper.get("result", "")

    if isinstance(inner, dict):
        data = inner
    elif isinstance(inner, str) and inner.strip():
        data = _extract_json(inner)
    else:
        print("  Warning: empty result from Claude")
        data = {"summary": "No review generated.", "findings": []}

    findings = [
        Finding(**f) for f in data.get("findings", [])
    ]
    return data.get("summary", ""), findings
