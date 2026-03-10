"""CLI entry point for AI code review."""

import argparse
import sys

from scripts.code_review.diff import get_pr_diff
from scripts.code_review.reviewer import run_review
from scripts.code_review.dismiss import dismiss_previous_reviews
from scripts.code_review.commenter import post_review

MAX_DIFF_CHARS = 100_000


def main():
    """Parse args and run the review pipeline.

    Returns:
        None: Always exits with code 0.

    Raises:
        SystemExit: On argument parsing errors.
    """
    parser = argparse.ArgumentParser(
        description="AI-powered PR code review",
    )
    parser.add_argument(
        "--pr-number", type=int, required=True,
    )
    parser.add_argument(
        "--base-ref", type=str, required=True,
    )
    args = parser.parse_args()

    diff = get_pr_diff(args.base_ref)
    if not diff.strip():
        print("No diff found, skipping review.")
        sys.exit(0)
    if len(diff) > MAX_DIFF_CHARS:
        diff = diff[:MAX_DIFF_CHARS]
        print("Diff truncated to 100K chars.")

    print("Running Claude review...")
    summary, findings = run_review(diff)
    print(f"Found {len(findings)} issue(s).")

    dismiss_previous_reviews(args.pr_number)
    post_review(args.pr_number, summary, findings)
    print("Review posted.")


if __name__ == "__main__":
    main()
