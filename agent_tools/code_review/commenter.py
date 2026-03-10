"""Post review comments on a GitHub PR."""

import json
import os
import subprocess


def _get_head_sha():
    """Get current HEAD commit SHA.

    Returns:
        str: The 40-char commit SHA.

    Raises:
        subprocess.CalledProcessError: If git fails.
    """
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        capture_output=True, text=True, check=True,
    )
    return result.stdout.strip()


def _format_comment(finding):
    """Format a finding into a review comment body.

    Args:
        finding (Finding): The finding to format.

    Returns:
        str: Markdown-formatted comment string.
    """
    sev = finding.severity
    cat = finding.category
    body = f"**[{sev}/{cat}]** {finding.comment}"
    if finding.dont:
        body += f"\n\n**Don't:**\n```python\n{finding.dont}\n```"
    if finding.do:
        body += f"\n\n**Do:**\n```python\n{finding.do}\n```"
    return body


def post_review(pr_number, summary, findings,
                fix_doc="", cost=None):
    """Post a review with inline comments on a PR.

    Args:
        pr_number (int): The pull request number.
        summary (str): Overall review summary text.
        findings (list): List of Finding objects to
            post as inline comments.
        fix_doc (str): Markdown fix guide to append
            to the review body.
        cost (ReviewCost): Optional cost/usage data
            to include in the review comment.

    Returns:
        bool: True if review was posted successfully.

    Raises:
        subprocess.CalledProcessError: If gh api
            call fails.
    """
    repo = os.environ.get("GITHUB_REPOSITORY", "")
    sha = _get_head_sha()
    count = len(findings)
    body = f"## AI Code Review\n\n{summary}"
    if count:
        body += f"\n\n_{count} finding(s)_"
    if cost and cost.cost_usd > 0:
        body += (
            f"\n\n**Review cost:** ${cost.cost_usd:.4f} "
            f"({cost.input_tokens} in / "
            f"{cost.output_tokens} out)"
        )
    if fix_doc:
        body += f"\n\n---\n\n{fix_doc}"
    comments = []
    for f in findings:
        comments.append({
            "path": f.file,
            "line": f.line,
            "side": "RIGHT",
            "body": _format_comment(f),
        })
    payload = json.dumps({
        "commit_id": sha,
        "event": "COMMENT",
        "body": body,
        "comments": comments,
    })
    subprocess.run(
        [
            "gh", "api", "--method", "POST",
            f"repos/{repo}/pulls/{pr_number}/reviews",
            "--input", "-",
        ],
        input=payload,
        capture_output=True, text=True, check=True,
    )
    return True
