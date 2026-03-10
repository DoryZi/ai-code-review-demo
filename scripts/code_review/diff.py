"""Retrieve PR diff from git."""

import subprocess

EXCLUDE_PATTERNS = (
    "*.lock", "*/migrations/*",
    "*.md", ".github/*",
)


def get_pr_diff(base_ref):
    """Get the git diff between base branch and HEAD.

    Args:
        base_ref (str): The base branch name to diff
            against, e.g. 'main' or 'dev'.

    Returns:
        str: The unified diff output as a string.

    Raises:
        subprocess.CalledProcessError: If git diff
            command fails.
    """
    cmd = [
        "git", "diff",
        f"origin/{base_ref}...HEAD", "--",
    ]
    for pat in EXCLUDE_PATTERNS:
        cmd.extend([":!{}".format(pat)])
    result = subprocess.run(
        cmd, capture_output=True, text=True, check=True,
    )
    return result.stdout


def get_latest_commit_diff():
    """Get diff of only the latest commit.

    Args:
        None.

    Returns:
        str: The unified diff of HEAD~1..HEAD.

    Raises:
        subprocess.CalledProcessError: If git diff
            command fails.
    """
    cmd = ["git", "diff", "HEAD~1..HEAD", "--"]
    for pat in EXCLUDE_PATTERNS:
        cmd.extend([":!{}".format(pat)])
    result = subprocess.run(
        cmd, capture_output=True, text=True, check=True,
    )
    return result.stdout
