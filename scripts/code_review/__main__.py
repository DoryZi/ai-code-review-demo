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

    print(f"[1/5] Getting diff against {args.base_ref}...")
    diff = get_pr_diff(args.base_ref)
    if not diff.strip():
        print("No diff found, skipping review.")
        sys.exit(0)
    print(f"[1/5] Diff size: {len(diff)} chars")
    print(f"[1/5] Diff preview:\n{diff[:500]}\n...")
    if len(diff) > MAX_DIFF_CHARS:
        diff = diff[:MAX_DIFF_CHARS]
        print("[1/5] Diff truncated to 100K chars.")

    print("[2/5] Sending diff to Claude for review...")
    summary, findings = run_review(diff)
    print(f"[2/5] Summary: {summary}")
    print(f"[2/5] Found {len(findings)} finding(s).")
    for f in findings:
        print(f"  - [{f.severity}/{f.category}] "
              f"{f.file}:{f.line} {f.comment[:80]}")

    print(f"[3/5] Dismissing old reviews on PR #{args.pr_number}...")
    count = dismiss_previous_reviews(args.pr_number)
    print(f"[3/5] Dismissed {count} old review(s).")

    print(f"[4/5] Posting review on PR #{args.pr_number}...")
    post_review(args.pr_number, summary, findings)
    print("[5/5] Done! Review posted.")


if __name__ == "__main__":
    main()
