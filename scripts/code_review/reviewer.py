"""Invoke Claude CLI for code review."""

import json
import subprocess

from scripts.code_review.models import Finding
from scripts.code_review.prompt import REVIEW_PROMPT
from scripts.code_review.schema import REVIEW_SCHEMA


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
        json.JSONDecodeError: If Claude returns
            invalid JSON.
    """
    prompt = REVIEW_PROMPT.format(diff=diff_text)
    schema_str = json.dumps(REVIEW_SCHEMA)
    cmd = [
        "claude", "-p",
        "--output-format", "json",
        "--max-turns", "5",
        "--json-schema", schema_str,
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
    print(f"  Claude stdout: {result.stdout[:500]}")
    if result.stderr:
        print(f"  Claude stderr: {result.stderr[:500]}")
    data = json.loads(result.stdout)
    # Claude JSON mode wraps in {"result": ...}
    if "result" in data:
        inner = data["result"]
        if isinstance(inner, str):
            data = json.loads(inner)
        else:
            data = inner
    findings = [
        Finding(**f) for f in data.get("findings", [])
    ]
    return data.get("summary", ""), findings
