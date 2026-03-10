"""Invoke an LLM for code review (Claude or OpenAI)."""

import json
import subprocess

from agent_tools.code_review.models import Finding, ReviewCost
from agent_tools.code_review.prompt import REVIEW_PROMPT
from agent_tools.code_review.openai_provider import review_openai
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
    decoder = json.JSONDecoder()
    start = text.find("{")
    if start == -1:
        return EMPTY
    try:
        obj, _ = decoder.raw_decode(text, start)
        return obj
    except json.JSONDecodeError:
        print(f"  Failed to parse: {text[start:start+200]}")
        return EMPTY


def _parse_findings(data):
    """Parse findings list from review data.

    Args:
        data (dict): Parsed JSON with summary and
            findings keys.

    Returns:
        tuple: A (summary, findings) tuple.
    """
    findings = [
        Finding(**f) for f in data.get("findings", [])
    ]
    return data.get("summary", ""), findings


def _extract_cost(wrapper):
    """Extract cost info from Claude CLI JSON wrapper.

    Args:
        wrapper (dict): The full JSON response from
            claude -p --output-format json.

    Returns:
        ReviewCost: Extracted cost and usage data.
    """
    usage = wrapper.get("usage", {})
    model_usage = wrapper.get("modelUsage", {})
    model_name = next(iter(model_usage), "unknown")
    return ReviewCost(
        input_tokens=usage.get("input_tokens", 0),
        output_tokens=usage.get("output_tokens", 0),
        cost_usd=wrapper.get("total_cost_usd", 0.0),
        provider="claude",
        model=model_name,
    )


def _review_claude(prompt):
    """Run review via Claude Code CLI.

    Args:
        prompt (str): The full review prompt.

    Returns:
        tuple: (review_data dict, ReviewCost).

    Raises:
        subprocess.CalledProcessError: If the Claude
            CLI invocation fails.
    """
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
    cost = _extract_cost(wrapper)
    inner = wrapper.get("result", "")

    if isinstance(inner, dict):
        return inner, cost
    if isinstance(inner, str) and inner.strip():
        data = _extract_json(inner)
        if not data.get("findings") and inner.strip():
            print("  Claude returned text, using as summary")
            return {"summary": inner.strip(), "findings": []}, cost
        return data, cost
    print("  Warning: empty result from Claude")
    return EMPTY, cost


def run_review(diff_text, provider="claude", model=""):
    """Send diff to an LLM and parse findings.

    Args:
        diff_text (str): The unified diff text to
            review.
        provider (str): LLM provider — "claude" uses
            the Claude Code CLI, "openai" calls the
            OpenAI API. Defaults to "claude".
        model (str): Model override. Only used for
            the openai provider. Defaults to gpt-4o.

    Returns:
        tuple: A (summary, findings, cost) tuple where
            summary is str, findings is list of Finding
            objects, and cost is a ReviewCost.

    Raises:
        ValueError: If provider is not supported.
    """
    prompt = REVIEW_PROMPT.format(diff=diff_text)
    cost = ReviewCost()

    if provider == "claude":
        data, cost = _review_claude(prompt)
    elif provider == "openai":
        m = model or "gpt-5.1-codex-mini"
        data, cost = review_openai(prompt, model=m,
                                   extract_json=_extract_json)
    else:
        raise ValueError(f"Unknown provider: {provider}")

    summary, findings = _parse_findings(data)
    return summary, findings, cost
