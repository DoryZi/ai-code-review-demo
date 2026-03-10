"""Dismiss stale bot reviews on a PR."""

import json
import os
import subprocess


def dismiss_previous_reviews(pr_number):
    """Dismiss old bot reviews to avoid clutter.

    Args:
        pr_number (int): The pull request number to
            dismiss reviews on.

    Returns:
        int: Count of reviews dismissed.

    Raises:
        subprocess.CalledProcessError: If the gh CLI
            command fails.
    """
    repo = os.environ.get("GITHUB_REPOSITORY", "")
    result = subprocess.run(
        [
            "gh", "api",
            f"repos/{repo}/pulls/{pr_number}/reviews",
        ],
        capture_output=True, text=True, check=True,
    )
    reviews = json.loads(result.stdout)
    dismissed = 0
    for review in reviews:
        user = review.get("user", {})
        login = user.get("login", "")
        if "bot" not in login:
            continue
        rid = review["id"]
        subprocess.run(
            [
                "gh", "api", "--method", "PUT",
                f"repos/{repo}/pulls/{pr_number}"
                f"/reviews/{rid}/dismissals",
                "-f", "message=Superseded by new review",
            ],
            capture_output=True, text=True, check=True,
        )
        dismissed += 1
    return dismissed
