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
    return f"**[{sev}/{cat}]** {finding.comment}"


def post_review(pr_number, summary, findings):
    """Post a review with inline comments on a PR.

    Args:
        pr_number (int): The pull request number.
        summary (str): Overall review summary text.
        findings (list): List of Finding objects to
            post as inline comments.

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
