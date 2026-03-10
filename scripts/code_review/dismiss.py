"""Clean up old bot reviews on a PR."""

import json
import os
import subprocess


def _get_head_sha():
    """Get current HEAD commit SHA.

    Returns:
        str: The 40-char commit SHA.
    """
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        capture_output=True, text=True, check=True,
    )
    return result.stdout.strip()


def _get_bot_reviews(repo, pr_number):
    """Fetch all bot reviews on a PR.

    Args:
        repo (str): The owner/repo string.
        pr_number (int): The pull request number.

    Returns:
        list: Review objects from the GitHub API.
    """
    result = subprocess.run(
        [
            "gh", "api",
            f"repos/{repo}/pulls/{pr_number}/reviews",
        ],
        capture_output=True, text=True, check=True,
    )
    reviews = json.loads(result.stdout)
    return [
        r for r in reviews
        if "bot" in r.get("user", {}).get("login", "")
    ]


def count_bot_reviews(pr_number):
    """Count existing bot reviews on a PR.

    Args:
        pr_number (int): The pull request number.

    Returns:
        int: Number of bot reviews found.
    """
    repo = os.environ.get("GITHUB_REPOSITORY", "")
    return len(_get_bot_reviews(repo, pr_number))


def already_reviewed(pr_number):
    """Check if this commit was already reviewed.

    Args:
        pr_number (int): The pull request number.

    Returns:
        bool: True if a bot review exists for HEAD.
    """
    repo = os.environ.get("GITHUB_REPOSITORY", "")
    sha = _get_head_sha()
    for r in _get_bot_reviews(repo, pr_number):
        if r.get("commit_id") == sha:
            return True
    return False


def delete_old_reviews(pr_number):
    """Delete old bot review comments on a PR.

    Args:
        pr_number (int): The pull request number.

    Returns:
        int: Count of review comments deleted.
    """
    repo = os.environ.get("GITHUB_REPOSITORY", "")
    result = subprocess.run(
        [
            "gh", "api",
            f"repos/{repo}/pulls/{pr_number}/comments",
        ],
        capture_output=True, text=True, check=True,
    )
    comments = json.loads(result.stdout)
    deleted = 0
    for c in comments:
        login = c.get("user", {}).get("login", "")
        if "bot" not in login:
            continue
        cid = c["id"]
        try:
            subprocess.run(
                [
                    "gh", "api", "--method", "DELETE",
                    f"repos/{repo}/pulls/comments/{cid}",
                ],
                capture_output=True, text=True,
                check=True,
            )
            deleted += 1
        except subprocess.CalledProcessError:
            print(f"  Could not delete comment {cid}")
    return deleted
