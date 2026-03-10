"""CLI entry point for AI code review."""

import argparse
import sys

from agent_tools.code_review.diff import get_pr_diff
from agent_tools.code_review.diff import get_latest_commit_diff
from agent_tools.code_review.reviewer import run_review
from agent_tools.code_review.dismiss import already_reviewed
from agent_tools.code_review.dismiss import count_bot_reviews
from agent_tools.code_review.commenter import post_review
from agent_tools.code_review.fix_doc import build_fix_doc

MAX_DIFF_CHARS = 100_000
MAX_FOLLOWUP_FINDINGS = 5


def main():
    """Parse args and run the review pipeline.

    First push gets a full review (up to 15 findings).
    Subsequent pushes review only the latest commit
    diff, capped at 5 findings. Skips if the current
    commit was already reviewed.

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

    print("[1/6] Checking for existing review...")
    if already_reviewed(args.pr_number):
        print("Already reviewed this commit, skipping.")
        sys.exit(0)

    is_first = count_bot_reviews(args.pr_number) == 0
    if is_first:
        print("[2/6] First review — full PR diff...")
        diff = get_pr_diff(args.base_ref)
    else:
        print("[2/6] Follow-up — latest commit diff...")
        diff = get_latest_commit_diff()

    if not diff.strip():
        print("No diff found, skipping review.")
        sys.exit(0)
    print(f"[2/6] Diff size: {len(diff)} chars")
    if len(diff) > MAX_DIFF_CHARS:
        diff = diff[:MAX_DIFF_CHARS]
        print("[2/6] Diff truncated to 100K chars.")

    print("[3/6] Sending diff to Claude for review...")
    summary, findings, cost = run_review(diff)
    if not is_first and len(findings) > MAX_FOLLOWUP_FINDINGS:
        print(f"[3/6] Capping to {MAX_FOLLOWUP_FINDINGS}")
        findings = findings[:MAX_FOLLOWUP_FINDINGS]
    print(f"[3/6] Summary: {summary[:200]}")
    print(f"[3/6] Found {len(findings)} finding(s).")
    print(f"[3/6] Cost: {cost}")
    for f in findings:
        print(f"  - [{f.severity}/{f.category}] "
              f"{f.file}:{f.line} {f.comment[:80]}")

    print("[4/6] Building fix guide...")
    fix_doc = build_fix_doc(summary, findings)

    print(f"[5/6] Posting review on PR #{args.pr_number}...")
    post_review(args.pr_number, summary, findings, fix_doc,
                cost=cost)
    print("[6/6] Done! Review posted.")


if __name__ == "__main__":
    main()
